import argparse
import os

import networkx

from maven_module import MavenModule
from graph_helpers import NodesStore, DependencyGraphBuilder, ParentEdgeBuilder, ModuleGraphBuilder
from pom_parsing import parse_maven_module_from_pom


def write_graph(graph, graph_output_path):
    """
    Writes the graph into a file.
    :param graph: The graph to be written.
    :param graph_output_path: The output file.
    :return: None
    """
    networkx.write_gexf(graph, graph_output_path)

def find_maven_modules(pom_root_paths):
    """
    Returns of all the maven modules found under pom_root_paths.
    :param pom_root_paths: An iterable over the absolute path of the root directory that contains our poms
                           (typically the root of our maven project).
    :return: An iterable with all the discovered maven modules as MavenModule instances.
    """
    maven_modules = []
    for pom_root_path in pom_root_paths:
        for current_dir_path, subdirs, files in os.walk(pom_root_path):
            if 'pom.xml' in files:
                pom_path = os.path.join(current_dir_path, 'pom.xml')
                group_id, artifact_id = parse_maven_module_from_pom(pom_path)
                maven_modules.append(MavenModule(pom_path, group_id, artifact_id))
    return maven_modules


def main(args):
    """
    The main process function.
    :param args: Argparse arguments
    :return: None
    """
    maven_modules = find_maven_modules(args.maven_module_paths)

    graph = networkx.DiGraph()
    nodes_store = NodesStore(graph)

    DependencyGraphBuilder(graph, nodes_store).build_graph(maven_modules)
    ParentEdgeBuilder(graph, nodes_store).build_graph(maven_modules)
    ModuleGraphBuilder(graph, nodes_store).build_graph(maven_modules)

    write_graph(graph, args.graph_output_path)


def parse_args():
    """
    Parses the command line arguments.
    :return: The arguments as an argpars structure.
    """
    parser = argparse.ArgumentParser(description = "Maven dependency tree graph builder.")

    parser.add_argument('graph_output_path', metavar='GRAPH_OUTPUT_FILE',
                        help='the generated graph is written to that file')

    parser.add_argument('maven_module_paths', metavar='MAVEN_MODULE_DIR', nargs='+',
                        help='directories which will be recursively searched for pom.xml files')

    # parser.add_argument('--include-parent-edges', dest='include_parent_edges', action='store_const', const=True,default=False,
    #                     help='add a maven module\'s relation to it\'s parent module as edge in the graph (default: don\'t add them)')

    # parser.add_argument('--maven-home', dest='maven_home', action="store", default="",
    #                     help='defines some maven home to compute the effective pom')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
