import os
from xml.etree import ElementTree as xml

MAVEN_NAMESPACES = {
    'mvn': 'http://maven.apache.org/POM/4.0.0',
}


def parse_maven_module_from_pom(pom_path):
    """
    Returns a MavenModule instance from
    :param pom_path: Absolute path to the pom.xml file. Provided as a string.
    :return: A MavenModule instance build upon the pom.xml file.
    """
    pom = xml.parse(pom_path)

    group_id, artifact_id = parse_artifact_ids_from_pom(pom)

    if not group_id:
        raise Exception('Missing groupId')

    if not artifact_id:
        raise Exception('Missing artifactId')

    # maven_module = NewMavenModule(pom_path, group_id, artifact_id)

    # parent_group_id, parent_artifact_id = parse_parent_artifact_ids_from_project_node(pom.getroot())
    # if(not parent_artifact_id is None):
    #     if(parent_group_id is None):
    #         raise Exception('Missing parent groupId')
    #     maven_module.parent = NewMavenModule(None, parent_group_id, parent_artifact_id)
    #
    # maven_module.dependencies.update(parse_dependencies_from_pom(pom))

    #return maven_module
    return group_id, artifact_id


def parse_sub_modules(pom_path):
    """
    Given a pom.xml path, parses the xml and extracts the modules.
    :param pom_path: The path to the pom.xm lfile.
    :return: Yields the modules as MavenModule instances.
    """
    pom = xml.parse(pom_path)
    for sub_module in pom.findall('mvn:modules/mvn:module', MAVEN_NAMESPACES):
        sub_pom_path = os.path.join(os.path.dirname(pom_path), sub_module.text, 'pom.xml')
        yield parse_maven_module_from_pom(sub_pom_path)


# import tempfile
# import subprocess


def build_dependencies_from_pom_path(pom_path):#, maven_home):
    # Extracting all the dependencies from pom
    pom = xml.parse(pom_path)
    dependency_nodes = pom.findall('mvn:dependencies/mvn:dependency', MAVEN_NAMESPACES)
    for dependency_node in dependency_nodes:
        dep_group_id, dep_artifact_id = parse_artifact_ids_from_node(dependency_node)
        yield  dep_group_id, dep_artifact_id
    # # These dependency nodes may lack versions, so we'll compute the effective pom for this
    # mvn = os.path.join(maven_home, "bin/mvn")
    # mvn_settings = os.path.join(maven_home, "conf/settins.xml")
    # effective_pom_path = tempfile.NamedTemporaryFile(prefix = "mvn-graph-builder-", delete = True)
    # cmd_line = mvn, "--quiet", "--settings", mvn_settings, "-Doutput=" + effective_pom_path.name, "-f", pom_path
    # error_code = subprocess.call(cmd_line)
    # # FIXME Check error_code
    # effective_pom = xml.parse(effective_pom_path)
    # effective_dependency_nodes = effective_pom.findall('mvn:dependencies/mvn:dependency', MAVEN_NAMESPACES)
    # # Now I can ask my effective pom the effective version (if nor already there).
    # for dependency_node in dependency_nodes:
    #     group_id, artifact_id, version = parse_id_from_node(dependency_node)
    #     # FIXME Use XPATH ?
    #     if not version:
    #         group_id, artifact_id, version = parse_id_from_node(dependency_node)


def parse_artifact_ids_from_pom(pom):
    project_node = pom.getroot()

    group_id, artifact_id = parse_artifact_ids_from_node(project_node)

    if not group_id:
        parent_group_id, parent_artifact_id = parse_parent_artifact_ids_from_project_node(project_node)
        group_id = parent_group_id
    return group_id, artifact_id


def parse_parent_artifact_ids_from_project_node(project_node):
    """
    Retrieves the (groupId, artifactId) from the project node.
    :param project_node: The parsed xml project node.
    :return: (groupId, artifactId) of (None, None).
    """
    parent_nodes = project_node.findall('mvn:parent', MAVEN_NAMESPACES)
    assert(len(parent_nodes) in (0, 1))
    for parent_node in parent_nodes:
        group_id, artifact_id = parse_artifact_ids_from_node(parent_node)
        if group_id and artifact_id:
            return group_id, artifact_id
    return None, None


def parse_artifact_ids_from_node(node):
    """
    Given a parsed xml node, retrieves the (groupId, artifactId) information.
    :param node: The parsed xml node.
    :return: (groupId, artifactId)
    """
    return get_child_node_value(node, 'groupId'), get_child_node_value(node, 'artifactId')


def parse_packaging_from_project_node(project_node):
    """
    Returns the packaging of the pom.
    :param project_node: The xml parsed project node.
    :return: The packaging as a string.
    """
    packaging = get_child_node_value(project_node, "packaging")
    if not packaging:
        packaging = "jar"
    return packaging


def get_child_node_value(parent_node, child_node_name):
    for child_node in parent_node.findall('mvn:%s' % (child_node_name, ), MAVEN_NAMESPACES):
        return child_node.text
    return None

