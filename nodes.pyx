from libc.math cimport sqrt


cdef bint c_nodes_touching(double x1, double y1, double x2, double y2, double r1, double r2):
    """Checks if two nodes touch or intersect one another
    """
    return (r1 - r2)**2 <= (x1 - x2)**2 + (y1 - y2)**2 <= (r1 + r2)**2


def nodes_touching(x1, y1, x2, y2, r1, r2):
    """Checks if two nodes touch or intersect one another
    """
    return c_nodes_touching(x1, y1, x2, y2, r1, r2)


cdef bint c_nodes_touching_3d(double x1, double y1, double z1, double x2, double y2, double z2, double r1, double r2):
    """Checks if two nodes touch or intersect one another
    """
    return sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2) <= (r1 + r2)


def nodes_touching_3d(x1, y1, z1, x2, y2, z2, r1, r2):
    """Checks if two nodes touch or intersect one another, 3d version
    """
    return c_nodes_touching_3d(x1, y1, z1, x2, y2, z2, r1, r2)


if __name__ == "__main__":
    pass
