import networkx as nx
import random
import sys
import getopt


def usage():
    print("main.py -o <output graph file> -n <number of nodes> -e <number of edges> -w <maximum weight> ")


def main(argv):
    probability = 0.5
    nodes = 0
    edges = 0
    max_weight = 0
    gritter_range = 0
    filename = None

    try:
        opts, args = getopt.getopt(argv, "o:n:e:w:")
        if not opts:
            usage()
            sys.exit()
    except getopt.GetoptError:
        usage()
        sys.exit()
    for opt, arg in opts:
        if opt == "-n":
            nodes = int(arg)
        elif opt == "-e":
            edges = int(arg)
        elif opt == "-w":
            max_weight = int(arg)
        elif opt == "-o":
            filename = arg

    graph = nx.connected_watts_strogatz_graph(nodes, edges, probability)
    for (u, v) in graph.edges:
        graph.edges[u, v]["weight"] = random.randint(1, max_weight)

    for (u, v) in graph.edges:
        needed_range = min(
            2 * (min(nx.astar_path_length(graph, 0, u), nx.astar_path_length(graph, 0, v)) + graph.edges[u, v]["weight"]),
            nx.astar_path_length(graph, 0, u) + nx.astar_path_length(graph, 0, v) + graph.edges[u, v]["weight"]
        )
        if needed_range > gritter_range:
            gritter_range = needed_range
    nx.write_weighted_edgelist(graph, filename, delimiter=",")
    print("minimal possible range:", gritter_range)


if __name__ == "__main__":
    main(sys.argv[1:])