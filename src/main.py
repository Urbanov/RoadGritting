import networkx as nx
import copy
import sys
import getopt
import matplotlib.pyplot as plt
from timeit import default_timer as timer

UNVISITED_FACTOR = 1000
DISTANCE_FACTOR = 1.1


class Solution:
    def __init__(self, graph, gritter_range):
        self.graph = graph
        self.nodes = [0]
        self.cycle_length = 0
        self.cost = 0
        self.unvisited = nx.number_of_edges(self.graph)
        self.gritter_range = gritter_range

    def function(self):
        return self.cost + self.unvisited * UNVISITED_FACTOR + self.graph.nodes[self.nodes[-1]]["distance"] * DISTANCE_FACTOR

    def add_node(self, node):
        weight = self.graph.edges[self.nodes[-1], node]["weight"]
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
            self.cost -= self.graph.edges[self.nodes[-1], self.nodes[-2]]["weight"]
            if not self.check_edge_existence(self.nodes.pop(), self.nodes[-1]):
                self.unvisited += 1
        self.cycle_length = 0
        if self.nodes[-1] == 0:
            return
        for i in reversed(range(1, len(self.nodes))):
            self.cycle_length += self.graph.edges[self.nodes[i], self.nodes[i - 1]]["weight"]
            if self.nodes[i - 1] == 0:
                break

    def neighbourhood(self, radius=1):
        neighbourhood = self.recursive_neighbourhood(radius)
        if len(self.nodes) > radius:
            back = copy.deepcopy(self)
            back.remove_nodes(radius)
            neighbourhood.append(back)
        return neighbourhood

    def recursive_neighbourhood(self, radius):
        direct_neighbourhood = []
        for node in nx.all_neighbors(self.graph, self.nodes[-1]):
            neighbour = copy.deepcopy(self)
            if neighbour.predict_cycle_length(node) <= self.gritter_range:
                neighbour.add_node(node)
                direct_neighbourhood.append(neighbour)
        if radius == 1:
            return direct_neighbourhood
        neighbourhood = []
        for neighbour in direct_neighbourhood:
            neighbourhood += neighbour.recursive_neighbourhood(radius - 1)
        return neighbourhood

    def predict_cycle_length(self, next_node):
        return self.cycle_length + self.graph.edges[self.nodes[-1], next_node]["weight"] + self.graph.nodes[next_node]["distance"]

    def check_edge_existence(self, first_node, second_node):
        for i in range(len(self.nodes) - 1):
            if sorted([first_node, second_node]) == sorted([self.nodes[i], self.nodes[i + 1]]):
                return True
        return False

    def last_node(self):
        return self.nodes[-1]

    def penultimate_node(self):
        return self.nodes[-2]

    def in_base(self):
        return self.last_node() == 0

    def cleared(self):
        return self.unvisited == 0


class Tabu:
    def __init__(self, graph, gritter_range):
        self.global_tabu = [0]
        self.local_tabu = []
        for i in range(nx.number_of_nodes(graph)):
            self.local_tabu.append([])
        self.current_solution = Solution(graph, gritter_range)
        self.best_solution = self.current_solution

    def run(self):
        while not self.stop_condition():
            # select best solution from neighbourhood
            self.current_solution = self.select_best()
            self.insert_into_global_tabu(self.current_solution.last_node())
            self.insert_into_local_tabu(self.current_solution.penultimate_node(), self.current_solution.last_node())
            if self.current_solution.function() < self.best_solution.function():
                # clear global tabu
                self.global_tabu = []
                self.best_solution = self.current_solution
                if self.best_solution.in_base():
                    # in base after successful cycle
                    self.successful_cycle()
            elif self.current_solution.in_base():
                # in base after coming back from unsuccessful cycle
                self.unsuccessful_cycle()
        return self.best_solution

    def stop_condition(self):
        return self.best_solution.cleared() and self.best_solution.in_base()

    def select_best(self):
        neighbourhood = self.current_solution.neighbourhood()
        if len(neighbourhood) == 1 or len(neighbourhood[-1].nodes) == len(neighbourhood[-2].nodes):
            sorted_list = sorted(neighbourhood, key=lambda obj: obj.function())
        else:
            # ignore shorter neighbour if exists
            sorted_list = sorted(neighbourhood[:-1], key=lambda obj: obj.function())
        for candidate in sorted_list:
            if candidate.function() < self.best_solution.function():
                # allow coming back to base
                self.remove_from_global_tabu(0)
            elif candidate.function() > self.best_solution.function():
                # disallow coming back to base
                self.insert_into_global_tabu(0)
            if candidate.last_node() not in self.local_tabu[candidate.penultimate_node()] and candidate.last_node() not in self.global_tabu:
                return candidate
        else:
            # break the tabu
            if sorted_list[0].function() < self.best_solution.function():
                # try to get back to base even if its against local tabu
                return sorted_list[0]
            # go back, cannot continue in current branch
            self.remove_from_global_tabu(self.current_solution.last_node())
            self.clear_local_tabu_for(self.current_solution.last_node())
            return neighbourhood[-1]

    def successful_cycle(self):
        for local_tabu in self.local_tabu:
            del local_tabu[:]
        self.global_tabu = []
        self.insert_into_global_tabu(0)

    def unsuccessful_cycle(self):
        for local_tabu in self.local_tabu[1:]:
            del local_tabu[:]

    def insert_into_local_tabu(self, node, tabu_node):
        if tabu_node not in self.local_tabu[node]:
            self.local_tabu[node].append(tabu_node)

    def clear_local_tabu_for(self, node):
        self.local_tabu[node] = []

    def insert_into_global_tabu(self, node):
        if node not in self.global_tabu:
            self.global_tabu.append(node)

    def remove_from_global_tabu(self, node):
        if node in self.global_tabu:
            self.global_tabu.remove(node)


