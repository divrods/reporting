# TO Run - workon divrods_reporting
# pip install requirements.txt
# python generate_network_graph.py

import matplotlib.pyplot as plt
import networkx as net
import csv
import math
import struct

PREF_CSV_PATH = './data/prefs2080423.csv'
MIN_SUPPORT = 20
RELATION_MAP = {}


def read_prefs_data():
    return_objects = []
    with open(PREF_CSV_PATH, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        row_num = 0
        for row in csvreader:
            row_num += 1

            if row_num == 1 or row[1].startswith('admin_survey'):
                continue # header

            return_objects.append(
                {
                    'resource_id': row[0],
                    'user_id': row[1],
                    'item_id': row[2],
                    'pref': row[3],
                    'synced_timestamp': row[4],
                    'timestamp': row[5],
                    'occurances': 0,
                    'total_likes': 0
                })
    return return_objects

def create_node_relationships(pref_data):
    # Cluster into buckets by user

    sessions = {}
    occurance_map = {}
    total_likes_map = {}

    for pref in pref_data:
        sess = sessions.get(pref['user_id'])
        if not sess:
            sess = {}

        # Count Occurances
        occ = occurance_map.get(pref['item_id'])
        if not occ:
            occ = 0;
        occ += 1
        occurance_map[pref['item_id']] = occ

        # Count total_likes
        likes = total_likes_map.get(pref['item_id'], 0)
        if not likes:
            likes = 0
        if (pref['pref'] == 'True'):
            likes += 1
        total_likes_map[pref['item_id']] = likes

        sess[pref['item_id']] = pref
        sessions[pref['user_id']] = sess

    # Now make relationship tuples
    tuples = []
    for sess in sessions.values():
        for item1 in sess.values():
            for item2 in sess.values():
                if item1['item_id'] != item2['item_id']:
                    item1['occurances'] = occurance_map[item1['item_id']]
                    item2['occurances'] = occurance_map[item2['item_id']]
                    item1['total_likes'] = total_likes_map[item1['item_id']]
                    item2['total_likes'] = total_likes_map[item2['item_id']]

                    if (item1['occurances'] > MIN_SUPPORT and item2['occurances'] > MIN_SUPPORT):
                        tuples.append((item1, item2))

                    pair_count = RELATION_MAP.get((item1['item_id'], item2['item_id']), 0)
                    if (not pair_count):
                        pair_count = 0
                    RELATION_MAP[(item1['item_id'], item2['item_id'])] = pair_count + 1

    return tuples



def draw_graph(graph):

    # extract nodes from graph
    node_map = {}
    for n1, n2 in graph:
        node_map[n1['item_id']] = n1
        node_map[n2['item_id']] = n2

    nodes = node_map.values();

    # create networkx graph
    G=net.Graph()

    # add nodes
    for node in nodes:
        G.add_node(node['item_id'], **{'occurances' : node['occurances'], 'score': ((1.0* node['total_likes']) / node['occurances'])})

    # add edges
    for edge in graph:
        frequency = RELATION_MAP[(edge[0]['item_id'], edge[1]['item_id'])] + RELATION_MAP[(edge[0]['item_id'], edge[1]['item_id'])]
        G.add_edge(edge[0]['item_id'], edge[1]['item_id'], **{'frequency': frequency})

    # draw graph
    plt.figure(figsize=(18,18))
    plt.axis('off')
    plt.title("DivRods Network (min prefs %s)" % MIN_SUPPORT, fontsize=20)
    pos = net.spring_layout(G, k=1, weight='occurances')
    #pos = net.spectral_layout(G, dim=2, weight='occurances', scale=3)
    #pos = net.random_layout(G);

    node_size = [math.pow(data['occurances'] / 2, 1) * 75 for __, data in G.nodes(data=True)]
    #node_color = ['#' + struct.pack('BBB',*((g[0] + r[0]) * (data['score']), (g[1] + r[1]) * (data['score']), (g[2] + r[2]) * (data['score']))).encode('hex') for __, data in G.nodes(data=True)] # This geometric mean but everything is yellow
    node_color = ['#' + struct.pack('BBB',*(255 * data['score'], 0, 0)).encode('hex') if data['score'] < .5 else '#' + struct.pack('BBB',*(0, 255 * data['score'], 0)).encode('hex') for __, data in G.nodes(data=True)]

    min_pair_frequency = min(float(f) for f in RELATION_MAP.values())
    max_pair_frequency = max(float(f) for f in RELATION_MAP.values())
    edge_width = [5 * (data['frequency'] - min_pair_frequency)/(max_pair_frequency - min_pair_frequency)  for __, ___, data in G.edges(data=True)]
    edge_alpha = [(data['frequency'] - min_pair_frequency)/(max_pair_frequency - min_pair_frequency)  for __, ___, data in G.edges(data=True)]

    net.draw_networkx_nodes(G,pos, node_size=node_size, alpha=.85, node_color=node_color)
    net.draw_networkx_edges(G, pos, edge_color=edge_alpha, alpha=.75, width=edge_width)
    net.draw_networkx_labels(G, pos, font_size=10)

    #plt.show() # Uncomment to launch preview window
    plt.savefig('./output/divrod_network_map_no_survey.png')

def main():

    pref_data = read_prefs_data();
    graph = create_node_relationships(pref_data)
    draw_graph(graph)
    print "Done: Check your output folder."

if __name__ == "__main__":
    main()