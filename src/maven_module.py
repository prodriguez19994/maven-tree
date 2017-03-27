#!/usr/bin/python2

from xml.etree import ElementTree as xml

from pom_parsing import build_dependencies_from_pom_path, parse_sub_modules, parse_parent_artifact_ids_from_project_node


class MavenModule(object):

    def __init__(self, pom_path, group_id, artifact_id):
        self.pom_path = pom_path
        if pom_path:
            self.pom = xml.parse(pom_path)
        else:
            self.pom = None
        self.group_id = group_id
        self.artifact_id = artifact_id

    @property
    def id(self):
        """
        The maven module id is only based on the groupID and the artifactId.
        :return:
        """
        return self.group_id, self.artifact_id

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def parent(self):
        """
        Returns the maven parent project.
        :return: Returns the maven parent project as a MavenModule instance. Or None if no parent found.
        """
        group_id, artifact_id =  parse_parent_artifact_ids_from_project_node(self.pom.getroot())
        if group_id and artifact_id:
            return MavenModule(None, group_id, artifact_id)
        else:
            return None

    @property
    def dependencies(self):
        """
        Returns the direct dependencies as a set of MavenModule instances.
        :return: The set of dependencies.
        """
        tmp = map(lambda group_artifact_id: MavenModule(None, *group_artifact_id),
                  build_dependencies_from_pom_path(self.pom_path))
        return set(tmp)

    @property
    def sub_modules(self):
        """
        Returns the modules as a set of MavenModule instances.
        :return: The set of modules.
        """
        tmp = map(lambda group_artifact_id: MavenModule(None, *group_artifact_id),
                  parse_sub_modules(self.pom_path))
        return set(tmp)