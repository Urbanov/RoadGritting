import networkx as nx
import csv

edgeList = []

with open('test.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        edgeList.append([int(x) for x in row])

Graph = nx.Graph()

for edge in edgeList:
    Graph.add_edge(edge[0], edge[1], object=edge[2])

print(Graph.edges)



