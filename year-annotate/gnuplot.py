import subprocess
import datetime


with open("codeage.plot") as f:
    content = f.read()


current_year = datetime.datetime.now().year
start_year = 2019

if f'"≥ {current_year}"' not in content or True:
    start = content[:content.index("# START PLOT") + 13]
    end = content[content.index("# END PLOT"):]

    with open("codeage.plot", "w") as f:
        f.write(start)
        f.write("plot \\\n")
        for y in range(current_year, start_year - 1, -1):
            f.write(f" 'codeage.csv' using 1:{y - start_year + 2} axes x1y2 with filledcurves above title")
            f.write(f' "≥ {y}"')
            if y != 2019:
                f.write(", \\\n")
            else:
                f.write("\n")
        f.write(end)

output = subprocess.run(["gnuplot", "-p", "codeage.plot"], capture_output=True)
with open("codeage.svg", "w") as f:
    f.write(output.stdout.decode('utf-8').strip())

