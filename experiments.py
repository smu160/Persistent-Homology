"""
Our experiments!
"""

__author__ = "Saveliy Yusufov, Helen Jin"
__date__ = "20 March 2019"
__license__ = "GPL"
__maintainer__ = "Saveliy Yusufov"
__email__ = "sy2685@columbia.edu"


import sys
import itertools
import numpy as np

from topology import VietorisRipsComplex
from nodes import nodes_touching_3d


def points_on_circle(radius, size=10):
    """Draws random points from the circumference of a circle

    NOTE: If duplicate points are generated, they will not be included.

    Parameters
    ----------
    radius: int
        The radius of the circle of interest.

    size: int, optional, default: 10
        The amount of points to randomly draw from the circle.
        NOTE: the length of the generated set of points may be less than
        size since duplicates are not allowed in sets.

    Returns
    -------
    points: set
        A set of points on a circle of the given radius.
    """
    angles = [np.random.uniform(0, 2*np.pi) for _ in range(size)]
    points = {(round(radius * np.cos(theta)), round(radius * np.sin(theta))) for theta in angles}
    return points


def points_on_torus(radius, tube_radius, size=10):
    """Draws random points from the circumferences of the two circles of a torus

    NOTE: If duplicate points are generated, they will not be included.
    
    Parameters
    ----------
    radius: int
        The radius of the first circle of the torus of interest.
    tube_radius: int
        The radius of the second circle (tube) of the torus of interest.
    size: int, optional, default: 10
        The amount of points to randomly draw from the torus.
        NOTE: the length of the generated set of points may be less than
        size since duplicates are not allowed in sets.
    Returns
    -------
    points: set
        A set of points on a torus of the given radii
    """
    angles1 = [np.random.uniform(0, 2*np.pi) for _ in range(size)]
    angles2 = [np.random.uniform(0, 2*np.pi) for _ in range(size)]

    points = {(round((tube_radius + radius * np.cos(theta)) * np.cos(phi)), 
                round((tube_radius + radius * np.cos(theta)) * np.sin(phi)),
                round(radius * np.sin(theta)))
                for theta, phi in zip(angles1, angles2)}

    return points


def points_on_sphere(radius, size=10):
    """Draws random points from a sphere

    NOTE: If duplicate points are generated, they will not be included.

    Parameters
    ----------
    radius: int
        The radius of the sphere of interest.

    size: int, optional, default: 10
        The amount of points to randomly draw from the sphere.
        NOTE: the length of the generated set of points may be less than
        size since duplicates are not allowed in sets.

    Returns
    -------
    points: set
        A set of points on a sphere of the given radius.
    """
    angles1 = [np.random.uniform(0, 2*np.pi) for _ in range(size)]
    angles2 = [np.random.uniform(0, 2*np.pi) for _ in range(size)]

    points = {(round(radius * np.cos(theta) * np.sin(phi)),
                round(radius * np.sin(theta) * np.sin(phi)),
                round(radius * np.cos(phi))) 
                for theta, phi in zip(angles1, angles2)}

    return points


def update_complex(positions, value):
    """Update as the value of epsilon changes

    Parameters
    ----------
    positions: set
        A set of points

    value: int
        value of epsilon
    """
    v_rips_complex = VietorisRipsComplex(positions)

    pos = list(v_rips_complex.pos_to_node.keys())

    node_sizes = [0.2 for _ in positions]
    perim_node_sizes = [value * 0.1] * len(pos)
    sizes = node_sizes + perim_node_sizes

    radius = (value * 0.1) * 0.5
    for pos1, pos2 in itertools.combinations(pos, 2):
        node1 = v_rips_complex.pos_to_node[pos1]
        node2 = v_rips_complex.pos_to_node[pos2]

        if nodes_touching_3d(*pos1, *pos2, radius, radius):
            v_rips_complex.network.add_edge(node1, node2)
            # print("{}, {} are touching".format(node1, node2), file=sys.stderr)
        elif v_rips_complex.network.has_edge(node1, node2):
            v_rips_complex.network.remove_edge(node1, node2)
            # print("{}, {} are NOT touching".format(node1, node2), file=sys.stderr)

    v_rips_complex.update_simplices()
    pos = np.array(pos * 2)

    betti_nums = [v_rips_complex.betti_number(i) for i in range(3)]
    print(betti_nums, file=sys.stderr)



def main():
    #circle example --> see main.py

    # torus example
    datapoints = points_on_torus(30, 10, size=20)
    print("amount of points generated: {}".format(len(datapoints)), file=sys.stderr)

    for epsilon in np.arange(0, 450, 0.1):
        update_complex(datapoints, epsilon)

    # small circle vs. 2 large circles example
    datapoints = points_on_circle(5, size=15)


    # sphere vs. torus example
    datapoints = points_on_sphere(10, size=15)

if __name__ == '__main__':
    main()
