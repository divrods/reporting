# TO Run - workon divrods_reporting
# pip install requirements.txt
# python generate_network_graph.py

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as net
import math
import struct
from utils import read_prefs_data
from utils import read_artwork_data
from colour import Color
from math import ceil, floor

PREF_CSV_PATH = './data/prefs2080423.csv'
FIXED_PREF_CSV_PATH = './data/prefs2080423REPAIRED.csv'
PREF_CSV_PATH = FIXED_PREF_CSV_PATH
ARTWORK_CSV_PATH = './data/artwork_data.csv'
GRAPH_DEST = './output/divrod_network_map.png'
MIN_SUPPORT = 15
RELATION_MAP = {}
SKIP_ADMIN_SURVEY = True


# Generate Color distro for nodes
TOTAL_COLOR_STEPS = 11 # This should be an odd #
NODE_COLOR_RANGE = list(Color('#C21807').range_to(Color('#ed4400'), int(floor(TOTAL_COLOR_STEPS/2)))) + list(Color('#68a800').range_to(Color('green'), int(floor(TOTAL_COLOR_STEPS/2))))
# NODE_COLOR_RANGE = list(Color('#C21807').range_to(Color('#ed4400'), int(floor(TOTAL_COLOR_STEPS/2)))) + list(Color('#68a800').range_to(Color('green'), int(floor(TOTAL_COLOR_STEPS/2))))
EDGE_COLOR_RANGE = list(Color('#696969').range_to(Color('#000'), int(floor(TOTAL_COLOR_STEPS/2)))) + list(Color('#696969').range_to(Color('#000'), int(floor(TOTAL_COLOR_STEPS/2))))

NODE_COLOR_RANGE = list(Color('#C21807').range_to(Color('#ed4400'), int(floor(TOTAL_COLOR_STEPS/2) - 1))) + list(Color('#FFD900').range_to(Color('#FFF700'), 2)) + list(Color('#68a800').range_to(Color('green'), int(floor(TOTAL_COLOR_STEPS/2) - 1 )))


