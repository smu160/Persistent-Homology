"""
Here be dragons.
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
        self.simplices.sort()

    def k_chain_group(self, k):
        """Extract the kth chain group C_{k}

        For example, `C_{2} = <[1 2 3]>`

        Parameters
        ----------
        k: int
            The designation of the chain group.

        Returns
        -------
        list:
            The simplices of size k+1

        """
        return [simplex for simplex in self.simplices if len(simplex) == k+1]

    def boundary_operator(self, k):
        """Compute the coefficients of the simplices

        Parameters
        ----------
        k: int


        Returns
        -------
        matrix: dok_matrix

        """
        columns = self.k_chain_group(k)
        rows = self.k_chain_group(k-1)

        if not rows: # not target_simplices:
            matrix = dok_matrix((1, len(columns)))
            matrix[0, 0:len(columns)] = 1
        else:

            # len(rows) = m_{k}, i.e., the order of the basis that generates
            # C_{k}
            # len(columns) = m_{k-1}, i.e., the order of the basis that
            # generates C_{k-1}
            matrix = dok_matrix((len(rows), len(columns)), dtype=np.float32)

            # Create "labels" for the columns
            column_labels = {simplex: j for j, simplex in enumerate(columns)}

            # Create "labels" for the rows
            row_labels = {simplex: i for i, simplex in enumerate(rows)}

            for column in columns:
                for i, _ in enumerate(column):

                    # By the definition of the boundary operator, the current
                    # iteration should have v_{i} removed from the sequence
                    sequence = column[:i] + column[(i+1):]

                    row = row_labels[sequence]
                    col = column_labels[column]
                    matrix[row, col] = -1 if i % 2 == 1 else 1

        return matrix

    # TODO: Figure out why ValueError exception was needed
    def betti_number(self, k):

        # The matrix, M_{k}
        matrix_k = self.boundary_operator(k)

        # The matrix, M_{k+1}
        matrix_kpp = self.boundary_operator(k+1)

        if k == 0:
            rank_m_k = 0
        else:
            try:
                rank_m_k = np.linalg.matrix_rank(matrix_k.toarray())
            except (np.linalg.LinAlgError, ValueError):
                rank_m_k = matrix_k.shape[1]
        try:
            rank_m_kpp = np.linalg.matrix_rank(matrix_kpp.toarray())
        except (np.linalg.LinAlgError, ValueError):
            rank_m_kpp = matrix_kpp.shape[1]

        nullity_m_k = matrix_k.shape[1] - rank_m_k
        return nullity_m_k - rank_m_kpp


class VietorisRipsComplex(SimplicialComplex):

    def __init__(self, positions):
        super(VietorisRipsComplex, self).__init__(positions)

        self.pos_to_node = {tuple(pos): node for node, pos in enumerate(positions)}
        self.network = self.construct_network(positions)
        self.update_simplices()

    def construct_network(self, positions):
        """Builds a NetworkX graph from datapoint positions

        Parameters
        ----------
        positions: list
            A list of 2-tuples, where each 2-tuple represents a datapoint.

        Returns
        -------
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

    def update_simplices(self):
        self.import_simplices(nx.enumerate_all_cliques(self.network))
