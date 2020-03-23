import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import pickle
import pandas as pd
import scipy
from matplotlib.colors import LogNorm
import re
import numpy as np

sns.set_style("whitegrid")


# import the network pickles:
with open('network_pickles/network1', 'rb') as filehandle:
    network1 = pickle.load(filehandle)
with open('network_pickles/network2', 'rb') as filehandle:
    network2 = pickle.load(filehandle)
with open('network_pickles/networks4', 'rb') as filehandle:
    network4 = pickle.load(filehandle)

# import measures of success
with open('measures', 'rb') as filehandle:
    measures = pickle.load(filehandle)

# For the measures, first only count the flat number of all of them to get an int
#measures = dict(zip(measures.keys(), list(map(lambda x: len(x), measures.values()))))

# Only get fork or watch events
measures = dict(zip(measures.keys(), list(map(lambda x: len(list(filter(lambda y: re.search("Fork", y), x))),
                                              measures.values()))))


# ------------ Network measures ---------------

def make_all_plots():

    # Overall networks

    def degree_dist(n):

        # Color the repo points only based on measures of success (len of events)
        # Need to color only half the nodes

        # >>>>>>>>>>>>>>>>>>>>>> Take out nodes with degree = 1?
        if n == network1:

            d = dict(nx.degree(n))
            dfdegree = pd.DataFrame(list(d.items()), columns=['user_node', 'Node Degree'])
            dfdegree.sort_values('Node Degree', inplace=True, ascending=False)
            dfdegree = dfdegree.reset_index(drop=True)

            dfsuccess = pd.DataFrame(list(measures.items()), columns=['user_node', 'Repo Success'])
            df_outer = pd.merge(dfdegree, dfsuccess, on='user_node', how='outer')  # >>>>>>>>>>>>>>>>>>>>> about 100 nodes are missing, they don't get joined?
            df_outer['Repo Success'] = df_outer['Repo Success'].fillna(value=-1000)

            df_inner = pd.merge(dfdegree, dfsuccess, on='user_node', how='inner')
            df_inner['Repo Success'] = df_inner['Repo Success']
            stats = scipy.stats.spearmanr(df_inner['Node Degree'], df_inner['Repo Success'])

            ax = sns.scatterplot(data=df_outer, x=df_outer.index, y='Node Degree', hue='Repo Success',
                                 size='Repo Success', alpha=0.7, palette='Blues', hue_norm=LogNorm(),
                                 size_norm=LogNorm(), sizes=(2, 100), linewidth=0)
            ax.text(6400, 12, r'$\rho = $' + format(stats.correlation, '.4f') + ' (p = ' + format(stats.pvalue, '.2f') + ')',
                    horizontalalignment='left', size='medium', color='black', weight='regular')

            ax.set_yscale('log')
            ax.set(ylabel='log(Degree)')
            ax.set(xlabel='Node # (rank order)')
            plt.show()

        else:

            degree_sequence = sorted([d for n, d in n.degree()], reverse=True)
            ax = sns.scatterplot(x=list(range(0, len(degree_sequence))), y=degree_sequence, linewidth=0,
                                 alpha=0.5, palette='Blues')
            ax.set_yscale('symlog')
            ax.set(ylabel='log(Degree)')
            ax.set(xlabel='User Node # (rank order)')
            plt.show()


    def centrality_dist(n):

        if n == network1:

            d = dict(nx.degree_centrality(n))
            dfdegree = pd.DataFrame(list(d.items()), columns=['user_node', 'Node Centrality'])
            dfdegree.sort_values('Node Centrality', inplace=True, ascending=False)
            dfdegree = dfdegree.reset_index(drop=True)

            dfsuccess = pd.DataFrame(list(measures.items()), columns=['user_node', 'Repo Success'])
            df_outer = pd.merge(dfdegree, dfsuccess, on='user_node', how='outer')  # >>>>>>>>>>>>>>>>>>>>> about 100 nodes are missing, they don't get joined?
            df_outer['Repo Success'] = df_outer['Repo Success'].fillna(value=-1000)

            df_inner = pd.merge(dfdegree, dfsuccess, on='user_node', how='inner')
            df_inner['Repo Success'] = df_inner['Repo Success']
            stats = scipy.stats.spearmanr(df_inner['Node Centrality'], df_inner['Repo Success'])

            ax = sns.scatterplot(data=df_outer, x=df_outer.index, y='Node Centrality', hue='Repo Success',
                                 size='Repo Success', alpha=0.7, palette='Blues', hue_norm=LogNorm(), size_norm=LogNorm())
            ax.text(500, 0.004, r'$\rho = $' + format(stats.correlation, '.4f') + ' (p = ' + format(stats.pvalue, '.2f') + ')',
                    horizontalalignment='left', size='medium', color='black', weight='regular')

            ax.set_yscale('symlog')
            ax.set_xscale('symlog')
            ax.set(ylabel='log(Centrality)')
            ax.set(xlabel='Node # (log rank order)')
            plt.show()

        else:

            degree_sequence = sorted(list(nx.degree_centrality(n).values()), reverse=True)
            ax = sns.scatterplot(x=list(range(0, len(degree_sequence))), y=degree_sequence, linewidth=0, alpha=0.5)
            ax.set_yscale('symlog')
            ax.set_xscale('symlog')
            ax.set(ylabel='log(Centrality)')
            ax.set(xlabel='User Node # (rank order)')
            plt.show()


    def evc_dist(n):

        if n == network1:

            d = dict(nx.eigenvector_centrality(n))
            dfdegree = pd.DataFrame(list(d.items()), columns=['user_node', 'Eigenvector Centrality'])
            dfdegree.sort_values('Eigenvector Centrality', inplace=True, ascending=False)
            dfdegree = dfdegree.reset_index(drop=True)

            dfsuccess = pd.DataFrame(list(measures.items()), columns=['user_node', 'Repo Success'])
            df_outer = pd.merge(dfdegree, dfsuccess, on='user_node', how='outer')  # >>>>>>>>>>>>>>>>>>>>> about 100 nodes are missing, they don't get joined?
            df_outer['Repo Success'] = df_outer['Repo Success'].fillna(value=-1000)

            df_inner = pd.merge(dfdegree, dfsuccess, on='user_node', how='inner')
            df_inner['Repo Success'] = df_inner['Repo Success']
            stats = scipy.stats.spearmanr(df_inner['Eigenvector Centrality'], df_inner['Repo Success'])

            ax = sns.scatterplot(data=df_outer, x=df_outer.index, y='Eigenvector Centrality', hue='Repo Success',
                                 size='Repo Success', alpha=0.7, palette='Blues', hue_norm=LogNorm(),
                                 size_norm=LogNorm(), sizes=(2, 100), linewidth=0)
            ax.text(100, 0.1, r'$\rho = $' + format(stats.correlation, '.4f') + ' (p = ' + format(stats.pvalue, '.2f') + ')',
                    horizontalalignment='left', size='medium', color='black', weight='regular')

            ax.set_yscale('symlog')
            ax.set_xscale('symlog')
            ax.set(ylabel='log(Eigenvector Centrality)')
            ax.set(xlabel='Node # (rank order)')
            plt.show()

        else:

            degree_sequence = sorted(list(nx.eigenvector_centrality(n).values()), reverse=True)
            ax = sns.scatterplot(x=list(range(0, len(degree_sequence))), y=degree_sequence, linewidth=0,
                                 alpha=0.5, palette='Blues')
            ax.set_yscale('symlog')
            ax.set_xscale('symlog')
            ax.set(ylabel='log(Eigenvector Centrality)')
            ax.set(xlabel='User Node # (rank order)')
            plt.show()


    degree_dist(network1)
    degree_dist(network2)
    centrality_dist(network1)
    centrality_dist(network2)
    evc_dist(network1)
    evc_dist(network2)


    # Repo-specific networks

    # Gotta make a DF for all of this for sns to work nicely
    # header: repo, node number, degree, centrality, evc

    def make_df(ns):

        dataframedegree = pd.DataFrame()
        dataframcentrality = pd.DataFrame()
        dataframepagerank = pd.DataFrame()

        for network in ns:
            repo = network.name
            pr = nx.pagerank(network)
            dc = nx.degree_centrality(network)
            d = dict(nx.degree(network))

            dfdegree = pd.DataFrame(list(d.items()), columns=['user_node', 'degree'])
            dfdegree.sort_values('degree', inplace=True, ascending=False)
            dfdegree = dfdegree.reset_index(drop=True)

            dfcentrality = pd.DataFrame(list(dc.items()), columns=['user_node', 'centrality'])
            dfcentrality.sort_values('centrality', inplace=True, ascending=False)
            dfcentrality = dfcentrality.reset_index(drop=True)

            dfpagerank = pd.DataFrame(list(pr.items()), columns=['user_node', 'pagerank'])
            dfpagerank.sort_values('pagerank', inplace=True, ascending=False)
            dfpagerank = dfpagerank.reset_index(drop=True)

            dfdegree['repo'] = repo
            dfdegree['success'] = measures.get(repo)
            dfcentrality['repo'] = repo
            dfcentrality['success'] = measures.get(repo)
            dfpagerank['repo'] = repo
            dfpagerank['success'] = measures.get(repo)

            dataframedegree = pd.concat([dataframedegree, dfdegree])
            dataframcentrality = pd.concat([dataframcentrality, dfcentrality])
            dataframepagerank = pd.concat([dataframepagerank, dfpagerank])

        return dataframedegree, dataframcentrality, dataframepagerank


    def degree_dists(df):

        ax = sns.lineplot(data=df.reset_index(), x='index', y='degree', hue='repo',  palette="Blues", legend=False, size=0.5)
        entropies = []
        successes = []
        for graph in network4:
            s = measures.get(graph.name)
            if not s: continue
            successes.append(measures.get(graph.name))
            degrees = sorted(list(dict(nx.degree(graph)).values()), reverse=True)
            entropy = scipy.stats.entropy(degrees)
            entropies.append(entropy)
        result = scipy.stats.spearmanr(successes, entropies)
        ax.text(10, 10, r'$\rho = $' + format(result.correlation, '.4f') + ' (p = ' + format(result.pvalue, '.2f') + ')',
                horizontalalignment='left', size='medium', color='black', weight='regular')
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set(ylabel='log(Degree)')
        ax.set(xlabel='Node # (log rank order)')
        plt.show()


    def centrality_dists(df):

        ax = sns.lineplot(data=df.reset_index(), x='index', y='centrality', hue='repo', palette="Blues", legend=False, size=0.5)
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set(ylabel='log(Centrality)')
        ax.set(xlabel='Node # (log rank order)')
        plt.show()


    def pagerank_dists(df):

        ax = sns.lineplot(data=df.reset_index(), x='index', y='pagerank', hue='repo', palette="Blues", legend=False, size=0.5)
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set(ylabel='log(Pagerank)')
        ax.set(xlabel='Node # (log rank order)')
        plt.show()


    dataframedegree, dataframcentrality, dataframepagerank = make_df(network4)
    degree_dists(dataframedegree)
    centrality_dists(dataframcentrality)
    pagerank_dists(dataframepagerank)


