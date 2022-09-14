import numpy as np


def path_distance(cities: np.ndarray, route: list = None) -> float:
    """Calculate the euclidian distance in n-space of the route traversing cities, ending at the path start.

    Args:
        cities: The cities used in the problem.
        route: A solution. If None the function sees the order of cities as the route.

    Returns:
        The total distance the route takes.
    """
    if route is not None:  # Cities are not in the right order
        return np.sum([np.linalg.norm(cities[route[p]] - cities[route[p - 1]]) for p in range(len(route))])
    else:  # Cities are in the right order
        return np.sum(np.linalg.norm(cities - np.roll(cities, 1, axis=0), axis=1))
