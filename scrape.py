import re, os, json
import requests


# Public and release events can be done later
# And delete

# ------------- Load file, each newline is a json blob -------------

filename = '2017-12-31-23.json'
filepath = os.path.join('urls', filename)

with open(filepath, 'r+') as jfile:
    content = jfile.read()
    jsonblobs = content.split('\n')

# Filter out any non-json blobs
jsonblobs = filter(lambda x: x != '' and x != '}{', jsonblobs)

# Only filter out the pull/push events
pushjsonblobs = filter(lambda x: re.search('Push', json.loads(x)['type']), jsonblobs)
pulljsonblobs = filter(lambda x: re.search('Pull', json.loads(x)['type']), jsonblobs)
# types: set(map(lambda x: json.loads(x)['type'], jsonblobs))


# ------------- Save file in the same way to save memory -------------

pushoutfile = re.sub('.json', '_push_results.json', filename)
pulloutfile = re.sub('.json', '_pull_results.json', filename)

if not os.path.exists('scraped_data'):
    os.makedirs('scraped_data')

pushoutfile = os.path.join('scraped_data', pushoutfile)
pushoutf = open(pushoutfile, 'a+')
pulloutfile = os.path.join('scraped_data', pulloutfile)
pulloutf = open(pulloutfile, 'a+')


# ------------- Push events can have many commits, loop through them -------------

for i, blob in enumerate(pushjsonblobs):

    blob = json.loads(blob)
    commits = blob['payload']['commits']

    # Skip if there are no commits
    if commits == []:
        continue

    # Loop through the commits and get the files
    for commit in commits:
        url = commit['url']
        r = requests.get(url)
        jsonresult = r.json()
        strresult = json.dumps(jsonresult) + '\n'
        pushoutf.write(strresult)

    print i

pushoutf.close()


# ------------- Pull events are multiple commits, with multiple files in each commit -------------

for i, blob in enumerate(pulljsonblobs):

    blob = json.loads(blob)
    url = blob['payload']['pull_request']['commits_url']
    r = requests.get(url)
    commit_urls = r.json()

    # Skip if there are no commits
    if commit_urls == []:
        continue

    # Loop through the commits and get the files
    for commit in commit_urls:
        url = commit['url']
        r = requests.get(url)
        jsonresult = r.json()
        strresult = json.dumps(jsonresult) + '\n'
        pushoutf.write(strresult)

    print i

pulloutf.close()




