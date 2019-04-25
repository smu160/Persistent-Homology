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

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np

from topology import VietorisRipsComplex
from nodes import nodes_touching
from experiments import points_on_circle


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
        p.setColor(self.backgroundRole(), QtGui.QColor(100, 100, 100))
        self.setPalette(p)

        self.vertical_layout = QVBoxLayout(self)

        self.win = pg.GraphicsWindow()
        view_box = self.win.addViewBox()
        self.graph_item = pg.GraphItem()
        view_box.addItem(self.graph_item)

        self.vertical_layout.addWidget(self.win)

        self.eps_slider = Slider()
        self.vertical_layout.addWidget(self.eps_slider)

        self.v_rips_complex = VietorisRipsComplex(positions)

        self.line_pen = pg.mkPen((238, 130, 238), width=3)
        self.node_brushes = [pg.mkBrush('k') for _ in positions]
        self.perim_nodes = [pg.mkBrush(color=(255, 165, 0, 40)) for _ in positions]
        self.brushes = self.node_brushes + self.perim_nodes
        self.node_sizes = [0.2 for _ in positions]

        # Define the symbol to use for each node (this is optional)
        self.symbols = ['o'] * len(self.v_rips_complex.network.nodes)

        self.communicate = Communicate()
        self.communicate.update_simplices.connect(self.update_simplices)
        self.eps_slider.slider.valueChanged.connect(self.update_graph)

        self.update_graph(1)

    def update_simplices(self):
        self.v_rips_complex.update_simplices()

    # TODO: fix leftover edges bug!!
    def update_graph(self, value):
        """Update the graph when the value of the slider changes

        Parameters
        ----------
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

        # Update the graph visualization
        if self.v_rips_complex.network.edges:
            adj = np.array([list(edge) for edge in self.v_rips_complex.network.edges])
            self.graph_item.setData(pos=pos, adj=adj, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)
        else:
            self.graph_item.setData(pos=pos, pen=self.line_pen, size=sizes, symbol=self.symbols*2, pxMode=False, symbolBrush=self.brushes)

        betti_nums = [self.v_rips_complex.betti_number(i) for i in range(3)]
        print(betti_nums, file=sys.stderr)



def main():
    # circle example with GUI
    """Starts the GUI with some test datapoints"""
    pg.setConfigOption("background", 'w')
    pg.setConfigOption("foreground", 'k')

    # Generate datapoints
    datapoints = points_on_circle(10, size=15)
    print("amount of points generated: {}".format(len(datapoints)), file=sys.stderr)

    app = QApplication(sys.argv)
    w = Widget(datapoints)
    w.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