# ------------ Network viz ---------------

def viz_networks():

    # ------ networks 1 and 2 -------------

    def whole_network(G, measures, title):

        # Pick a component instead of whole network
        #G = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[1]).copy()

        # Only get biggest nodes for a particular measure
        # measures = dict((k, v) for k, v in measures.items() if v >= 0.08)
        # G = G.subgraph(list(measures.keys())).copy()

        pos = nx.spring_layout(G)
        # Can take some time to calculate, so use a pickle for faster results on multiple iterations
        # pos = pickle.load(open("posnetworks1", "rb"))
        # with open('posnetworks1', 'wb') as outfile:
        #    pickle.dump(pos, outfile)
        #    outfile.close()

        nodes = nx.draw_networkx_nodes(G, pos, node_size=4, cmap=plt.cm.cividis,
                                       node_color=list(measures.values()),
                                       nodelist=list(measures.keys()))
        nodes.set_norm(mcolors.SymLogNorm(linthresh=0.01, linscale=1))

        # labels = nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)

        plt.colorbar(nodes)
        plt.title(title)
        plt.axis('off')
        plt.show()

    G = network2

    # most popular repos
    # collections.Counter(list(nx.get_edge_attributes(G, 'type').values()))

    # Color by some measure
    #measures = nx.degree_centrality(G)
    title = 'User Interactions via Shared Repos\nDegree Centrality'
    #whole_network(G, measures, title)


    def bipartite_network(G, title):

        # Pick a component instead of whole network
        # G = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[1]).copy()

        pos = nx.spring_layout(G)
        # Can take some time to calculate, so use a pickle for faster results on multiple iterations
        # pos = pickle.load(open("posnetworks1", "rb"))
        # with open('posnetworks1', 'wb') as outfile:
        #    pickle.dump(pos, outfile)
        #    outfile.close()

        repo_nodes = list(filter(lambda x: x[1]['bipartite'] == 1, list(G.nodes(data=True))))
        repo_nodes = list(map(lambda x: x[0], repo_nodes))
        user_nodes = list(filter(lambda x: x[1]['bipartite'] == 0, list(G.nodes(data=True))))
        user_nodes = list(map(lambda x: x[0], user_nodes))
        nx.draw_networkx_nodes(G, pos, nodelist=repo_nodes, node_color='#fcb800', node_size=4, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=user_nodes, node_color='#66a1ff', node_size=4, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.2)

        plt.title(title)
        plt.axis('off')
        plt.show()


    G = network1
    title = 'User & Repos via Push/Pull Events'
    #bipartite_network(G, title)


    def smallworld(G):

        numnodes = G.number_of_nodes()
        numedges = G.number_of_edges()
        nodedegree = (numedges * 2.0) / numnodes
        c_sm = nx.average_clustering(G)  # c^ws in H&G (2006)
        # c_sm=sum(nx.triangles(usfg).values())/(# of paths of length 2) # c^tri
        l_sm = nx.average_shortest_path_length(G)
        # c_rand same as edge density for a random graph? not sure if "-1" belongs in denominator, double check
        # c_rand= (numedges*2.0)/(numnodes*(numnodes-1))   # c^ws_rand?
        c_rand = float(nodedegree) / numnodes  # c^tri_rand?
        l_rand = np.log(numnodes) / np.log(nodedegree)  # approximation, see humphries & gurney (2008) eq 11
        # l_rand= (np.log(numnodes)-0.5772)/(np.log(nodedegree)) + .5 # alternative ASPL from fronczak, fronczak & holyst (2004)
        s = (c_sm / c_rand) / (l_sm / l_rand)
        return s


    def hub_spokes_network4(G):

        # Small world network vs scale free network
        # Small world: sigma and omega
        # Scale free:

        successes = []
        sms = []

        for graph in G:
            s = measures.get(graph.name)
            if not s: continue
            if not nx.is_connected(graph): continue
            successes.append(measures.get(graph.name))
            sms.append(smallworld(graph))
            print(G.index(graph))

        result = scipy.stats.spearmanr(successes, sms)
        print(result)

    hub_spokes_network4(network4)


#make_all_plots()
viz_networks()

