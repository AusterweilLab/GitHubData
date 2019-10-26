import networkx as nx
import re, os, json, math, time
import pickle
from networkx.algorithms import bipartite

g = nx.Graph()

# 3. Bipitarte graph between users and files for each repo

# 4. Nodes are users and edges are a shared file for each repo
# Edges can be either push or pull

# File: users
# Edge attributes make no sense for these networks


# ------------- NETWORKS 4 -------------

# Nodes are users
# Edges are a file they worked on together
# Edges do not have attributes
# Multigraphs, to denote multiple files shared between users

def make_networks_4():

    nodesusers_edgesfiles = {}

    with open('scraped_data/pull_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo = '/'.join(info['commit']['url'].split('/')[4:6])
            user = info['commit']['author']['email']
            files = list(set(list(map(lambda x: x['filename'], info['files']))))

            if repo in nodesusers_edgesfiles.keys():
                nodesusers_edgesfiles[repo].append((user, files))
            else:
                nodesusers_edgesfiles[repo] = [(user, files)]

    with open('scraped_data/push_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo = '/'.join(info['commit']['url'].split('/')[4:6])
            user = info['commit']['author']['email']
            files = list(set(list(map(lambda x: x['filename'], info['files']))))

            if repo in nodesusers_edgesfiles.keys():
                nodesusers_edgesfiles[repo].append((user, files))
            else:
                nodesusers_edgesfiles[repo] = [(user, files)]


    nodesusers_edgesfiles2 = {}

    for repo in nodesusers_edgesfiles.keys():
        nodesusers_edgesfiles2[repo] = {}

        for event in nodesusers_edgesfiles.get(repo):
            user = event[0]
            files = event[1]

            for file in files:
                if file in nodesusers_edgesfiles2[repo].keys():
                    nodesusers_edgesfiles2[repo][file].append(user)
                else:
                    nodesusers_edgesfiles2[repo][file] = [user]


    nodesusers_edgesfiles_graphs = []

    for repo in nodesusers_edgesfiles2.keys():

        graph = nx.MultiGraph()

        # One edge between two users means they worked on one file together.
        # Two edges means they worked on two files together. Edges are not weighted here.

        for file in nodesusers_edgesfiles2[repo].keys():
            users = nodesusers_edgesfiles2[repo][file]
            if len(set(users)) == 1:
                graph.add_node(users[0])
            elif len(set(users)) == 2:
                graph.add_edge(tuple(set(users))[0], tuple(set(users))[1])
            else:
                us = list(set(users))
                for i, u in enumerate(list(us)[:-1]):
                    graph.add_edge(u, us[i+1])

        nodesusers_edgesfiles_graphs.append(graph)

    return nodesusers_edgesfiles_graphs


# ------------- NETWORKS 3 -------------

# Nodes are users or files
# Edges are a push or a pull event
# Edges will have attributes
# Edges will have weights denoting number of times an event for that user-file interaction happened
# Multigraph, so if it has two edges, then means both push and pull
# One graph per repo

def make_networks_3():

    nodesusersfiles_edgesevents = {}

    with open('scraped_data/pull_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo = '/'.join(info['commit']['url'].split('/')[4:6])
            user = info['commit']['author']['email']
            files = list(set(list(map(lambda x: x['filename'], info['files']))))

            if repo in nodesusersfiles_edgesevents.keys():
                nodesusersfiles_edgesevents[repo].append([user, files, 'pull'])
            else:
                nodesusersfiles_edgesevents[repo] = [[user, files, 'pull']]

    with open('scraped_data/push_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo = '/'.join(info['commit']['url'].split('/')[4:6])
            user = info['commit']['author']['email']
            files = list(set(list(map(lambda x: x['filename'], info['files']))))

            if repo in nodesusersfiles_edgesevents.keys():
                nodesusersfiles_edgesevents[repo].append([user, files, 'push'])
            else:
                nodesusersfiles_edgesevents[repo] = [[user, files, 'push']]

    nodesusersfiles_edgesevents_graphs = []

    for repo in nodesusersfiles_edgesevents.keys():

        graph = nx.Graph()

        for event in nodesusersfiles_edgesevents.get(repo):
            user = event[0]
            files = event[1]
            event_type = event[2]

            for file in files:
                graph.add_node(user, bipartite=0)
                graph.add_node(file, bipartite=1)
                graph.add_edge(user, file, type=event_type)

    return nodesusersfiles_edgesevents_graphs


# ------------- NETWORKS 3 -------------

# Nodes are users or repos
# Edges are a push or a pull event
# Edges will have attributes
# Edges will have weights denoting number of times an event for that user-file interaction happened
# Multigraph, so if it has two edges, then means both push and pull
# One graph per repo


networks3 = make_networks_3()
networks4 = make_networks_4()