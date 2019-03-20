"""
The entrypoint into the Persistent Homology visualization program.
"""

__author__ = "Saveliy Yusufov, Helen Jin"
__date__ = "19 March 2019"
__license__ = "GPL"
__maintainer__ = "Saveliy Yusufov"
__email__ = "sy2685@columbia.edu"

import sys
import itertools

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np


class Slider(QWidget):

    def __init__(self, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.verticalLayout = QVBoxLayout(self)

        self.label = QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMaximum(500)

        self.horizontalLayout.addWidget(self.slider)
        spacerItem1 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.resize(self.sizeHint())

        self.slider.valueChanged.connect(self.setLabelValue)
        self.setLabelValue(self.slider.value())

    def setLabelValue(self, value):
        self.label.setText("epsilon: {}".format(round(value * 0.1, 1)))


class Graph:
    """A graph theory style graph to represent data points"""

    def __init__(self, nodes, edges, positions):
        self.nodes = {tuple(pos): node for node, pos in zip(nodes, positions)}
        self.edges = edges

    def add_edge(self, node_x, node_y):
        """Adds an edge between two given nodes in the graph
        """
        self.edges.add((node_x, node_y))

    def remove_edge(self, node_x, node_y):
        """Adds an edge between two given nodes in the graph
        """
        self.edges.discard((node_x, node_y))

    # TODO: Write in C and call it with ctypes
    def nodes_touching(self, x1, y1, x2, y2, r1, r2):
        """Checks if two nodes touch or intersect one another
        """
        return (r1 - r2)**2 <= (x1 - x2)**2 + (y1 - y2)**2 <= (r1 + r2)**2


class Widget(QWidget):

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent=parent)
        self.vertical_layout = QVBoxLayout(self)

        self.win = pg.GraphicsWindow()
        view_box = self.win.addViewBox()
        self.graph_item = pg.GraphItem()
        view_box.addItem(self.graph_item)

        self.vertical_layout.addWidget(self.win)

        self.w1 = Slider()
        self.vertical_layout.addWidget(self.w1)

        # The nodes of our graph (the set of data points)
        nodes = [node for node in range(20)]

        edges = set() # [[np.random.randint(0, 10), np.random.randint(0, 10)] for _ in range(40)]
        positions = [[np.random.randint(0, 50), np.random.randint(0, 50)] for _ in range(20)]

        self.graph = Graph(nodes, edges, positions)

        self.line_pen = pg.mkPen('g', width=3)
        self.node_brushes = [pg.mkBrush('r') for _ in positions]
        self.perim_nodes = [pg.mkBrush(color=(255, 165, 0, 40)) for _ in positions]
        self.brushes = self.node_brushes + self.perim_nodes
        self.node_sizes = [0.5 for _ in positions]

        # Define the symbol to use for each node (this is optional)
        self.symbols = ['o' for _, _ in self.graph.nodes.items()]

        self.update_graph(1)

        self.w1.slider.valueChanged.connect(self.update_graph)

    def update_graph(self, value):
        """Update the graph when the value of the slider changes

        Args:
            value: int
                The slider value/position that represents the diameter of the
                perimeter nodes.
        """
        pos = list(self.graph.nodes.keys())

        perim_node_sizes = [value * 0.1] * len(pos)
        sizes = self.node_sizes + perim_node_sizes

        radius = (value * 0.1) * 0.5
        for node1, node2 in itertools.combinations(pos, 2):
            x1 = node1[0]
            x2 = node2[0]
            y1 = node1[1]
            y2 = node2[1]
            if self.graph.nodes_touching(x1, y1, x2, y2, radius, radius):
                self.graph.add_edge(self.graph.nodes[node1], self.graph.nodes[node2])
                # print("{}, {} are touching".format(node1, node2), file=sys.stderr)
            else:
                # print("{}, {} are NOT touching".format(node1, node2), file=sys.stderr)
                self.graph.remove_edge(self.graph.nodes[node1], self.graph.nodes[node2])

        pos = np.array(pos*2)

        # Update the graph
        if self.graph.edges:
            adj = [list(edge) for edge in self.graph.edges]
            adj = np.array(adj)
            self.graph_item.setData(pos=pos, adj=adj, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)
        else:
            self.graph_item.setData(pos=pos, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)

        # print(self.graph.edges)

if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
