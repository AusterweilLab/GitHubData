import pickle
import os


picklejar = 'wanted_measures'
files = os.listdir(picklejar)

measures = {}

for file in files:
    with open(os.path.join(picklejar, file), 'rb') as filehandle:
        ms = pickle.load(filehandle)
        for m in ms:
            repo = m['repo']['name'].split('/')[-1]
            type = m['type']

            if measures.get(repo):
                measures[repo].append(type)
            else:
                measures[repo] = [type]

with open('measures', 'wb') as filehandle:
    pickle.dump(measures, filehandle)