import subprocess
import datetime
import sys
import os


if not os.path.exists("data") or not os.path.isdir("data"):
    print("gnuplot.py must be run in the root directory of the 'stats' project")
    sys.exit(1)

# sort the input data, in case dates are all over the place
with open("data/codeage.csv") as source:
    lines = sorted([line.strip() for line in source.readlines() if line.strip()])
    with open("data/codeage.csv", "w") as output:
        output.write("\n".join(lines))

with open("data/codeage.plot") as f:
    content = f.read()


current_year = datetime.datetime.now().year
start_year = 2019

print(f"Current year: ${current_year}")

if f'"≥ {current_year}"' not in content or True:
    start = content[:content.index("# START PLOT") + 13]
    end = content[content.index("# END PLOT"):]

    with open("data/codeage.plot", "w") as f:
        f.write(start)
        f.write("plot \\\n")
        for y in range(current_year, start_year - 1, -1):
            f.write(f" 'data/codeage.csv' using 1:{y - start_year + 2} axes x1y2 with filledcurves above title")
            f.write(f' "≥ {y}"')
            if y != start_year:
                f.write(", \\\n")
            else:
                f.write("\n")
        f.write(end)
    print("Updated codeage.plot")

output = subprocess.run(["gnuplot", "-p", "data/codeage.plot"], capture_output=True)
with open("data/codeage.svg", "w") as f:
    f.write(output.stdout.decode('utf-8').strip())
print("Updated codeage.svg")

