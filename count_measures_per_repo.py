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

if not os.path.exists('final_pickles'):
    os.makedirs('final_pickles')

with open('final_pickles/measures', 'wb') as filehandle:
    pickle.dump(measures, filehandle)