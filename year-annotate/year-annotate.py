#!/usr/bin/env python3
# Author: Kees Cook <kees@kernel.org>
# License: MIT
# Reworked from the original Perl implementation:
# https://github.com/curl/stats/blob/master/codeage.pl
#
# Extract per-line commit dates for each git tag for graphing code ages.
# Inspired by:
# https://fosstodon.org/@bagder@mastodon.social/113399049650160188
# https://github.com/curl/stats/blob/master/codeage.pl
# https://github.com/curl/stats/blob/master/codeage.plot
#
# cd ~/src/linux && year-annotate.py -d | tee codeage.csv
import sys, os
import pickle
import optparse
import datetime
from subprocess import *
from itertools import repeat
from multiprocessing import Pool, cpu_count, set_start_method
import tqdm
from packaging.version import Version
from pathlib import Path

# Globals (FIXME: turn this into a proper object)
parser = optparse.OptionParser()
parser.add_option("-d", "--debug", help="Report additional debugging while processing USNs", action='store_true')
parser.add_option("-C", "--csv", help="Report as CSV file", action='store_true')
(opt, args) = parser.parse_args()

devnull = open("/dev/null", "w")

cache_dir = os.path.expanduser("~/.cache/codeage")
Path(cache_dir).mkdir(parents=True, exist_ok=True)

def save_cache(cache, tag):
    cachefile = "%s/%s.pickle" % (cache_dir, tag)
    if opt.debug:
        print("Saving cache %s ..." % (cachefile), file=sys.stderr)
    pickle.dump(cache, open(cachefile, 'wb'), -1)

def load_cache(tag):
    cachefile = "%s/%s.pickle" % (cache_dir, tag)
    if os.path.exists(cachefile):
        if opt.debug:
            print("Loading cache %s ..." % (cachefile), file=sys.stderr)
        cache = pickle.load(open(cachefile, 'rb'))
    else:
        cache = dict()
        cache.setdefault('annotated', dict())
        cache.setdefault('ages', dict())
    return cache

def run(cmd):
    #if opt.debug:
    #    print(cmd, file=sys.stderr)
    return Popen(cmd, stdout=PIPE, stderr=devnull).communicate()[0].decode("utf-8", "ignore")

def sha_to_date(sha):
    output = run(["git", "show", "--pretty=%at", "-s", "%s^{commit}" % (sha)])
    epoch = output.strip()
    date = datetime.datetime.fromtimestamp(float(epoch))
    return date

def annotate(tag, file):
    epochs = dict()
    ann = run(['git', 'annotate', '-t', '--line-porcelain', file, tag]).splitlines()
    for line in ann:
        if line.startswith('committer-time '):
            epoch = int(line.split(' ', 1)[1])
            epochs.setdefault(epoch, 0)
            epochs[epoch] += 1
    return {file: epochs}

def frombefore(before, epochs):
    count = 0
    for file in epochs:
        for epoch in epochs[file]:
            if epoch < before:
                count += epochs[file][epoch]
    return count

def process(tag, years):
    cache = load_cache(tag)

    date = sha_to_date(tag)
    epochs = cache['annotated']
    if len(epochs) == 0:
        if opt.debug:
            print(date.strftime('Processing files at %%s (%Y-%m-%d) ...') % (tag), file=sys.stderr)
        # Do we want to exclude Documentation, samples, or tools subdirectories?
        # Or MAINTAINERS, dot files, etc?
        files = run(['git', 'ls-tree', '-r', '--name-only', tag]).splitlines()
        count = len(files)

        with Pool(cpu_count()) as p:
            results = p.starmap(annotate,
                                tqdm.tqdm(zip(repeat(tag), files), total=count))
            # starmap produces a list of outputs from the function.
            for result in results:
                epochs |= result

        cache['annotated'] = epochs
        # Save this tag's epochs!
        save_cache(cache, tag)

    report = cache['ages']
    if len(report) == 0:
        day = date.strftime('%Y-%m-%d')
        report = day
        if opt.debug:
            print('Scanning ages ...                  ', file=sys.stderr)
        for year in years:
            report += ';%u' % (frombefore(year, epochs))
        # Save age span report
        cache['ages'] = report
        save_cache(cache, tag)
    print(report)

if __name__ == "__main__":
    set_start_method('spawn')

    # Get the list of tags we're going to operate against
    output = run(["git", "tag", "--sort=authordate"])
    # ignoring 3.2.0 tag that seems to have been tagged out of nowhere when calling
    # git tag --sort=authordate, it is the first one (even though git show v3.2.0
    # says it was on a commit in 2022)
    tags = [x
            for x in output.strip().splitlines()
            if x.startswith('v') and
                '3.2.0' not in x
            #   '-' not in x and
            #   '_' not in x
           ] + ['HEAD']
    # tags.sort(key=Version)
    if opt.debug:
        print(tags, file=sys.stderr)

    # Find the year bounds of our tags
    year_first = sha_to_date(tags[0]).year + 1
    year_last  = sha_to_date(tags[-1]).year + 1
    if opt.debug:
        print("%d .. %d" % (year_first, year_last), file=sys.stderr)
    years = [int(datetime.datetime.strptime('%d' % (year), '%Y').strftime("%s")) for year in range(year_first, year_last + 1, 1)]
    if opt.debug:
        print(years, file=sys.stderr)

    # Walk tags
    for tag in tags:
        process(tag, years)

