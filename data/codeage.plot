# Author: Daniel Stenberg
# License: MIT
# Tweaked by: Kees Cook <kees@kernel.org>
#
# Inspired by the stat posting:
# https://fosstodon.org/@bagder@mastodon.social/113399049650160188
# https://github.com/curl/stats/blob/master/codeage.pl
# https://github.com/curl/stats/blob/master/codeage.plot

# SVG output
set terminal svg size 1920,1080 dynamic font ",24"

# title
set title "ArkScript source code age\n{/*0.5Lines of code written per year}" font ",48"
# where's the legend
set key left top font ",22"

# Identify the axes
set y2label "Lines of code (including blanks, comments, docs, and tools)"
set format y2 "%.0s%c"

set grid y2tics
unset border

# time formated using this format
set timefmt "%Y-%m-%d"
set xdata time

set y2range [0:]
# TODO: make this range dynamic
set xrange ["2019-04-19":]

set xtics rotate 3600*24*365.25 nomirror out
unset mxtics
set y2tics mirror out
unset ytics

# set the format of the dates on the x axis
set format x "%Y"
set datafile separator ";"
# START PLOT
plot \
 'codeage.csv' using 1:8 axes x1y2 with filledcurves above title "≥ 2025", \
 'codeage.csv' using 1:7 axes x1y2 with filledcurves above title "≥ 2024", \
 'codeage.csv' using 1:6 axes x1y2 with filledcurves above title "≥ 2023", \
 'codeage.csv' using 1:5 axes x1y2 with filledcurves above title "≥ 2022", \
 'codeage.csv' using 1:4 axes x1y2 with filledcurves above title "≥ 2021", \
 'codeage.csv' using 1:3 axes x1y2 with filledcurves above title "≥ 2020", \
 'codeage.csv' using 1:2 axes x1y2 with filledcurves above title "≥ 2019"
# END PLOT
