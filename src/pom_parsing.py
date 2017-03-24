from xml.etree import ElementTree as xml


def parse_maven_module_from_pom(pom_path):
    """
    Returns a MavenModule instance from
    :param pom_path: Absolute path to the pom.xml file. Provided as a string.
    :return: A MavenModule instance build upon the pom.xml file.
    """
    pom = xml.parse(pom_path)

    group_id, artifact_id = parse_artifact_ids_from_pom(pom)

    if(group_id is None):
        raise Exception('Missing groupId')

    if(artifact_id is None):
        raise Exception('Missing artifactId')

    maven_module = MavenModule(group_id, artifact_id)

    parent_group_id, parent_artifact_id = parse_parent_artifact_ids_from_project_node(pom.getroot())
    if(not parent_artifact_id is None):
        if(parent_group_id is None):
            raise Exception('Missing parent groupId')

        maven_module.parent = MavenModule(parent_group_id, parent_artifact_id)

    maven_module.dependencies.update(parse_dependencies_from_pom(pom))

    return maven_module


def parse_dependencies_from_pom(pom):
    for dependency_node in pom.findall('mvn:dependencies/mvn:dependency', MAVEN_NAMESPACES):
        dep_group_id, dep_artifact_id = parse_artifact_ids_from_node(dependency_node)

        yield MavenModule(dep_group_id, dep_artifact_id)


def parse_artifact_ids_from_pom(pom):
    project_node = pom.getroot()

    group_id, artifact_id = parse_artifact_ids_from_node(project_node)

    if(group_id is None):
        parent_group_id, parent_artifact_id = parse_parent_artifact_ids_from_project_node(project_node)

        group_id = parent_group_id

    return (group_id, artifact_id)


def parse_parent_artifact_ids_from_project_node(project_node):
    for parent_node in project_node.findall('mvn:parent', MAVEN_NAMESPACES):
        return parse_artifact_ids_from_node(parent_node)

    return (None, None)


def parse_artifact_ids_from_node(node):
    return (get_child_node_value(node, 'groupId'), get_child_node_value(node, 'artifactId'))


def get_child_node_value(parent_node, child_node_name):
    for child_node in parent_node.findall('mvn:%s' % (child_node_name, ), MAVEN_NAMESPACES):
        return child_node.text

    return None