# degreeTwo.py
# Aakash Indurkhya
import numpy as np 
from matplotlib import pyplot as plt 
import pandas as pd 
import itertools as itools
import networkx as nx 
import sys
import pickle
from datetime import datetime
data = pd.read_csv(sys.argv[1])
antenna_map = {}
items_moving = {}
G = nx.Graph()
antennas = list(pd.unique(data['antenna_id']))
items = list(pd.unique(data['item_number']))

# Create graph by adding one vertex for each antenna
for a in antennas: 
	G.add_node(a)

# create a hash table value for each pair of antennas
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

# create hash table for each item
for i in items:
	items_moving[i] = 0

# print antenna_map

# vote takes in two antenna id's and increments the hash table value
# that is stored for that pair. 
def vote(id1, id2, val):
	if id1 < id2:
		a = id1
		b = id2
	else: 
		a = id2
		b = id1
	antenna_map[(a, b)] += val

def voteWeight(a, b):
	# print a
	# print b
	if abs(a - b) > 200:
		return abs(a-b)
	else: 
		return a

FMT = '%Y-%m-%d %H:%M:%S'
startOfDay = datetime.strptime('2015-02-13 00:00:00', FMT)
timeVar = []
# Read in and filter data
data = data[data['count'] > 200]
print data
byItem = data.groupby(['item_number', 'serial_number']) # , 'antenna_id'])
for name, group in byItem:
	if len(group['item_number']) > 4:
		# print name 
		# print group
		aid = list(group['antenna_id'])
		counts = list(group['count'])
		times = list(group['first_seen'])
		
		times = [(datetime.strptime(t, FMT) - startOfDay).seconds/3600.0 for t in times]
		timeVar.append(np.var(times))

		item = list(group['item_number'])[0]
		if np.var(times) > .2: 
			print item
			items_moving[item] += np.var(times)

		countVals = {}
		for i in range(len(aid)):
			countVals[aid[i]] = counts[i]

		# for valid pairs (associated with a single item), vote once
		for pair in list(itools.combinations(list(set(group['antenna_id'])), 2)):
			a, b = pair
			vote(a, b, voteWeight(countVals[a], countVals[b]))

print np.mean(timeVar)
timeVar = timeVar - np.mean(timeVar)
plt.hist(timeVar, bins=25)
plt.plot()
plt.show()


print items_moving

with open('moving_items.pickle', 'w') as f:
	pickle.dump(items_moving, f)

# add an edge for pairs with a high enough number of votes
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

# print pos

# # Display the network
# pos = nx.graphviz_layout(G)

# day = sys.argv[1].split(".")[0][-1]
# title = "Relative map of antennas using counts > 200 and day %s data" %day
# nx.draw_networkx(G, pos, title=title)
# plt.axis('off')
# plt.title(title)
# plt.show()