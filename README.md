maven-tree - maven dependency tree graph builder
------------------------------------------------
Overview

maven-tree recurses through your maven projects and generates a graph from the declared dependencies, parent and modules.

Based on xml parsing, this code is a small hack for my specific needs (working on a huge spaghetti code) and does not pretend to a robust industrial code.

I've been using Gephi (http://gephi.github.io/) to explore the graph.

Hopefully it may help you.

------------------------------------------------------------------------
Requirements

maven-tree require the networkx python module.

For the moment it creates graphs in the gexf format.
But you may modify the code for any networkx supported format.