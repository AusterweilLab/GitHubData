import re, os, json, math, time
import requests
from lxml.html import fromstring
import asyncio
from itertools import cycle
import traceback
from os import listdir
from os.path import isfile, join
from aiohttp import ClientSession

# Parallelize the requests
# Use proxy IP requests
# About 44k files, each with 30k commits = 13M requests :)
# Github rate limiting = 5k per hour


# ------------- Load file, each newline is a json blob -------------

files = list(filter(lambda x: re.search('.json$', x), [f for f in listdir('urls') if isfile(join('urls', f))]))

for file in files:

    t0 = time.time()

    print("---------- FILE {} ----------".format(file))

    filepath = os.path.join('urls', file)

    with open(filepath, 'r+') as jfile:
        content = jfile.read()
        jsonblobs = content.split('\n')

    # Filter out any non-json blobs
    jsonblobs = list(filter(lambda x: x != '' and x != '}{', jsonblobs))

    # Only filter out the pull/push events
    pushjsonblobs = list(filter(lambda x: re.search('Push', json.loads(x)['type']), jsonblobs))
    #pulljsonblobs = list(filter(lambda x: re.search('Pull', json.loads(x)['type']), jsonblobs))
    # types: set(map(lambda x: json.loads(x)['type'], jsonblobs))


    # ------------- Save file in the same way -------------

    pushoutfile = re.sub('.json', '_push_results.json', file)
    #pulloutfile = re.sub('.json', '_pull_results.json', file)

    if not os.path.exists('scraped_data'):
        os.makedirs('scraped_data')

    pushoutfile = os.path.join('scraped_data', pushoutfile)
    pushoutf = open(pushoutfile, 'a+')
    #pulloutfile = os.path.join('scraped_data', pulloutfile)
    #pulloutf = open(pulloutfile, 'a+')


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


    # ------------- Get a list of IPs to use for proxying ---------------

    def get_proxies():

        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()

        for i in parser.xpath('//tbody/tr'):

            if i.xpath('.//td[7][contains(text(),"yes")]'):

                #Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)

        return proxies


    def find_proxy(proxy_pool):

        # Find a proxy ip that will work

        proxy_found = False
        print("Looking for proxy ip to bash to death...")

        while proxy_found == False:

            proxy = next(proxy_pool)

            try:
                requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=1)
                proxy_found = True
                print("Proxy found!")
                return proxy

            except:
                continue


    # ------------- Make parallel requests for each chunk of 5000 -------------

    n_urls = len(pushurls)
    n_requests = 100  # Let's keep smaller chunks
    n_chunks = math.ceil(n_urls/n_requests)

    for n in range(n_chunks):

        pushurls_chunk = pushurls[n_requests*n:n_requests*(n+1)]

        async def fetch(url, session, proxy):

            """Fetch a url, using specified ClientSession."""
            try:
                async with session.get(url, proxy='http://' + proxy, timeout=5) as response:
                    resp = await response.read()
                    jsonresult = json.loads(resp)

                    # Only save if it has files
                    if jsonresult.get('files'):
                        strresult = json.dumps(jsonresult) + '\n'
                        pushoutf.write(strresult)
                        return resp
                    else:
                        return None
            except:
                print("There was an error.")
                return None


        async def fetch_all(urls):

            """Launch requests for all web pages."""
            tasks = []

            async with ClientSession() as session:

                proxies = get_proxies()
                proxy_pool = cycle(proxies)
                proxy = find_proxy(proxy_pool)

                for url in urls:
                    task = asyncio.ensure_future(fetch(url, session, proxy))
                    tasks.append(task) # create list of tasks

                _ = await asyncio.gather(*tasks) # gather task responses

        loop = asyncio.get_event_loop() # event loop
        future = asyncio.ensure_future(fetch_all(pushurls_chunk)) # tasks to do
        loop.run_until_complete(future) # loop until done
        # pushoutf.close()

        # sleep one hour before continuing
        #time.sleep(3600)
        print("Finished chunk " + str(n))

    dt = time.time() - t0
    print(dt)


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