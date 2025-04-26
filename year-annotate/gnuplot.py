import subprocess
import datetime
import sys
import os


if not os.path.exists("data") or not os.path.isdir("data"):
    print("gnuplot.py must be run in the root directory of the 'stats' project")
    sys.exit(1)


with open("data/codeage.plot") as f:
    content = f.read()


current_year = datetime.datetime.now().year
start_year = 2019

if f'"≥ {current_year}"' not in content or True:
    start = content[:content.index("# START PLOT") + 13]
    end = content[content.index("# END PLOT"):]

    with open("data/codeage.plot", "w") as f:
        f.write(start)
        f.write("plot \\\n")
        for y in range(current_year, start_year - 1, -1):
            f.write(f" 'codeage.csv' using 1:{y - start_year + 2} axes x1y2 with filledcurves above title")
            f.write(f' "≥ {y}"')
            if y != start_year:
                f.write(", \\\n")
            else:
                f.write("\n")
        f.write(end)

output = subprocess.run(["gnuplot", "-p", "data/codeage.plot"], capture_output=True)
with open("data/codeage.svg", "w") as f:
    f.write(output.stdout.decode('utf-8').strip())

