import re, os, json, math, time
#import requests
import asyncio
from aiohttp import ClientSession

# Parallelize the requests
# About 44k files, each with 30k commits = 13M requests :)

# Github rate limiting = 5k per hour

# >>>>>> Just do one file at a time for now, until parallelization is stable

# ------------- Load file, each newline is a json blob -------------

filename = '2017-12-31-23.json'
filepath = os.path.join('urls', filename)

with open(filepath, 'r+') as jfile:
    content = jfile.read()
    jsonblobs = content.split('\n')

# Filter out any non-json blobs
jsonblobs = list(filter(lambda x: x != '' and x != '}{', jsonblobs))

# Only filter out the pull/push events
pushjsonblobs = list(filter(lambda x: re.search('Push', json.loads(x)['type']), jsonblobs))
pulljsonblobs = list(filter(lambda x: re.search('Pull', json.loads(x)['type']), jsonblobs))
# types: set(map(lambda x: json.loads(x)['type'], jsonblobs))


# ------------- Save file in the same way -------------

pushoutfile = re.sub('.json', '_push_results.json', filename)
pulloutfile = re.sub('.json', '_pull_results.json', filename)

if not os.path.exists('scraped_data'):
    os.makedirs('scraped_data')

pushoutfile = os.path.join('scraped_data', pushoutfile)
pushoutf = open(pushoutfile, 'a+')
pulloutfile = os.path.join('scraped_data', pulloutfile)
pulloutf = open(pulloutfile, 'a+')


# ------------- PUSH: Extract a list of urls to use -------------

pushurls = []

# Push
for i, blob in enumerate(pushjsonblobs):

    blob = json.loads(blob)
    commits = blob['payload']['commits']

    # Skip if there are no commits
    if commits == []:
        continue

    # Loop through the commits and get the files
    for commit in commits:
        url = commit['url']
        pushurls.append(url)


# ------------- Make parallel requests for each chunk of 5000 -------------

n_urls = len(pushurls)
n_chunks = math.ceil(n_urls/5000)

for n in range(n_chunks):

    pushurls_chunk = pushurls[5000*n:5000*(n+1)]

    async def fetch(url, session):

        """Fetch a url, using specified ClientSession."""
        async with session.get(url) as response:
            resp = await response.read()
            jsonresult = json.loads(resp)

            if jsonresult.get('message'):
                if re.search('API rate limit exceeded', jsonresult.get('message')):
                    print("API rate limit exceeded :(")

            # Only save if it has files
            if jsonresult.get('files'):
                strresult = json.dumps(jsonresult) + '\n'
                pushoutf.write(strresult)
                return resp

            else: return None

    async def fetch_all(urls):

        """Launch requests for all web pages."""
        tasks = []
        fetch.start_time = dict() # dictionary of start times for each url

        async with ClientSession() as session:

            for url in urls:
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task) # create list of tasks

            _ = await asyncio.gather(*tasks) # gather task responses

    loop = asyncio.get_event_loop() # event loop
    future = asyncio.ensure_future(fetch_all(pushurls_chunk)) # tasks to do
    loop.run_until_complete(future) # loop until done
    pushoutf.close()

    # sleep one hour before continuing
    time.sleep(3600)
    print(n)


"""
# ------------- Pull events are multiple commits, with multiple files in each commit -------------

# Pull
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
        pullurls.append(url)

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

    print(i)

pulloutf.close()




"""