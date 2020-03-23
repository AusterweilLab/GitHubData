import re, os, json, time
import requests


# XXXXXXXXXXXXXX DEPRICATED XXXXXXXXXXXXXXXXXXXXXX



# Github rate limiting = 5k per hour

#time.sleep(3600)

# ------------- Load file, each newline is a json blob -------------

files = list(map(lambda x: x[0], list(map(lambda x: x[2], list(os.walk('urls'))))[1:]))

for file in files[106:]:

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

    # pushoutfile = re.sub('.json', '_push_results.json', file)
    pulloutfile = re.sub('.json', '_pull_urls.json', file)

    if not os.path.exists('scraped_data'):
        os.makedirs('scraped_data')

    # pushoutfile = os.path.join('scraped_data', pushoutfile)
    # pushoutf = open(pushoutfile, 'a+')  # This way if the script quits, then it can continue where it left off
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

    for url in pullurls:

        url = url + '?client_id=befb2692dfc5374d6dc8&client_secret=03ae2df64c664d427ac43ed7936862327fd5b583'

        r = requests.get(url)
        jsonresult = json.loads(r.text)

        # PULL
        # Skip if there are no commits
        if jsonresult == []:
            continue

        if isinstance(jsonresult, dict):
            if jsonresult.get('message'):
                if re.search('NOT FOUND', jsonresult.get('message').upper()):
                    continue
                elif re.search('RATE LIMIT EXCEEDED', jsonresult.get('message').upper()):
                    print('Hit rate limit! Waiting...')
                    time.sleep(3605)
                    continue
                else:
                    print('Other error')
                    continue

        # Loop through the commits and get the files
        for commit in jsonresult:
            url2 = commit.get('url')
            url2 = url2 + '?client_id=befb2692dfc5374d6dc8&client_secret=03ae2df64c664d427ac43ed7936862327fd5b583'
            r2 = requests.get(url2)
            jsonresult2 = json.loads(r2.text)

            # Skip if it doesn't have any file information
            if jsonresult2.get('files'):
                strresult = json.dumps(jsonresult2) + '\n'
                pulloutf.write(strresult)
                print("Found data!")

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