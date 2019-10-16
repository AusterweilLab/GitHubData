import re, os, json, math, time
import requests
from lxml.html import fromstring
import asyncio
from itertools import cycle
import random
from aiohttp import ClientSession

# Only take the most active repos
# Register an app to get the 5k requests per hour limit
# Parallelize the requests
# Run and monitor it running
# Maybe make several apps

# ------------- Load in all of the files, one at a time, and save the urls to a dict {reportname: [url]} ---------------
# ------------- Do this for both Push and Pull -------------------------------------------------------------------------

files = list(map(lambda x: x[0], list(map(lambda x: x[2], list(os.walk('urls'))))[1:]))



# ------------- Load file, each newline is a json blob -------------

files = list(map(lambda x: x[0], list(map(lambda x: x[2], list(os.walk('urls'))))[1:]))

for file in files:

    t0 = time.time()

    print("---------- FILE {} ----------".format(file))

    filepath = os.path.join('urls', file, file)

    with open(filepath, 'r+', encoding='utf-8') as jfile:
        content = jfile.read()
        jsonblobs = content.split('\n')

    # Filter out any non-json blobs
    jsonblobs = list(filter(lambda x: x != '' and x != '}{', jsonblobs))

    # Only filter out the pull/push events
    pushjsonblobs = list(filter(lambda x: re.search('Push', json.loads(x)['type']), jsonblobs))
    pulljsonblobs = list(filter(lambda x: re.search('Pull', json.loads(x)['type']), jsonblobs))
    # types: set(map(lambda x: json.loads(x)['type'], jsonblobs))


    # ------------- Save file in the same way -------------

    #pushoutfile = re.sub('.json', '_push_results.json', file)
    pulloutfile = re.sub('.json', '_pull_urls.json', file)

    if not os.path.exists('scraped_data'):
        os.makedirs('scraped_data')

    #pushoutfile = os.path.join('scraped_data', pushoutfile)
    #pushoutf = open(pushoutfile, 'a+')  # This way if the script quits, then it can continue where it left off
    pulloutfile = os.path.join('scraped_data', pulloutfile)
    pulloutf = open(pulloutfile, 'a+')


    # ------------- PULL: Need to go to URLs to get a second url -------------

    pullurls = []

    for i, blob in enumerate(pulljsonblobs):

        blob = json.loads(blob)
        url = blob['payload']['pull_request']['commits_url']
        pullurls.append(url)


    '''
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

    '''
    # ------------- Get a list of IPs to use for proxying ---------------

    def get_proxies():

        #url = 'https://free-proxy-list.net/'
        url = 'https://www.sslproxies.org/'
        # url = 'https://www.socks-proxy.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()

        for i in parser.xpath('//tbody/tr'):

            if i.xpath('.//td[7][contains(text(),"yes")]'):

                #Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)

        return proxies


    def find_proxy(proxies, url):

        # Find a proxy ip that will work

        proxy_found = False
        print("Looking for proxy ip to bash to death...")
        max_ips = len(proxies)
        proxy_pool = cycle(proxies)

        tries = 1

        while proxy_found == False and tries != max_ips:

            proxy = next(proxy_pool)

            try:
                requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=1)
                proxy_found = True
                print("Proxy found!")
                return proxy

            except:
                tries += 1
                continue

        else:
            print("Proxy not found :(")
            return None


    # ------------- Make parallel requests for each url, each url needs to find a proxy -------------

    async def fetch(url, session):

        """Fetch a url, using specified ClientSession."""

        proxy_success = False

        while proxy_success == False:

            proxies = get_proxies()
            random.shuffle(list(proxies))
            proxy = find_proxy(proxies, url)

            if not proxy:
                return None

            try:
                async with session.get(url, proxy='http://' + proxy, timeout=5) as response:
                    resp = await response.read()
                    jsonresult = json.loads(resp)

                    # PULL
                    # Skip if there are no commits
                    if jsonresult == []:
                        return None

                    # Loop through the commits and get the files
                    for commit in jsonresult:
                        url = commit['url']
                        strresult = json.dumps(url) + '\n'
                        pulloutf.write(strresult)

                    '''
                    # PUSH
                    # Only save if it has files
                    if jsonresult.get('files'):
                        strresult = json.dumps(jsonresult) + '\n'
                        pushoutf.write(strresult)
                        return resp
                    else:
                        return None
                    '''

            except:
                continue

            if not proxy:
                return None


    async def fetch_all(urls):

        """Launch requests for all web pages."""
        tasks = []

        async with ClientSession() as session:

            for url in urls:
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task) # create list of tasks

            _ = await asyncio.gather(*tasks) # gather task responses

    loop = asyncio.get_event_loop() # event loop
    future = asyncio.ensure_future(fetch_all(pullurls)) # tasks to do
    loop.run_until_complete(future) # loop until done
    # pushoutf.close()

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