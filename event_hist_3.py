import csv
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

wanted_repos = []

with open("repos_count.csv", 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 0:
            continue
        if int(row[1]) > 24:
            wanted_repos.append(row[0])

with open('wanted_repos.data', 'wb') as filehandle:
    # store the data as binary data stream
    pickle.dump(wanted_repos, filehandle)


# Make plot for histogram
"""
repos = []
events = []

with open("repos_count.csv", 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 0:
            continue
        repos.append(row[0])
        events.append(row[1])

ax = sns.distplot(np.array(events).astype(np.float), kde=False, rug=True)
ax.set_yscale('log')
ax.set(xlabel='N Events in 2015', ylabel='log(N Repositories with N Events)')
plt.show()
"""