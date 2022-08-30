from numpy import cos
from numpy import ndarray
from numpy import pi
from numpy import random
from numpy import sin


def get_circle_points(radius: int, n: int) -> ndarray:
    """Create a circle with a certain radius and place cities evenly on this circle.

    Args:
        radius: The radius of the circle you are generating.
        n: The number of nodes you want to generate.

    Returns:
        A ndarray with cities with two coordinates.
    """
    points = ndarray(shape=(n, 2))
    for x, point in enumerate(points):
        point[0] = cos(2 * pi / n * x) * radius
        point[1] = sin(2 * pi / n * x) * radius

    # Shuffle the points so the initial route is not the perfect one
    random.RandomState(n).shuffle(points)
    return points


def get_random_points(n, seed):
    """Generate cities on random points given a seed. The same seed and n will always generate the same topology.

    Args:
        n: The number of nodes you want to generate.
        seed: The random seed for generating the topology. Makes sure that we can generate the same topology whenever we like.

    Returns:
        A ndarray with cities with two coordinates.
    """
    return random.RandomState(seed).rand(n, 2)
