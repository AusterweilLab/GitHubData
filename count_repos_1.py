import csv, os, re
import gzip, json
import paramiko

urlfile = 'urlfile2'

hostname = "vader.psych.wisc.edu"
username = "alyssa"
password = "Alyssa"
port = 1202

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.WarningPolicy)
client.connect(hostname, port=port, username=username, password=password)

stdin, stdout, stderr = client.exec_command("cd 2015; ls")
filelist = stdout.read().splitlines()
filelist = list(map(lambda x: x.decode("utf-8"), filelist))

sftp = client.open_sftp()

remote_images_path = '2015/'
local_path = '/Temp/'


for file in filelist:

    urls = {}

    file_remote = remote_images_path + file
    file_local = local_path + file

    print(file_remote + '>>>' + file_local)

    sftp.get(file_remote, file_local)

    with gzip.open(file_local, 'rb') as gfile:

        data = gfile.read()
        data = data.decode("utf-8")
        rows = data.split('\n')

        jrows = []
        for row in rows:
            try:
                jrows.append(json.loads(row))
            except:
                continue

        jsonblobs = list(filter(lambda x: re.search('Push', x['type']) or re.search('Pull', x['type']), jrows))

        for blob in jsonblobs:

            repo = blob['repo']['id']
            if re.search('Push', blob['type']):
                type = 'push'
            else:
                type = 'pull'


            if type == 'push':

                commits = blob['payload']['commits']

                # Skip if there are no commits
                if commits == []:
                    continue

                # Loop through the commits and get the files
                for commit in commits:
                    url = commit['url']
                    if urls.get(repo):
                        urls[repo].append((url, type))
                    else:
                        urls[repo] = [(url, type)]


            if type == 'pull':

                url = blob['payload']['pull_request']['commits_url']

                if urls.get(repo):
                    urls[repo].append((url, type))
                else:
                    urls[repo] = [(url, type)]


    os.remove(file_local)

    with open(urlfile, 'a+') as fp:
        fp.write(str(urls))


sftp.close()
client.close()