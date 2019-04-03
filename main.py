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

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np

from topology import VietorisRipsComplex
from nodes import nodes_touching


class Communicate(QtCore.QObject):
    update_simplices = QtCore.pyqtSignal()


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
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMaximum(200)

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

    def __init__(self, positions, parent=None):
        super(Widget, self).__init__(parent=parent)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(80, 80, 80))
        self.setPalette(p)

        self.vertical_layout = QVBoxLayout(self)

        self.win = pg.GraphicsWindow()
        view_box = self.win.addViewBox()
        self.graph_item = pg.GraphItem()
        view_box.addItem(self.graph_item)

        self.vertical_layout.addWidget(self.win)

        self.w1 = Slider()
        self.vertical_layout.addWidget(self.w1)

        self.v_rips_complex = VietorisRipsComplex(positions)

        self.line_pen = pg.mkPen('g', width=3)
        self.node_brushes = [pg.mkBrush('b') for _ in positions]
        self.perim_nodes = [pg.mkBrush(color=(255, 165, 0, 40)) for _ in positions]
        self.brushes = self.node_brushes + self.perim_nodes
        self.node_sizes = [0.2 for _ in positions]

        # Define the symbol to use for each node (this is optional)
        self.symbols = ['o'] * len(self.v_rips_complex.network.nodes)

        self.communicate = Communicate()
        self.communicate.update_simplices.connect(self.update_simplices)
        self.w1.slider.valueChanged.connect(self.update_graph)

        # self.pool = multiprocessing.Pool(processes=3)
        self.update_graph(1)

    def update_simplices(self):
        self.v_rips_complex.update_simplices()

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
        for pos1, pos2 in itertools.combinations(pos, 2):
            node1 = self.v_rips_complex.pos_to_node[pos1]
            node2 = self.v_rips_complex.pos_to_node[pos2]

            if nodes_touching(*pos1, *pos2, radius, radius):
                self.v_rips_complex.network.add_edge(node1, node2)
                # print("{}, {} are touching".format(node1, node2), file=sys.stderr)
            elif self.v_rips_complex.network.has_edge(node1, node2):
                self.v_rips_complex.network.remove_edge(node1, node2)
                # print("{}, {} are NOT touching".format(node1, node2), file=sys.stderr)

        self.communicate.update_simplices.emit()
        pos = np.array(pos * 2)

        # Update the graph
        if self.v_rips_complex.network.edges:
            adj = np.array([list(edge) for edge in self.v_rips_complex.network.edges])
            self.graph_item.setData(pos=pos, adj=adj, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)
        else:
            self.graph_item.setData(pos=pos, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)

        # betti_nums = self.pool.map(self.v_rips_complex.betti_number, range(3))
        betti_nums = [self.v_rips_complex.betti_number(i) for i in range(3)]
        print(betti_nums, file=sys.stderr)


def points_on_circle(radius, size=10):
    """Draws random points from the circumference of a circle

    NOTE: If duplicate points are generated, they will not be included.

    Args:
        radius: int
            The radius of the circle of interest.

        size: int, optional, default: 10
            The amount of points to randomly draw from the circle.
            NOTE: the length of the generated set of points may be less than
            size since duplicates are not allowed in sets.

    Returns:
        points: set
            A set of points on a circle of the given radius.
    """
    angles = [np.random.uniform(0, 2*np.pi) for _ in range(size)]
    points = {(round(radius * np.cos(theta)), round(radius * np.sin(theta))) for theta in angles}
    return points


def main():
    """Starts the GUI with some test datapoints"""
    pg.setConfigOption("background", 'w')
    pg.setConfigOption("foreground", 'k')

    # Generate datapoints
    datapoints = points_on_circle(10, size=15)
    print("amount of points generated: {}".format(len(datapoints)), file=sys.stderr)
    # datapoints = [[np.random.randint(0, 50), np.random.randint(0, 50)] for _ in range(10)]

    app = QApplication(sys.argv)
    w = Widget(datapoints)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
