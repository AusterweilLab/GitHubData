import csv
import pickle

repos_dict = {}

with open('urlfile', 'r+') as file:
    data = file.read()
    repos = data.split("}{")[:100]
    stop = len(repos)
    for i, repo in enumerate(repos):
        if i == 0:
            repo = eval(repo + '}')
            repos_dict.update(repo)
        elif i == stop-1:
            try:
                repo = eval('{' + repo)
            except:
                repo = eval('{' + repo + '}')
            repos_dict.update(repo)
        else:
            repo = eval('{' + repo + '}')
            repos_dict.update(repo)

file.close()

data = 0
repos = 0

with open('urlfile2', 'r+') as file:
    data = file.read()
    repos = data.split("}{")[:100]
    stop = len(repos)
    for i, repo in enumerate(repos):
        if i == 0:
            repo = eval(repo + '}')
            repos_dict.update(repo)
        elif i == stop-1:
            try:
                repo = eval('{' + repo)
            except:
                repo = eval('{' + repo + '}')
            repos_dict.update(repo)
        else:
            repo = eval('{' + repo + '}')
            repos_dict.update(repo)

file.close()

# All the repo urls
with open('repos_all.data', 'wb') as filehandle:
    # store the data as binary data stream
    pickle.dump(repos_dict, filehandle)

repos_all = repos_dict.keys()
repos_all = list(map(lambda x: (x, len(repos_dict[x])), repos_dict.keys()))

with open('repos_count.csv', 'w') as file:
    writer = csv.writer(file)
    for row in repos_all:
        writer.writerow(row)