# NODE_COLOR_RANGE = list(Color('#C21807').range_to(Color('#ed4400'), int(floor(TOTAL_COLOR_STEPS/2) - 1 ))) + [Color('pink'), Color('blue'), Color('purple')] + list(Color('#68a800').range_to(Color('green'), int(floor(TOTAL_COLOR_STEPS/2) - 1)))

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
            occ = 0
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

                    if (item1['occurances'] > MIN_SUPPORT and
                            item2['occurances'] > MIN_SUPPORT):
                        tuples.append((item1, item2))

                    pair_count = RELATION_MAP.get((item1['item_id'],
                                                  item2['item_id']), 0)
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

    nodes = node_map.values()

    # create networkx graph
    G = net.Graph()

    # add nodes
    for node in nodes:
        node_data = {'item_id': node['item_id'],
                     'occurances': node['occurances'],
                     'score': ((1.0 * node['total_likes']) / node['occurances'])}
        G.add_node(node['item_id'], **node_data)

    # add edges
    for edge in graph:
        frequency = RELATION_MAP[(edge[0]['item_id'], edge[1]['item_id'])] + RELATION_MAP[(edge[0]['item_id'], edge[1]['item_id'])]
        G.add_edge(edge[0]['item_id'], edge[1]['item_id'], **{'frequency': frequency})

    # draw graph
    fig = plt.figure(figsize=(25, 18))
    plt.axis('off')
    plt.title("DivRods Network (min prefs %s)" % MIN_SUPPORT, fontsize=20)
    pos = net.spring_layout(G, k=1, weight='occurances')
    # pos = net.spectral_layout(G, dim=2, weight='occurances', scale=3)
    # pos = net.random_layout(G);

    # Calculate Node Size
    node_size = [math.pow(data['occurances'] / 2, 1) * 75 for __, data in G.nodes(data=True)]
    #node_color = ['#' + struct.pack('BBB',*((g[0] + r[0]) * (data['score']), (g[1] + r[1]) * (data['score']), (g[2] + r[2]) * (data['score']))).encode('hex') for __, data in G.nodes(data=True)] # This geometric mean but everything is yellow
    #node_color = ['#' + struct.pack('BBB',*(255 * data['score'], 0, 0)).encode('hex') if data['score'] < .5 else '#' + struct.pack('BBB',*(0, 255 * data['score'], 0)).encode('hex') for __, data in G.nodes(data=True)]
    node_color = [NODE_COLOR_RANGE[int(floor((floor(data['score'] * 100)/TOTAL_COLOR_STEPS)))].hex for __, data in G.nodes(data=True)]

    # Generate Node Labels
    node_labels =  generate_node_display_name(G.nodes(data=True))

    # Determine edge weight and color
    min_pair_frequency = min(float(f) for f in RELATION_MAP.values())
    max_pair_frequency = max(float(f) for f in RELATION_MAP.values())
    edge_width = [5 * (data['frequency'] - min_pair_frequency)/(max_pair_frequency - min_pair_frequency)  for __, ___, data in G.edges(data=True)]
    #edge_color = [(data['frequency'] - min_pair_frequency)/(max_pair_frequency - min_pair_frequency)  for __, ___, data in G.edges(data=True)]
    edge_color = [EDGE_COLOR_RANGE[int(floor((data['frequency'] - min_pair_frequency)/(max_pair_frequency - min_pair_frequency)))].hex for __, ___, data in G.edges(data=True)]

    # Draw nodes, edges, labels
    net.draw_networkx_nodes(G,pos, node_size=node_size, alpha=.85, node_color=node_color)
    net.draw_networkx_edges(G, pos, edge_color=edge_color, alpha=.75, width=edge_width)
    net.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

    # Draw Color legend
    #like_patch = mpatches.Patch(color='green', label='Like')
    #dislike_patch = mpatches.Patch(color='red', label='Dislike')
    #plt.legend(handles=[like_patch, dislike_patch])

    # Node Color bar...
    #ax3 = fig.add_axes([0.05, 0.15, 0.01, 0.15]) # verticle
    ax3 = fig.add_axes([0.05, 0.05, 0.3, 0.01])

    cmap = mpl.colors.ListedColormap([ c.rgb for c in NODE_COLOR_RANGE])

    bounds = [x * 0.1 for x in range(0, TOTAL_COLOR_STEPS)]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb3 = mpl.colorbar.ColorbarBase(ax3, cmap=cmap,
                                    #norm=norm,
                                    boundaries=bounds,
                                    #extend='both',
                                    # Make the length of each extension
                                    # the same as the length of the
                                    # interior colors:
                                    extendfrac='auto',
                                    ticks=bounds,

                                    #spacing='uniform',
                                    orientation='horizontal')

    cb_labels = ['' for i in range(0, len(NODE_COLOR_RANGE) + 1)]
    cb_labels[0] = 'Strong Dislike'
    cb_labels[-1] = 'Strong Like'
    cb_labels[int(floor(len(NODE_COLOR_RANGE) / 2))] = 'Neutral'

    cb3.ax.set_xticklabels(cb_labels)  # vertically oriented colorbar
    cb3.ax.xaxis.set_ticks_position('top')
    #cb3.set_label('Range: Likes vs. Dislikes', horizontalalignment='right')


    # Node Size Legend
    msizes = [0, 400, 300, 200, 100, 25]
    size_label = ['More', ' ', ' ',' ',' ','Fewer']
    markers = []
    i = 0
    for size in msizes:
        markers.append(plt.scatter([1], [2], s=size, c='#000000', label=size_label[i]))
        i += 1

    plt.legend(handles=markers, loc = 6, borderpad = 0, frameon=False, title='Size = Number of Preferences (Likes + Dislikes)', bbox_to_anchor=(2, 1), ncol=6)

    #plt.colorbar(nc)

    #plt.show() # Uncomment to launch preview window
    plt.savefig(GRAPH_DEST)

def generate_node_display_name(nodes):
    artwork_data = read_artwork_data(ARTWORK_CSV_PATH)
    title_map = {}
    for art in artwork_data:
        title_map[art['id']] = art['title']

    node_names = {}
    i = 0
    for __, data in nodes:
        node_names[data['item_id']] = title_map.get(data['item_id'], 'UNKNOWN').decode('utf-8') + '\n(%s - %s)' % (data['item_id'], data['occurances'])
    return node_names

def main():
    pref_data = read_prefs_data(PREF_CSV_PATH, skip_admin_survey=SKIP_ADMIN_SURVEY)
    print 'Read %s preferences from csv' % len(pref_data)

    graph = create_node_relationships(pref_data)
    draw_graph(graph)
    print "Done: Graph written to %s" % GRAPH_DEST

if __name__ == "__main__":
    main()