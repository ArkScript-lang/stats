# Stats

## Attributions

1. https://mastodon.social/@bagder/113399049389149090
2. https://github.com/kees/kernel-tools/blob/trunk/stats/year-annotate.py

## year-annotate.py

This script is run once every week by the CI and generates [codeage.svg](https://raw.githubusercontent.com/ArkScript-lang/stats/refs/heads/master/year-annotate/codeage.svg).

1. Works with any kind of tags, sort them by `authordate`
2. `codeage.plot` is updated by `gnuplot.py` to add every new year that's not in it

```shell
cd Ark/ && ../stats/year-annotate/year-annotate.py -d | tee ../stats/year-annotate/codeage.csv
cd ../stats/year-annotate/ && python3 gnuplot.py
```

## user-count

This script is run once every day by the CI and generates [users.json](https://raw.githubusercontent.com/ArkScript-lang/stats/refs/heads/master/users.json).

1. Requires a `GITHUB_TOKEN` to query the web API (the code search API requires the user to be authentified)

```shell
python3 user-count/arkscript-usage.py
```

