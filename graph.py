import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.cm as cmx
import matplotlib.colors as colors
import sys

def get_graph_item(data):
    """ Item level graph"""
    # Compute distances using inverse max count and add to data
    dist = 1 / data.groupby(['item_number', 'antenna_id'])['count'].max()
    dist.name = 'dist'
    data = data.join(dist, on=['item_number', 'antenna_id'], how='inner', lsuffix='item_number')

    edge_data = data.groupby(['item_number', 'antenna_id'])['dist']
    edges = [] # Store edges as tuple (node1, node2, weight)
    for (item_number, antenna_id), group in edge_data:
        edges.append((item_number, antenna_id, group.values[0]))

    items = data['item_number'].unique()
    antennas = data['antenna_id'].unique()

    return (items, antennas, edges)

def draw_graph_item(graph_data):
    (items, antennas, edges) = graph_data
    print len(items)
    print len(antennas)
    print len(edges)
    G = nx.Graph()
    G.add_nodes_from(items)
    G.add_nodes_from(antennas)
    G.add_weighted_edges_from(edges)

    # Draw network
    pos = nx.graphviz_layout(G, prog='neato')
    nx.draw_networkx_nodes(G, pos, nodelist=items.tolist(), node_color = 'b', node_size=100, alpha=0.8)
    nx.draw_networkx_nodes(G, pos, nodelist=antennas.tolist(), node_color='y', node_size=150, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=1,alpha=0.5)
    plt.axis('off')
    line1 = mlines.Line2D(range(1), range(1), marker='o', markerfacecolor="blue")
    line2 = mlines.Line2D(range(1), range(1), marker='o',markerfacecolor="yellow")
    plt.legend((line1, line2), ("Items", "Antennas"))
    plt.title("Relative locations of items and antennas using inverse max counts and counts > 1000")
    plt.show()

def get_graph_style(data, taxon):
    """ Style level graph"""
    data['count'][data['count'] > 500] = 500
    # Normalize by max count of antenna
    # max_count = data.groupby(['antenna_id'])['count'].max()
    # max_count.name = 'max_count'
    # data = data.join(max_count, on='antenna_id', how='inner', lsuffix='antenna_id')
    # data['norm_count'] = data['count'] / data['max_count']

    # Work at style level
    data = pd.merge(data, taxon, on='item_number', how='inner')
    dist = 1 / data.groupby(['style', 'antenna_id'])['count'].max()
    dist.name = 'dist'
    data = data.join(dist, on=['style', 'antenna_id'], how='inner', lsuffix=['style', 'antenna_id'])

    edge_data = data.groupby(['style', 'antenna_id'])['dist']
    edges = [] # Store edges as tuple (node1, node2, weight)
    for (style, antenna_id), group in edge_data:
        edges.append((style, antenna_id, group.values[0]))

    antennas = data['antenna_id'].unique()
    #print data['style', 'category']
    # Category labels
    styles = []

    cat_groups = data.drop_duplicates(subset='style').groupby(['category'])
    for category, group in cat_groups:
        styles.append((category, group['style'].tolist()))

    categories = {}
    cat_groups = data.drop_duplicates(subset='style').groupby(['category'])
    for category, group in cat_groups:
        cat = category.split()[0]
        if cat not in categories:
            categories[cat] = []
        categories[cat] += group['style'].tolist()
    categories = [(key, value) for key,value in categories.items()]
    return (styles, antennas, edges), (categories, antennas, edges)

def draw_graph_style(graph_data):
    (items, antennas, edges) = graph_data
    antennas = antennas.tolist()
    print "Num styles:", sum([len(x[1]) for x in items])
    print "Num categories:", len(items)
    print "Num antennas:", len(antennas)
    print "Num edges:", len(edges)
    G = nx.Graph()
    for (category, style) in items:
        G.add_nodes_from(style)
    G.add_nodes_from(antennas)
    G.add_weighted_edges_from(edges)

    # Draw network
    pos = nx.graphviz_layout(G, prog='neato')
    colors = get_cmap(len(items))
    for index, (category, style) in enumerate(items):
        nx.draw_networkx_nodes(G, pos, nodelist=style, node_color = colors(index), node_size=100, alpha=0.8)
    nx.draw_networkx_nodes(G, pos, nodelist=antennas, node_color='w', node_size=150, alpha=0.8, label=[str(x) for x in antennas])
    nx.draw_networkx_edges(G, pos, width=1,alpha=0.5)
    plt.axis('off')
    lines = [mlines.Line2D(range(1), range(1), marker='o',markerfacecolor="w",markersize=5)]
    for i in range(len(items)):
        lines.append(mlines.Line2D(range(1), range(1), marker='o',markerfacecolor=colors(i),markersize=5))

    plt.legend(lines, ["Antennas"] + [x[0] for x in items],prop={'size':9})
    day = sys.argv[1].split(".")[0][-1]
    plt.title("Relative map of styles and antennas using inverse max counts and counts > 100 on day %s data" %day)
    plt.show()

def get_cmap(N):
    '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct
    RGB color.'''
    color_norm  = colors.Normalize(vmin=0, vmax=N)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv')
    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index)
    return map_index_to_rgb_color

def filter_data(data):
    data = data[data['count'] > 100]
    data = data[(data.antenna_id < 1400) | (data.antenna_id >= 1500)]
    data['antenna_id'] = data['antenna_id']*-1

def algorithm1():
    """ Use inverse counts as distance"""
    style, categories = get_graph_style(data, taxon)
    plt.figure(1)
    draw_graph_style(style)
    plt.figure(2)
    draw_graph_style(categories)

def algorithm2():


if __name__ == '__main__':
    data = pd.read_csv(sys.argv[1])
    taxon = pd.read_csv('taxonomy.csv')
    print "Num Styles: ", len(taxon.style.unique())
    filter_data(data)
