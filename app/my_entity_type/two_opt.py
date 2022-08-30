from typing import Union

import numpy as np

from .helpers import path_distance


def _two_opt_swap(r, i, k):
    """Reverse the order of all elements from element i to element k in array r."""
    return np.concatenate((r[0:i], r[k : -len(r) + i - 1 : -1], r[k + 1 : len(r)]))


def two_opt(cities: np.ndarray, improvement_threshold: float) -> Union[list, list, list]:
    """2-opt Algorithm adapted from https://en.wikipedia.org/wiki/2-opt

    Args:
        cities: The problem definition. A list of cities with x and y coordinates.
        improvement_threshold: This algorithm stops if a new solution is not improvement more than the threshold.
    Returns:
        routes: A list of routes.
        iterations: The different iterations.
        distances: The calculated distances for the best route of each generation.
    """
    route = np.arange(cities.shape[0])  # Make an array of row numbers corresponding to cities.
    routes = [route]
    improvement_factor = 1  # Initialize the improvement factor.
    best_distance = path_distance(cities, route)  # Calculate the distance of the initial path.
    distances = [best_distance]
    i = 0
    iterations = [i]
    while improvement_factor > improvement_threshold:  # If the route is still improving, keep going!
        i += 1
        distance_to_beat = best_distance  # Record the distance at the beginning of the loop.
        for swap_first in range(1, len(route) - 2):  # From each city except the first and last,
            for swap_last in range(swap_first + 1, len(route)):  # to each of the cities following,
                new_route = _two_opt_swap(route, swap_first, swap_last)  # try reversing the order of these cities
                new_distance = path_distance(cities, new_route)  # and check the total distance with this modification.
                if new_distance < best_distance:  # If the path distance is an improvement,
                    route = new_route  # make this the accepted best route
                    best_distance = new_distance  # and update the distance corresponding to this route.
        improvement_factor = 1 - best_distance / distance_to_beat  # Calculate how much the route has improved.
        routes.append(route)
        iterations.append(i)
        distances.append(best_distance)
    return (
        routes,
        iterations,
        distances,
    )  # When the route is no longer improving substantially, stop searching and return the route.
