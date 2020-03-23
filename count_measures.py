import os, re
import gzip, json
import paramiko
import pickle


# Wanted measures stuff
with open('final_pickles/wanted_repos.data', 'rb') as filehandle:
    # read the data as binary data stream
    wanted_repos = pickle.load(filehandle)

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

        # "measures of success"
        jsonblobs = list(filter(lambda x: re.search('Fork', x['type']) or re.search('Watch', x['type']) or re.search('Issue', x['type']), jrows))
        wanted_json = list(filter(lambda x: x['repo']['id'] in map(int, wanted_repos), jsonblobs))

    os.remove(file_local)

    if not os.path.exists('wanted_measures'):
        os.makedirs('wanted_measures')

    with open('wanted_measures/wanted_measures' + file + '.data', 'wb') as filehandle:
        pickle.dump(wanted_json, filehandle)

sftp.close()
client.close()