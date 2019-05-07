"""
Experiments and tests
"""

__author__ = "Saveliy Yusufov, Helen Jin"
__date__ = "20 March 2019"
__license__ = "GPL"
__maintainer__ = "Saveliy Yusufov"
__email__ = "sy2685@columbia.edu"


import sys
import itertools
import threading
from multiprocessing import Queue

import numpy as np

from nodes import nodes_touching_3d
from homology import VietorisRipsComplex


def circle_point(radius, theta):
    """Generates a point on a circle using polar coordinates

    Parameters
    ----------
    radius: int
        The radius of the circle of interest.

    theta: float
        The angle from the pole.

    Returns
    -------
    point: tuple
        The x, y coordinates of a point on the circle of the given radius.
    """
    point = ((round(radius * np.cos(theta)), round(radius * np.sin(theta))))
    return point


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
    points = {circle_point(radius, theta) for theta in angles}
    return points


def torus_datapoint(theta, phi, Radius, radius):
    """Compute a point on a torus

    Use the parameterization of a torus to compute a point on the torus

    Parameters
    ----------
    theta: float
        A value in `[0, 2pi)` that represents the angle of the circle in the
        inner tube.

    phi: float
        A value in `[0, 2pi)` that represents the angle of the circle in the
        center of the torus.

    Radius: float
        The distance from the center of the tube to the center of the torus.

    radius: float
        The radius of the tube.

    Returns
    -------
    x, y, z: tuple
        A tuple that defines a point on a torus, parametrically.

    References
    ----------
    .. [1] Weisstein, Eric W. "Torus." From MathWorld--A Wolfram Web Resource.
           http://mathworld.wolfram.com/Torus.html
    """
    x = (Radius + radius*np.cos(theta)) * np.cos(phi)
    y = (Radius + radius*np.cos(theta)) * np.sin(phi)
    z = radius * np.sin(theta)
    return x, y, z

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

    points = {torus_datapoint(theta, phi, radius, tube_radius) for theta, phi in zip(angles1, angles2)}

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


def update_complex(v_rips_complex, value, queue):
    """Update as the value of epsilon changes

    Parameters
    ----------
    v_rips_complex: VietorisRipsComplex

    value: float
         The value of epsilon, i.e., the radius of the encompassing
         circle or sphere.
    """
    pos = list(v_rips_complex.pos_to_node.keys())
    value *= 0.1

    node_sizes = [0.2 for _ in pos]
    perim_node_sizes = [value] * len(pos)
    sizes = node_sizes + perim_node_sizes

    radius = value * 0.5
    for pos1, pos2 in itertools.combinations(pos, 2):
        node1 = v_rips_complex.pos_to_node[pos1]
        node2 = v_rips_complex.pos_to_node[pos2]

        if nodes_touching_3d(*pos1, *pos2, radius, radius):
            v_rips_complex.network.add_edge(node1, node2)
        elif v_rips_complex.network.has_edge(node1, node2):
            v_rips_complex.network.remove_edge(node1, node2)

    v_rips_complex.update_simplices()
    pos = np.array(pos * 2)

    betti_nums = [v_rips_complex.betti_number(i) for i in range(3)]

    queue.put((value, *betti_nums))


def listener(queue):
    """listens for messages on the q, writes to file"""
    print("Now listening for queue", file=sys.stderr)
    f = open("results.txt", 'w')

    while True:
        value = queue.get()
        f.write("{}, {}, {}, {}\n".format(*value))
        f.flush()

    f.close()


def write_to_file(B_0, B_1, B_2, value):
    """Writes the Betti numbers and epsilon value to a CSV file
    """
    with open("betti.txt", 'a') as data_file:
        data_file.write("{}, {}, {}, {}\n".format(B_0, B_1, B_2, value))


def main():
    """Run some experiments... yay..."""

    # torus example
    datapoints = points_on_torus(20, 15, size=30)
    print("amount of points generated: {}".format(len(datapoints)), file=sys.stderr)

    queue = Queue()
    listener_thread = threading.Thread(target=listener, args=(queue,))
    listener_thread.daemon = True
    listener_thread.start()

    v_rips_complex = VietorisRipsComplex(datapoints)

    any(update_complex(v_rips_complex, epsilon, queue) for epsilon in np.arange(0, 400))

    # small circle vs. 2 large circles example
    # datapoints = points_on_circle(5, size=15)

    # sphere vs. torus example
    # datapoints = points_on_sphere(10, size=15)

if __name__ == '__main__':
    main()
