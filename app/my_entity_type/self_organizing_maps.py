from typing import Union

import numpy as np
import pandas as pd

from viktor.core import UserException

from .helpers import path_distance


def _select_closest(candidates: np.ndarray, origin: np.ndarray) -> int:
    """Return the index of the closest candidate to a given point.

    Args:
        candidates: The neuron network.
        origin: The original place of the city.

    Returns:
       The index of the closest candidate to a given point.
    """
    return np.linalg.norm(candidates - origin, axis=1).argmin()


def _read_tsp(cities: np.ndarray) -> pd.DataFrame:
    """Convert the cities in our examples to the format that this algorithm uses.

    Args:
        cities: List of cities with x and y coordinates.

    Returns:
        Pandas dataframe containing the cities with x and y coordinates.
    """
    data = {"city": [], "y": [], "x": []}
    for idx, city in enumerate(cities, start=1):
        data["city"].append(idx)
        data["y"].append(city[1])
        data["x"].append(city[0])

    df = pd.DataFrame(data=data)

    return df


def _normalize(points: pd.DataFrame) -> pd.DataFrame:
    """For a given array of n-dimensions, normalize each dimension by removing the
    initial offset and normalizing the points in a proportional interval: [0,1]
    on y, maintining the original ratio on x.

    Args:
        points: A vector of points.

    Returns:
        The normalized version of a given vector of points.
    """
    ratio = (points.x.max() - points.x.min()) / (points.y.max() - points.y.min()), 1
    ratio = np.array(ratio) / max(ratio)
    norm = points.apply(lambda c: (c - c.min()) / (c.max() - c.min()))
    return norm.apply(lambda p: ratio * p, axis=1)


def _generate_network(size: int) -> np.ndarray:
    """Generate a neuron network of a given size.

    Args:
        The size of the network you want to generate.

    Returns:
        A vector of two dimensional points in the interval [0,1].
    """
    return np.random.rand(size, 2)


def _get_neighborhood(center: int, radix: float, domain: np.ndarray) -> np.ndarray:
    """Get the range gaussian of given radix around a center index.

    Args:
        center: The id of the city you want to search from.
        radix: The distance from the center where you want to search.
        domain: The network.

    Returns:
        The distances of points around the center index given a radix.
    """

    # Impose an upper bound on the radix to prevent NaN and blocks
    if radix < 1:
        radix = 1

    # Compute the circular network distance to the center
    deltas = np.absolute(center - np.arange(domain))
    distances = np.minimum(deltas, domain - deltas)

    # Compute Gaussian distribution around the given center
    return np.exp(-(distances * distances) / (2 * (radix * radix)))


def _get_route(cities: pd.DataFrame, network: np.ndarray) -> pd.Int64Index:
    """Get the route generated by the algorithm.

    Args:
        cities: The problem definition.
        network: The neuron network closely representing the map.

    Returns:
        The route computed by a network.
    """
    cities["winner"] = cities[["x", "y"]].apply(lambda c: _select_closest(network, c), axis=1, raw=True)

    return cities.sort_values("winner").index


def self_organizing_maps(
    cities: np.ndarray, iterations: int, learning_rate: float = 0.8, popSize: int = 100, decay: float = 0.0003
) -> Union[list, list, list]:
    """Solve the TSP using a Self-Organizing Map.

    Args:
        cities: The problem definition. A list of cities with x and y coordinates.
        iterations: The number of generations we want to try getting a better solution.
        popSize: Size of the population.
        learning_rate: Controls the exploration and explotation of the algorithm. A high number indicates an aggressive search.
        decay: Decays the learning rate over time so the algorithm gets less aggressive.

    Returns:
        routes: A list of routes.
        iterations: The different generations.
        distances: The calculated distances for the best route of each generation.
    """
    problem = _read_tsp(cities)

    # Obtain the normalized set of cities (w/ coord in [0,1])
    cities = problem.copy()

    cities[["x", "y"]] = _normalize(cities[["x", "y"]])

    # The population size
    n = popSize

    # Generate an adequate network of neurons:
    network = _generate_network(n)

    routes = [_get_route(cities, network).values.tolist()]
    distances = [path_distance(problem[["x", "y"]].to_numpy())]

    for i in range(iterations):
        # Choose a random city
        city = cities.sample(1)[["x", "y"]].values
        winner_idx = _select_closest(network, city)
        # Generate a filter that applies changes to the winner's gaussian
        gaussian = _get_neighborhood(winner_idx, n // 10, network.shape[0])
        # Update the network's weights (closer to the city)
        network += gaussian[:, np.newaxis] * learning_rate * (city - network)
        # Decay the variables
        learning_rate = learning_rate * (1 - decay)
        n = n * (1 - decay)

        # Adding data for the frames
        route = _get_route(cities, network)
        problem = problem.reindex(route)
        distances.append(path_distance(problem[["x", "y"]].to_numpy()))
        route = route.values.tolist()
        routes.append(route)

        # Check if any parameter has completely decayed.
        if n < 1:
            raise UserException("Radius has completely decayed, finishing execution at {} iterations".format(i))
        if learning_rate < 0.001:
            raise UserException("Learning rate has completely decayed, finishing execution at {} iterations".format(i))

    return routes, np.arange(0, iterations + 1, 1).tolist(), distances
