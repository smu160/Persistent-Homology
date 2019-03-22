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
import multiprocessing

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np

from topology import VietorisRipsComplex, nodes_touching


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
        # nodes = [node for node in range(20)]

        positions = [[np.random.randint(0, 50), np.random.randint(0, 50)] for _ in range(20)]

        self.v_rips_complex = VietorisRipsComplex(positions, 1)

        self.line_pen = pg.mkPen('g', width=3)
        self.node_brushes = [pg.mkBrush('b') for _ in positions]
        self.perim_nodes = [pg.mkBrush(color=(255, 165, 0, 40)) for _ in positions]
        self.brushes = self.node_brushes + self.perim_nodes
        self.node_sizes = [0.5 for _ in positions]

        # Define the symbol to use for each node (this is optional)
        self.symbols = ['o'] * len(self.v_rips_complex.network.nodes)

        self.pool = multiprocessing.Pool(processes=4)
        self.update_graph(1)

        self.w1.slider.valueChanged.connect(self.update_graph)

    # TODO: fix leftover edges bug AND performance issues!
    def update_graph(self, value):
        """Update the graph when the value of the slider changes

        Args:
            value: int
                The slider value/position that represents the diameter of the
                perimeter nodes.
        """
        pos = list(self.v_rips_complex.pos_to_node.keys())

        perim_node_sizes = [value * 0.1] * len(pos)
        sizes = self.node_sizes + perim_node_sizes

        radius = (value * 0.1) * 0.5
        for node1, node2 in itertools.combinations(pos, 2):
            n1 = self.v_rips_complex.pos_to_node[node1]
            n2 = self.v_rips_complex.pos_to_node[node2]

            if nodes_touching(*node1, *node2, radius, radius):
                self.v_rips_complex.network.add_edge(n1, n2)
                # print("{}, {} are touching".format(node1, node2), file=sys.stderr)
            elif self.v_rips_complex.network.has_edge(n1, n2):
                self.v_rips_complex.network.remove_edge(n1, n2)
                # print("{}, {} are NOT touching".format(node1, node2), file=sys.stderr)

        self.v_rips_complex.update_simplices()
        pos = np.array(pos * 2)

        # Update the graph
        if self.v_rips_complex.network.edges:
            adj = np.array([list(edge) for edge in self.v_rips_complex.network.edges])
            self.graph_item.setData(pos=pos, adj=adj, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)
        else:
            self.graph_item.setData(pos=pos, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)

        # Compute
        betti_nums = self.pool.map(self.v_rips_complex.betti_number, range(3))
        print(betti_nums, file=sys.stderr)


if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
