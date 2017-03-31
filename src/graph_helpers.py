PARENT = "parent"
MODULE = "module"
DEPENDENCY = "dependency"
PACKAGING_KEY_WORD = "packaging"
LINK_KEY_WORD = "linktype"
POM_KEY_WORD = "pom"


class NodesStore(object):

    def __init__(self, graph):
        self.graph = graph

    def get_maven_module_node_id(self, maven_module):
        """
        Returns the node identifier for maven_module
        :param maven_module: A MavenModule instance.
        :return: The identifier (i.e. the (group_id, artifact_id) tuple)) or an empty string if not found.
        """
        # Getting the (id, attributes) tuple
        nodes_data = self.graph.nodes(data = True)

        matching_nodes_data = filter(lambda nd: nd[0] == maven_module.id, nodes_data)
        if not matching_nodes_data:
            node_id = '%s:%s' % (maven_module.group_id, maven_module.artifact_id)
            attributes = {PACKAGING_KEY_WORD: maven_module.packaging,
                          POM_KEY_WORD: maven_module.pom_path}
            self.graph.add_node(node_id, attr_dict=attributes)
            return node_id
        elif len(matching_nodes_data) == 1:
            maven_node_data = matching_nodes_data[0]
            if not maven_node_data[1][PACKAGING_KEY_WORD]:
                maven_node_data[1][PACKAGING_KEY_WORD] = maven_module.packaging
            if not maven_node_data[1][POM_KEY_WORD]:
                maven_node_data[1][POM_KEY_WORD] = maven_module.pom_path
            return maven_node_data[0]
        else:
            return ""


class GraphBuilder(object):

    def __init__(self, graph, nodes_store):
        self.graph = graph
        self.nodes_store = nodes_store

    def build_graph(self, maven_modules):
        for maven_module in maven_modules:
            self.nodes_store.get_maven_module_node_id(maven_module)
            self.add_edges(maven_module)

        return self.graph

    @staticmethod
    def add_attribute(edge, value):
        raw_old_types = edge.attributes().get(LINK_KEY_WORD, None)
        if raw_old_types:
            old_types = set(raw_old_types.split(","))
        else:
            old_types = set()
        old_types.add(value)
        edge[LINK_KEY_WORD] = ",".join(old_types)


class DependencyGraphBuilder(GraphBuilder):

    def __init__(self, graph, nodes_store):
        super(DependencyGraphBuilder, self).__init__(graph, nodes_store)

    def add_edges(self, maven_module):
        maven_module_node_id = self.nodes_store.get_maven_module_node_id(maven_module)

        for dependency_module in maven_module.dependencies:
            dependency_module_node = self.nodes_store.get_maven_module_node_id(dependency_module)
            attributes = {LINK_KEY_WORD: DEPENDENCY}
            self.graph.add_edge(maven_module_node_id, dependency_module_node, attr_dict = attributes)


class ModuleGraphBuilder(GraphBuilder):

    def __init__(self, graph, nodes_store):
        super(ModuleGraphBuilder, self).__init__(graph, nodes_store)

    def add_edges(self, maven_module):
        maven_module_node_id = self.nodes_store.get_maven_module_node_id(maven_module)

        for sub_module in maven_module.sub_modules:
            sub_module_node = self.nodes_store.get_maven_module_node_id(sub_module)
            attributes = {LINK_KEY_WORD: MODULE}
            self.graph.add_edge(maven_module_node_id, sub_module_node, attr_dict = attributes)


class ParentEdgeBuilder(GraphBuilder):

    def __init__(self, graph, nodes_store):
        super(ParentEdgeBuilder, self).__init__(graph, nodes_store)

    def add_edges(self, maven_module):
        if not maven_module.parent:
            return

        maven_module_node_id = self.nodes_store.get_maven_module_node_id(maven_module)
        parent_module_node_id = self.nodes_store.get_maven_module_node_id(maven_module.parent)

        attributes = {LINK_KEY_WORD: PARENT}
        self.graph.add_edge(maven_module_node_id, parent_module_node_id, attr_dict = attributes)
