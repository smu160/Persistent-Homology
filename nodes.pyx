from libc.math cimport sqrt


cdef bint c_nodes_touching(double x1, double y1, double x2, double y2, double r1, double r2):
    """Checks if two nodes touch or intersect one another
    """
    return (r1 - r2)**2 <= (x1 - x2)**2 + (y1 - y2)**2 <= (r1 + r2)**2


def nodes_touching(x1, y1, x2, y2, r1, r2):
    """Checks if two nodes touch or intersect one another
    """
    return c_nodes_touching(x1, y1, x2, y2, r1, r2)


if __name__ == "__main__":
    pass
