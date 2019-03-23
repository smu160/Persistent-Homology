"""
Here be dragons.

The SimplicialComplex class and the VietorisRipsComplex class are both heavily
based on code from the following source:

https://datawarrior.wordpress.com/2015/09/14/tda-2-constructing-connectivities/
"""

__author__ = "Saveliy Yusufov, Helen Jin"
__date__ = "20 March 2019"
__license__ = "GPL"
__maintainer__ = "Saveliy Yusufov"
__email__ = "sy2685@columbia.edu"

from itertools import combinations

import numpy as np
import networkx as nx
from scipy.sparse import dok_matrix


class SimplicialComplex:
    """Base class for Complexes"""

    def __init__(self, simplices=[]):
        self.import_simplices(simplices=simplices)

    def import_simplices(self, simplices=[]):
        self.simplices = [tuple(sorted(simplex)) for simplex in simplices]
        self.face_set = self.faces()

    # FIXME: this is ugly and inefficient
    def faces(self):
        faceset = set()
        for simplex in self.simplices:
            for i in range(len(simplex), 0, -1):
                for face in combinations(simplex, i):
                    faceset.add(face)

        return faceset

    def n_faces(self, n):
        return [face for face in self.face_set if len(face) == n+1]

    def boundary_operator(self, i):
        source_simplices = self.n_faces(i)
        target_simplices = self.n_faces(i - 1)

        if not target_simplices:
            matrix = dok_matrix((1, len(source_simplices)), dtype=np.float32)
            matrix[0, 0:len(source_simplices)] = 1
        else:
            source_simplices_dict = {source_simplice: j for j, source_simplice in enumerate(source_simplices)}
            target_simplices_dict = {target_simplice: k for k, target_simplice in enumerate(target_simplices)}

            matrix = dok_matrix((len(target_simplices), len(source_simplices)), dtype=np.float32)
            for source_simplex in source_simplices:
                for a, _ in enumerate(source_simplex):
                    target_simplex = source_simplex[:a] + source_simplex[(a+1):]
                    i = target_simplices_dict[target_simplex]
                    j = source_simplices_dict[source_simplex]
                    matrix[i, j] = -1 if a % 2 == 1 else 1

        return matrix

    # TODO: Figure out why ValueError exception was needed
    def betti_number(self, i):
        boundop_i = self.boundary_operator(i)
        boundop_ip1 = self.boundary_operator(i+1)

        if i == 0:
            boundop_i_rank = 0
        else:
            try:
                boundop_i_rank = np.linalg.matrix_rank(boundop_i.toarray())
            except (np.linalg.LinAlgError, ValueError):
                boundop_i_rank = boundop_i.shape[1]
        try:
            boundop_ip1_rank = np.linalg.matrix_rank(boundop_ip1.toarray())
        except (np.linalg.LinAlgError, ValueError):
            boundop_ip1_rank = boundop_ip1.shape[1]

        return (boundop_i.shape[1] - boundop_i_rank) - boundop_ip1_rank


class VietorisRipsComplex(SimplicialComplex):

    def __init__(self, positions):
        super(VietorisRipsComplex, self).__init__(positions)

        self.pos_to_node = {tuple(pos): node for node, pos in enumerate(positions)}
        self.network = self.construct_network(positions)
        self.update_simplices()

    def construct_network(self, positions):
        """Builds a NetworkX graph from datapoint positions

        Args:
            positions: list
                A list of 2-tuples, where each 2-tuple represents a datapoint.

        Returns:
            graph: NetworkX Graph
                A graph of isolate nodes representing the datapoint positions.
        """
        graph = nx.Graph()
        nodes = [node for node, _ in enumerate(positions)]
        graph.add_nodes_from(nodes)
        return graph

    def add_edge(self, node_x, node_y):
        """Adds an edge between two given nodes in the graph
        """
        self.network.add_edge(node_x, node_y)

    def remove_edge(self, node_x, node_y):
        """Adds an edge between two given nodes in the graph
        """
        self.network.remove_edge(node_x, node_y)

    # TODO: figure out whether we need maximal cliques or all cliques
    def update_simplices(self):
        self.import_simplices(nx.find_cliques(self.network))


def nodes_touching(x1, y1, x2, y2, r1, r2):
    """Checks if two nodes touch or intersect one another
    """
    return (r1 - r2)**2 <= (x1 - x2)**2 + (y1 - y2)**2 <= (r1 + r2)**2
