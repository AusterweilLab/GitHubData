import networkx as nx
import json, itertools, re
import collections
import matplotlib.pyplot as plt
import seaborn as sns
from networkx.algorithms import bipartite

# ------------- NETWORK 1 -------------

# Single static graph
# Nodes are users or repos
# Edges are a push or a pull event
# Edges will have attributes
# Edges will have weights denoting number of times an event for that user-repo interaction happened
# Multigraph, so if it has two edges, then means both push and pull


def make_network_1():

    nodesusersfiles_edgesevents = {}

    with open('scraped_data/pull_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
            user = info['commit']['author']['email']

            if repo in nodesusersfiles_edgesevents.keys():
                nodesusersfiles_edgesevents[repo].append([user, 'pull'])
            else:
                nodesusersfiles_edgesevents[repo] = [[user, 'pull']]

    with open('scraped_data/push_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
            user = info['commit']['author']['email']

            if repo in nodesusersfiles_edgesevents.keys():
                nodesusersfiles_edgesevents[repo].append([user, 'push'])
            else:
                nodesusersfiles_edgesevents[repo] = [[user, 'push']]

    graph = nx.Graph()

    for repo in nodesusersfiles_edgesevents.keys():

        for event in nodesusersfiles_edgesevents.get(repo):
            user = event[0]
            event_type = event[1]

            # Check to see if edge is already in there, if it is, adjust the weight
            existing_edges = graph.get_edge_data(user, repo, default=None)

            if existing_edges:  # If it has this edge

                found_edge = False

                try:
                    int(list(existing_edges.keys())[0])
                    for edge in existing_edges.keys():
                        type2 = existing_edges[edge]['type']
                        if type2 == event_type:  # If that edge is the certain repo type
                            weight = existing_edges[edge]['weight']
                            weight += 1
                            graph.add_edge(user, repo, weight=weight, type=repo)
                            found_edge = True

                        else:
                            continue

                except:
                    type2 = existing_edges['type']
                    if type2 == event_type:  # If that edge is the certain repo type
                        weight = existing_edges['weight']
                        weight += 1
                        graph.add_edge(user, repo, weight=weight, type=repo)
                        found_edge = True

                if not found_edge:  # In case the edge exists but it's actually not the right type
                    graph.add_edge(user, repo, weight=1, type=repo)

            else:
                graph.add_node(user, bipartite=0)
                graph.add_node(repo, bipartite=1)
                graph.add_edge(user, repo, type=event_type, weight=1)

    return graph


# ------------- NETWORKS 2 -------------

# Nodes are users
# Edges are a repo they worked on together
# Edges do not have attributes
# Edges have weights to denote multiple repos between users

def make_network_2():

    nodesusers_edgesrepos = {}

    with open('scraped_data/pull_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
            user = info['commit']['author']['email']

            if repo in nodesusers_edgesrepos.keys():
                nodesusers_edgesrepos[repo].append(user)
            else:
                nodesusers_edgesrepos[repo] = [user]

    with open('scraped_data/push_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
            user = info['commit']['author']['email']

            if repo in nodesusers_edgesrepos.keys():
                nodesusers_edgesrepos[repo].append(user)
            else:
                nodesusers_edgesrepos[repo] = [user]


    graph = nx.MultiGraph()

    for repo in nodesusers_edgesrepos.keys():

        users = list(set(nodesusers_edgesrepos[repo]))

        if len(users) > 1:  # Have to be more than one user to make an edge
            edges = list(itertools.combinations(users, 2))

            for edge in edges:

                # if edge already in here, update weight
                # Check to see if edge is already in there, if it is, adjust the weight
                existing_edges = graph.get_edge_data(edge[0], edge[1], default=None)

                if existing_edges:  # If it has this edge

                    found_edge = False

                    try:
                        int(list(existing_edges.keys())[0])
                        for e in existing_edges.keys():
                            type2 = existing_edges[e]['type']
                            if type2 == repo:  # If that edge is the certain repo type
                                weight = existing_edges[e]['weight']
                                weight += 1
                                graph.add_edge(edge[0], edge[1], weight=weight, type=repo)
                                found_edge = True

                            else:
                                continue

                    except:
                        type2 = existing_edges['type']
                        if type2 == repo:  # If that edge is the certain repo type
                            weight = existing_edges['weight']
                            weight += 1
                            graph.add_edge(edge[0], edge[1], weight=weight, type=repo)
                            found_edge = True

                    if not found_edge:  # In case the edge exists but it's actually not the right type
                        graph.add_edge(edge[0], edge[1], weight=1, type=repo)

                else:
                    graph.add_edge(edge[0], edge[1], type=repo, weight=1)

        else:
            graph.add_node(users[0])

    return graph


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

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
            user = info['commit']['author']['email']
            files = list(set(list(map(lambda x: x['filename'], info['files']))))

            if repo in nodesusersfiles_edgesevents.keys():
                nodesusersfiles_edgesevents[repo].append([user, files, 'pull'])
            else:
                nodesusersfiles_edgesevents[repo] = [[user, files, 'pull']]

    with open('scraped_data/push_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
            user = info['commit']['author']['email']
            files = list(set(list(map(lambda x: x['filename'], info['files']))))

            if repo in nodesusersfiles_edgesevents.keys():
                nodesusersfiles_edgesevents[repo].append([user, files, 'push'])
            else:
                nodesusersfiles_edgesevents[repo] = [[user, files, 'push']]


    nodesusersfiles_edgesevents_graphs = []

    for repo in nodesusersfiles_edgesevents.keys():

        graph = nx.MultiGraph()

        for event in nodesusersfiles_edgesevents.get(repo):
            user = event[0]
            files = event[1]
            event_type = event[2]

            for file in files:

                # Check to see if edge is already in there, if it is, adjust the weight
                existing_edges = graph.get_edge_data(user, file, default=None)

                if existing_edges:  # If it has this edge

                    found_edge = False
                    es = list(existing_edges.keys())

                    for edge in es:
                        type2 = existing_edges[edge]['type']
                        if type2 == event_type:  # If that edge is the certain repo type
                            weight = existing_edges[edge]['weight']
                            weight += 1
                            graph.add_edge(user, file, weight=weight, type=event_type)
                            found_edge = True

                        else:
                            continue

                    if not found_edge:  # In case the edge exists but it's actually not the right type
                        graph.add_edge(user, file, weight=1, type=event_type)

                else:
                    graph.add_node(user, bipartite=0)
                    graph.add_node(file, bipartite=1)
                    graph.add_edge(user, file, type=event_type, weight=1)

        nodesusersfiles_edgesevents_graphs.append(graph)


    return nodesusersfiles_edgesevents_graphs


# ------------- NETWORKS 4 -------------

# Nodes are users
# Edges are a file they worked on together
# Edges do not have attributes
# Edges have weights to denote multiple files between users

def make_networks_4():

    nodesusers_edgesfiles = {}

    with open('scraped_data/pull_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
            user = info['commit']['author']['email']
            files = list(set(list(map(lambda x: x['filename'], info['files']))))

            if repo in nodesusers_edgesfiles.keys():
                nodesusers_edgesfiles[repo].append((user, files))
            else:
                nodesusers_edgesfiles[repo] = [(user, files)]

    with open('scraped_data/push_json_files.json', 'r') as pull_file:
        for line in pull_file:

            info = json.loads(line)

            repo_url = re.findall('.+?(?=\/git\/commits)', info['commit']['url'])[0]
            repo = repo_url.split('/')[-1]
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
        # Two edges means they worked on two files together. Turn into weights.

        for file in nodesusers_edgesfiles2[repo].keys():
            users = nodesusers_edgesfiles2[repo][file]
            if len(set(users)) == 1:
                graph.add_node(users[0])
            elif len(set(users)) == 2:

                # check to see if this edge is in there already, to update weight
                weight = graph.get_edge_data(tuple(set(users))[0], tuple(set(users))[1], default=None)

                if weight:
                    weight = weight[0]['weight']
                    weight += 1
                else:
                    weight = 1

                graph.add_edge(tuple(set(users))[0], tuple(set(users))[1], weight=weight)

            else:
                us = list(set(users))
                for i, u in enumerate(list(us)[:-1]):

                    # check to see if this edge is in there already, to update weight
                    weight = graph.get_edge_data(u, us[i+1], default=None)

                    if weight:
                        weight = weight[0]['weight']
                        weight += 1
                    else:
                        weight = 1

                    graph.add_edge(u, us[i+1], weight=weight)


        nodesusers_edgesfiles_graphs.append(graph)


    return nodesusers_edgesfiles_graphs


#network1 = make_network_1()
#network2 = make_network_2()
#networks3 = make_networks_3()
networks4 = make_networks_4()



# ------------ Network measures ---------------

# network 2
# degree dist

#degree_sequence = sorted([d for n, d in network2.degree()], reverse=True)
#ax = sns.distplot(degree_sequence, kde=False, rug=True)
#ax.set_yscale('log')
#ax.set(xlabel='Degree', ylabel='log(N nodes with degree)')
#plt.show()

# networks 4
# degree dists

fig, ax = plt.subplots()
for i, network in enumerate(networks4):
    degree_sequence = sorted([d for n, d in network.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())
    sns.lineplot(deg, cnt, markers=True, ax=ax)
ax.set_yscale('log')
ax.set_xscale('log')
ax.set(xlabel='Node', ylabel='Degree')
plt.show()

# centrality

