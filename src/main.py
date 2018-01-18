import networkx as nx
import copy

UNVISITED_FACTOR = 1000
DISTANCE_FACTOR = 2

MAX = 13

graph = nx.read_weighted_edgelist('test.csv', delimiter=',', nodetype=int)
nx.set_node_attributes(
    graph,
    dict(zip(list(graph.nodes), [nx.astar_path_length(graph, 0, node) for node in graph.nodes])),
    'distance'
)


class Solution:
    def __init__(self):
        self.nodes = [0]
        self.cycle_length = 0
        self.cost = 0
        self.unvisited = nx.number_of_edges(graph)

    def function(self):
        return self.cost + self.unvisited * UNVISITED_FACTOR + graph.nodes[self.nodes[-1]]['distance'] * DISTANCE_FACTOR

    def add_node(self, node):
        weight = graph.edges[self.nodes[-1], node]['weight']
        if node == 0:
            self.cycle_length = 0
        else:
            self.cycle_length += weight
        self.cost += weight
        if not self.check_edge_existence(node, self.nodes[-1]):
            self.unvisited -= 1
        self.nodes.append(node)

    def remove_nodes(self, number_of_nodes):
        for i in range(number_of_nodes):
            self.cost -= graph.edges[self.nodes[-1], self.nodes[-2]]['weight']
            if not self.check_edge_existence(self.nodes.pop(), self.nodes[-1]):
                self.unvisited += 1
        if self.cycle_length == 0:
            return
        self.cycle_length = 0
        for i in reversed(range(1, len(self.nodes))):
            self.cycle_length += graph.edges[self.nodes[i], self.nodes[i - 1]]['weight']
            if self.nodes[i - 1] == 0:
                break

    def neighbourhood(self, radius=1):
        # neighbourhood = []
        # for node in nx.all_neighbors(graph, self.nodes[-1]):
        #     neighbour = copy.deepcopy(self)
        #     if neighbour.predict_cycle_length(node) <= MAX:
        #         neighbour.add_node(node)
        #         neighbourhood.append(neighbour)
        neighbourhood = self.recursive_neighbourhood(radius)
        if len(self.nodes) > radius:
            backwards = copy.deepcopy(self)
            backwards.remove_nodes(radius)
            neighbourhood.append(backwards)
        return neighbourhood

    def recursive_neighbourhood(self, radius):
        temp_neighbourhood = []
        for node in nx.all_neighbors(graph, self.nodes[-1]):
            neighbour = copy.deepcopy(self)
            if neighbour.predict_cycle_length(node) <= MAX:
                neighbour.add_node(node)
                temp_neighbourhood.append(neighbour)
        if radius == 1:
            return temp_neighbourhood
        neighbourhood = []
        for solution in temp_neighbourhood:
            neighbourhood += solution.recursive_neighbourhood(radius - 1)
        return neighbourhood

    def predict_cycle_length(self, next_node):
        return self.cycle_length + graph.edges[self.nodes[-1], next_node]['weight'] + graph.nodes[next_node]['distance']

    def check_edge_existence(self, first_node, second_node):
        for i in range(len(self.nodes) - 1):
            if first_node == self.nodes[i] and second_node == self.nodes[i + 1] or first_node == self.nodes[i + 1] and second_node == self.nodes[i]:
                return True
        return False

solution = Solution()
solution = solution.neighbourhood(2)[1]

for x in solution.neighbourhood(2):
    print(x.nodes, x.function())
