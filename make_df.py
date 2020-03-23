import pickle
import json
import re, os
import networkx as nx
import pandas as pd


def make_base_action_df():

    '''
    Make a df with columns
    Just push and pull for now
    repo, user, action, t, community
    community needs to be a connected component id, get from networks
    '''

    df_rows = []

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

                df_rows.append({
                    'repo': repo,
                    'user': user,
                    'action': action,
                    'time': time
                })

    # save to pickle file, need to fill in the community column next
    if not os.path.exists('scratch_pickles'):
        os.makedirs('scratch_pickles')
    with open('scratch_pickles/df_rows', 'wb') as outfile:
        pickle.dump(df_rows, outfile)
        outfile.close()


# make this base dict that will be the df for later
#make_base_action_df()


# now need to calculate the community id numbers based on the networks I already made
# Nodes are users
# Edges are a repo they worked on together

def get_community_ids():

    # load network2
    with open('network_pickles/network2', 'rb') as filehandle:
        network2 = pickle.load(filehandle)

    # this is a list of sets
    comps = list(nx.connected_components(network2))

    # for each user, what is the comp id?
    users = list(set([item for sublist in comps for item in sublist]))
    user_ids = {}
    for user in users:
        for i, comp in enumerate(comps):
            if user in comp:
                user_ids[user] = i


    # for each row, fill in the last value

    # load df rows
    with open('scratch_pickles/df_rows', 'rb') as filehandle:
        df_rows = pickle.load(filehandle)

    # make new list of rows
    df_rows_all = []
    for row in df_rows:
        community = user_ids[row['user']]
        row['community'] = community
        df_rows_all.append(row)

    # turn into a df
    df = pd.DataFrame(df_rows_all)

    # save df to pickle
    if not os.path.exists('final_pickles'):
        os.makedirs('final_pickles')
    with open('final_pickles/df_actions.pkl', 'wb') as outfile:
        pickle.dump(df, outfile)
        outfile.close()

    # save network communities to pickle
    with open('final_pickles/components.pkl', 'wb') as outfile:
        pickle.dump(df, outfile)
        outfile.close()


get_community_ids()
