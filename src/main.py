import networkx as nx
import csv

edgeList = []
Graph = nx.Graph()

with open('test.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        Graph.add_edge(int(row[0]), int(row[1]), object=int(row[2]))




