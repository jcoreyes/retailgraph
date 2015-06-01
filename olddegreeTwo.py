# degreeTwo.py
# Aakash Indurkhya
import numpy as np 
from matplotlib import pyplot as plt 
import pandas as pd 
import itertools as itools
import networkx as nx 
import sys
import pickle
data = pd.read_csv(sys.argv[1])
antenna_map = {}
G = nx.Graph()
antennas = list(pd.unique(data['antenna_id']))

for a in antennas: 
    G.add_node(a)

pairs = list(itools.combinations(antennas, 2))
for pair in pairs:
    # print pair
    id1, id2 = pair 
    if id1 < id2:
        a = id1
        b = id2
    else: 
        a = id2
        b = id1
    antenna_map[(a, b)] = 0

# print antenna_map

def vote(id1, id2):
    if id1 < id2:
        a = id1
        b = id2
    else: 
        a = id2
        b = id1
    antenna_map[(a, b)] += 1


data = data[data['count'] > 200]
byItem = data.groupby(['item_number', 'serial_number']) # , 'antenna_id'])
for name, group in byItem:
    if len(group['item_number']) > 0:
        # print name 
        # print group
        for pair in list(itools.combinations(list(set(group['antenna_id'])), 2)):
            a, b = pair
            vote(a, b)

for pair in pairs:
    id1, id2 = pair 
    if id1 < id2:
        a = id1
        b = id2
    else: 
        a = id2
        b = id1
    if antenna_map[(a, b)] >= 5:
        # print 'pair: (%d, %d) with %d connections' % (a, b, antenna_map[(a, b)])
        G.add_edge(a, b, weight=(1.0 / antenna_map[(a, b)]))
pickle.dump(antenna_map, "antenna_map.pickle")

pos = nx.graphviz_layout(G)

day = sys.argv[1].split(".")[0][-1]
title = "Relative map of antennas using counts > 200 and day %s data" %day
nx.draw_networkx(G, pos, title=title)
plt.axis('off')
plt.title(title)
plt.show()