class VNS:
    def __init__(self, graph, gritter_range):
        self.radius = 1
        self.current_solution = Solution(graph, gritter_range)
        self.best_solution = self.current_solution

    def run(self):
        while not self.stop_condition():
            self.radius = 1
            while True:
                self.current_solution = self.select_best()
                if self.current_solution.function() < self.best_solution.function():
                    self.best_solution = self.current_solution
                    break
                self.radius += 1
        return self.best_solution

    def stop_condition(self):
        return self.best_solution.cleared() and self.best_solution.in_base()

    def select_best(self):
        return sorted(self.current_solution.neighbourhood(self.radius), key=lambda obj: obj.function())[0]


def usage():
    print("main.py"
          " -i <input graph file>"
          " -r <gritter range>"
          " -h <tabu/vns>"
          " -d <show const and list of nodes>"
          " -v <show visual representation>"
          " -t <perform timed run>")


def full_screen():
    manager = plt.get_current_fig_manager()
    try:
        manager.window.showMaximized()
    except AttributeError:
        pass
    try:
        manager.resize(*manager.window.maxsize())
    except AttributeError:
        pass
    try:
        manager.frame.Maximize(True)
    except AttributeError:
        pass


def main(argv):
    filename = None
    gritter_range = None
    heuristic = None
    show_graph = False
    show_data = False
    timed_run = False

    try:
        opts, args = getopt.getopt(argv, "i:r:h:dvt")
        if not opts:
            usage()
            sys.exit()
    except getopt.GetoptError:
        usage()
        sys.exit()
    for opt, arg in opts:
        if opt == "-i":
            filename = arg
        elif opt == "-r":
            gritter_range = float(arg)
        elif opt == "-h":
            heuristic = arg
        elif opt == "-v":
            show_graph = True
        elif opt == "-d":
            show_data = True
        elif opt == "-t":
            timed_run = True

    graph = nx.read_weighted_edgelist(filename, delimiter=',', nodetype=int)
    nx.set_node_attributes(
        graph,
        dict(zip(list(graph.nodes), [nx.astar_path_length(graph, 0, node) for node in graph.nodes])),
        "distance")

    search = None
    if heuristic == "vns":
        search = VNS(graph, gritter_range)
    elif heuristic == "tabu":
        search = Tabu(graph, gritter_range)
    start = timer()
    result = search.run()
    end = timer()

    if show_data:
        print("\nfound solution: ", result.nodes)
        print("\ncost: ", result.function())

    if timed_run:
        print("\nelapsed:", end - start)

    if show_graph:
        node_list = result.nodes
        cycles = []
        current_cycle = []
        for i in range(1, len(node_list)):
            current_cycle.append((node_list[i - 1], node_list[i]))
            if node_list[i] == 0:
                cycles.append(current_cycle)
                current_cycle = []

        unvisited = list(graph.edges)
        for index, cycle in enumerate(cycles):
            nx.draw_networkx_nodes(graph, pos=nx.circular_layout(graph))
            nx.draw_networkx_nodes(graph, pos=nx.circular_layout(graph), nodelist=[0], node_color='b')
            nx.draw_networkx_edge_labels(graph, pos=nx.circular_layout(graph), edge_labels=nx.get_edge_attributes(graph, "weight"))
            unvisited = [edge for edge in unvisited if tuple(sorted(edge)) not in cycle and tuple(reversed(sorted(edge))) not in cycle]
            nx.draw_networkx_edges(graph, pos=nx.circular_layout(graph), edgelist=unvisited, width=5)
            nx.draw_networkx_edges(graph, pos=nx.circular_layout(graph), edgelist=cycle, width=5, edge_color='y')
            full_screen()
            plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
