import re, os, json, math, time
import pickle
import requests

# Github rate limiting = 5k per hour

with open('wanted_repos.data', 'rb') as filehandle:
    # read the data as binary data stream
    wanted_repos = pickle.load(filehandle)

with open('repos_all.data', 'rb') as filehandle:
    # read the data as binary data stream
    repos_all = pickle.load(filehandle)

wanted_urls = {int(your_key): repos_all[int(your_key)] for your_key in wanted_repos}

# ------------- Save file in the same way -------------

pushoutfile = "push_json_files.json"
pulloutfile = "pull_json_files.json"

if not os.path.exists('scraped_data'):
    os.makedirs('scraped_data')

pushoutfile = os.path.join('scraped_data', pushoutfile)
pushoutf = open(pushoutfile, 'a+')  # This way if the script quits, then it can continue where it left off
pulloutfile = os.path.join('scraped_data', pulloutfile)
pulloutf = open(pulloutfile, 'a+')


for repo in wanted_repos:

    print("---------- Repo {} ----------".format(repo))

    all_urls = wanted_urls[int(repo)]

    for u in all_urls:

        url = u[0] + '?client_id=befb2692dfc5374d6dc8&client_secret=03ae2df64c664d427ac43ed7936862327fd5b583'

        r = requests.get(url)
        jsonresult = json.loads(r.text)

        # If push then just get what it returns

        if u[1] == 'push':

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

            # Skip if it doesn't have any file information
            if jsonresult.get('files'):
                strresult = json.dumps(jsonresult) + '\n'
                pushoutf.write(strresult)
                print(".")

        if u[1] == 'pull':

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
                    print(".")
