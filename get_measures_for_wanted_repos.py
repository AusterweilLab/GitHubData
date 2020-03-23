import os, re
import gzip, json
import paramiko
import pickle

# Need to load the pickle that has the ids of the wanted repos, so we can filter out the ones we aren't including
with open('wanted_repos.data', 'rb') as filehandle:
    # read the data as binary data stream
    wanted_repos = pickle.load(filehandle)

# Conenct to the server
hostname = "vader.psych.wisc.edu"
username = "alyssa"
password = "Alyssa"
port = 1202

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.WarningPolicy)
client.connect(hostname, port=port, username=username, password=password)

# Get a list of all the files
stdin, stdout, stderr = client.exec_command("cd 2015; ls")
filelist = stdout.read().splitlines()
filelist = list(map(lambda x: x.decode("utf-8"), filelist))

sftp = client.open_sftp()

remote_images_path = '2015/'
local_path = '/Temp/'

# Going to temp download one file at a time (delete after) and then load in the data
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

        # "measures of success"
        jsonblobs = list(filter(lambda x: re.search('Fork', x['type']) or re.search('Watch', x['type']) or re.search('Issue', x['type']), jrows))
        wanted_json = list(filter(lambda x: x['repo']['id'] in map(int, wanted_repos), jsonblobs))

    os.remove(file_local)

    # On pickle per file so we can load all the pickles in a different script (so we don't run out of memory)
    with open('wanted_measures/wanted_measures' + file + '.data', 'wb') as filehandle:
        pickle.dump(wanted_json, filehandle)

sftp.close()
client.close()