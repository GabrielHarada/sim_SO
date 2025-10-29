# this is an experimental workspace. Not part of the main program. Should be deleted soon

import matplotlib.pyplot as plt

t1name = "t1"
t1color = "#5f5c9e"
t1start = 0
t1duration = 2

t2name = "t2"
t2color = "#5f5c9e"
t2start = 5
t2duration = 5

# Split point: 3 units after t2 starts
split_time = t2start + 3

fig, ax = plt.subplots()

# Draw t1 with border
ax.barh(t1name, t1duration, left=t1start, color=t1color, edgecolor="black")

# Draw t2 in two segments (both with border)
ax.barh(t2name, 3, left=t2start, color=t2color, edgecolor="black")     # first colored part
ax.barh(t2name, 2, left=split_time, color="white", edgecolor="black")  # white (inactive) part

ax.set_xlabel("Time")
ax.set_xlim(0, 12)
ax.set_title("Gantt Chart Example")

plt.show()

