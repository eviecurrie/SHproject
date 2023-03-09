import matplotlib.pyplot as plt
import numpy as np
import csv
from pandas import *

seeds = [0, 42, 64, 123, 256, 301, 598, 647, 999, 1011]
allSeedsAllRuns = []

for i in range(0, len(seeds)):
    allRunsForSeed = []
    for j in range(0, 10):
        data = read_csv("./seeds/seed_" + str(seeds[i]) + "_" + str(j))

        valid_acc = data["valid_acc"].tolist()
        allRunsForSeed.extend(valid_acc)

    allSeedsAllRuns.append(allRunsForSeed)

fig = plt.figure()
ax = plt.axes()
bp = ax.boxplot(allSeedsAllRuns)
plt.show()


