import argparse

def main(args):
    maven_modules = find_maven_modules(args.maven_module_paths)

    graph = pygraphml.Graph()
    nodes_store = NodesStore(graph)

    DependencyGraphBuilder(graph, nodes_store).build_graph(maven_modules)

    if(args.include_parent_edges):
        ParentEdgeBuilder(graph, nodes_store).build_graph(maven_modules)

    write_graph(args.graph_output_path, graph)


def parse_args():
    parser = argparse.ArgumentParser(description='maven dependency tree graph builder')

    parser.add_argument('graph_output_path', metavar='GRAPH_OUTPUT_FILE', help='the generated graph is written to that file')

    parser.add_argument('maven_module_paths', metavar='MAVEN_MODULE_DIR', nargs='+', help='directories which will be recursively searched for pom.xml files')

    parser.add_argument('--include-parent-edges', dest='include_parent_edges', action='store_const', const=True, default=False, help='add a maven module\'s relation to it\'s parent module as edge in the graph (default: don\'t add them)')

    return parser.parse_args()



if __name__ == '__main__':
    args = parse_args()
    main(args)