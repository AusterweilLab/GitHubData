import pickle
import json
import re, os


def make_base_action_df():

    '''
    Make a df with columns
    Just push and pull for now
    repo, user, action, t, community
    community needs to be a connected component id, get from networks
    '''

    df_dict = {}

    files = ['pull_json_files', 'push_json_files']

    for file in files:

        with open('scraped_data/' + file + '.json', 'r') as pull_file:

            for i, line in enumerate(pull_file):

                info = json.loads(line)

                repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
                repo = repo_url.split('/')[-1]
                user = info['commit']['author']['email']
                time = info['commit']['author']['date']

                if file == 'pull_json_files':
                    action = 'pull'
                else:
                    action = 'push'

                df_dict[i] = {
                    'repo': repo,
                    'user': user,
                    'action': action,
                    'time': time
                }

    # save to pickle file, need to fill in the community column next
    with open('scratch_pickles', 'wb') as outfile:
        pickle.dump(df_dict, outfile)
        outfile.close()


make_base_action_df()
