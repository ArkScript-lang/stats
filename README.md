# Stats

## Attributions

1. https://mastodon.social/@bagder/113399049389149090
2. https://github.com/kees/kernel-tools/blob/trunk/stats/year-annotate.py

## year-annotate.py

1. Only works with non-RC tags.
2. `codeage.plot` has to be updated every year to add a new line to the `plot` command


```shell
cd Ark/ && ../stats/year-annotate/year-annotate.py -d | tee ../stats/year-annotate/codeage.csv
cd ../stats/year-annotate/ && gnuplot -p codeage.plot > codeage.svg
```

