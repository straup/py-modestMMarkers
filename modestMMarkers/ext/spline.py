####################################################################

# THIS DOESN'T WORK YET.

# see also:

####################################################################

from sympy import solve, Symbol
from shapely.geometry import Point
from random import random
from decimal import Decimal
from math import sin, cos, pi

####################################################################

def splinify(points):

    funcs = []

    n = len(points)

    for i in range(len(points)):
        funcs.append(getfunc(points[i % n], points[(i + 1) % n], points[(i + 2) % n], points[(i + 3) % n]))

    steps = list(path(funcs, .02, False))
    return steps

####################################################################

def getfunc(p1, p2, p3, p4):
    """ Get a point-returning function for a cubic
        curve over four points, with domain [0 - 3].
    """
    # knowns
    points = p1, p2, p3, p4

    # unknowns
    a, b, c, d, e, f, g, h = [Symbol(n) for n in 'abcdefgh']

    # coefficients
    xco = solve([(a * i**3 + b * i**2 + c * i + d - p.x) for (i, p) in enumerate(points)], [a, b, c, d])
    yco = solve([(e * i**3 + f * i**2 + g * i + h - p.y) for (i, p) in enumerate(points)], [e, f, g, h])

    # shorter variable names
    a, b, c, d = [xco[n] for n in (a, b, c, d)]
    e, f, g, h = [yco[n] for n in (e, f, g, h)]

    def func(t, d1=False):
        """ Return a position for given t or velocity (1st derivative) if arg. is True.
        """
        if d1:
            # first derivative
            return Point(3 * a * t**2 + 2 * b * t + c,
                         3 * e * t**2 + 2 * f * t + g)

        else:
            # actual function
            return Point(a * t**3 + b * t**2 + c * t + d,
                         e * t**3 + f * t**2 + g * t + h)

    return func

####################################################################

def frange(start, stop, step):
    """ Generate floating-point values.
    """
    # use decimals internally to compensate for floating point accuracy
    i, stop, step = [Decimal('%.8f' % s) for s in (start, stop, step)]

    # fudge the stop, thanks floating point precision!
    while i <= stop:
        yield float(i)
        i += step

####################################################################

def path(funcs, step, open):
    """ Generate points over a series of functions.
    """
    for i in range(len(funcs) + 2):
        if open and i == 0:
            # first segment
            for t in frange(0, 1-step, step):
                p = funcs[0](t)
                yield p

        elif open and i == 1 and i < len(funcs):
            # second segment
            f1, f2 = funcs[0], funcs[1]
            for t in frange(0, 1-step, step):
                p1, p2 = f1(t + 1), f2(t)
                c1, c2 = (1 - t/2), t/2

                _t = pi * t / 2

                # starting to fall
                c1 = (1 + cos(_t)) / 2

                # next one
                c2 = (1 - cos(_t)) / 2

                x = p1.x * c1 + p2.x * c2
                y = p1.y * c1 + p2.y * c2
                yield Point(x, y)

        elif open and i == len(funcs):
            # second-to-last segment
            f1, f2 = funcs[-2], funcs[-1]
            for t in frange(1, 2-step, step):
                p1, p2 = f1(t + 1), f2(t)
                c1, c2 = (1 - t/2), t/2

                _t = pi * (t - 1) / 2

                # tail end
                c1 = (1 - sin(_t)) / 2

                # finishing rise
                c2 = (1 + sin(_t)) / 2

                x = p1.x * c1 + p2.x * c2
                y = p1.y * c1 + p2.y * c2
                yield Point(x, y)

        elif open and i == len(funcs) + 1:
            # last segment
            for t in frange(2, 3, step):
                p = funcs[-1](t)
                yield p

        else:
            # some middle segment
            n = len(funcs)
            f1, f2, f3 = funcs[(i - 2) % n], funcs[(i - 1) % n], funcs[i % n]
            for t in frange(0, 1-step, step):
                p1, p2, p3 = f1(t + 2), f2(t + 1), f3(t)
                c1, c2, c3 = (1 - t)/2, .5, t/2

                _t = pi * t / 2

                # tail end
                c1 = (1 - sin(_t)) / 2

                # middle bit
                c2a = cos(_t - pi/2)
                c2b = cos(_t)
                c2 = (c2a + c2b) / 2

                # next one
                c3 = (1 - cos(_t)) / 2

                x = p1.x * c1 + p2.x * c2 + p3.x * c3
                y = p1.y * c1 + p2.y * c2 + p3.y * c3
                yield Point(x, y)

####################################################################
