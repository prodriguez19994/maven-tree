class NodesStore(object):

    def __init__(self, graph):
        self.graph = graph
        self.maven_module_nodes = {}

    def get_maven_module_node(self, maven_module):
        if(maven_module in self.maven_module_nodes):
            return self.maven_module_nodes[maven_module]
        else:
            node_id = '%s:%s' % (maven_module.group_id, maven_module.artifact_id)
            maven_module_node = self.graph.add_node(node_id)

            self.maven_module_nodes[maven_module] = maven_module_node

            return maven_module_node


class GraphBuilder(object):

    def __init__(self, graph, nodes_store):
        self.graph = graph
        self.nodes_store = nodes_store

    def build_graph(self, maven_modules):
        for maven_module in maven_modules:
            maven_module_node = self.nodes_store.get_maven_module_node(maven_module)
            self.add_edges(maven_module)

        return self.graph

    @staticmethod
    def add_attribute(edge, value):
        raw_old_types = edge.attributes().get("type", None)
        if raw_old_types:
            old_types = set(raw_old_types.split(","))
        else:
            old_types = set()
        old_types.add(value)
        edge["type"] = ",".join(old_types)


class DependencyGraphBuilder(GraphBuilder):

    def __init__(self, graph, nodes_store):
        super(DependencyGraphBuilder, self).__init__(graph, nodes_store)

    def add_edges(self, maven_module):
        return self.add_dependency_edges(maven_module)

    def add_dependency_edges(self, maven_module):
        maven_module_node = self.nodes_store.get_maven_module_node(maven_module)

        for dependency_module in maven_module.dependencies:
            dependency_module_node = self.nodes_store.get_maven_module_node(dependency_module)

            edge = self.graph.add_edge(maven_module_node, dependency_module_node, directed = True)
            GraphBuilder.add_attribute(edge, "dependency")


class ModuleGraphBuilder(GraphBuilder):

    def __init__(self, graph, nodes_store):
        super(ModuleGraphBuilder, self).__init__(graph, nodes_store)

    def add_edges(self, maven_module):
        return self.add_modules_edges(maven_module)

    def add_modules_edges(self, maven_module):
        maven_module_node = self.nodes_store.get_maven_module_node(maven_module)

        for sub_module in maven_module.sub_modules:
            sub_module_node = self.nodes_store.get_maven_module_node(sub_module)

            edge = self.graph.add_edge(maven_module_node, sub_module_node, directed = True)
            GraphBuilder.add_attribute(edge, "module")


class ParentEdgeBuilder(GraphBuilder):

    def __init__(self, graph, nodes_store):
        super(ParentEdgeBuilder, self).__init__(graph, nodes_store)

    def build_graph(self, maven_modules):
        for maven_module in maven_modules:
            if maven_module.parent is None:
                continue

            maven_module_node = self.nodes_store.get_maven_module_node(maven_module)
            parent_module_node = self.nodes_store.get_maven_module_node(maven_module.parent)

            edge = self.graph.add_edge(maven_module_node, parent_module_node, directed = True)
            GraphBuilder.add_attribute(edge, "parent")
