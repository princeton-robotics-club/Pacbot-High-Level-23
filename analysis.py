import sys

if len(sys.argv) < 2:
    raise ValueError("File name required")
total_time = 0
n = 0
largest_time = float("-inf")
lowest_time = float("inf")
with open(sys.argv[1], "r") as f:
    for line in f:
        if "CALC TIME: " in line:
            time = float(line[11:])
            total_time += time
            n += 1
            largest_time = max(time, largest_time)
            lowest_time = min(time, lowest_time)

print(f"Num Calcs: {n}")
print(f"Average Time: {total_time / n}")
print(f"Largest Time: {largest_time}")
