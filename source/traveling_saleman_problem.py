from enum import Enum
from typing import Union

import numpy as np

from .geneticalgorithm import geneticAlgorithm
from .plotting import create_animation
from .self_organizing_maps import self_organizing_maps
from .two_opt import two_opt


class Method(Enum):
    two_opt = 0
    GA = 1
    SOM = 2


def tsp(
    cities: np.ndarray,
    method: Method = Method.two_opt,
    improvement_threshold: float = 0.001,
    popSize: int = 100,
    eliteSize: int = 20,
    mutationRate: float = 0.01,
    generations: int = 500,
    learning_rate: float = 0.8,
    decay: float = 0.0003,
) -> Union[str, dict]:
    """Solve the traveling salesman problem with the selected method, the different parameters are used for different methods.

    Args:
        cities: The topology of the problem.
        method: The algorithm to be used.
        improvement_threshold: The minimum improvement for two-opt to continue searching.
        popSize: Population size for evolutionary algorithms.
        eliteSize: The selection size for evolutionary algorithms.
        mutationRate: Mutation rate for evolutionary algorithms.
        generations: The number of generations an evolutionary algorithm must go through.
        learning_rate: Displacement of the neurons to search a route.
        decay: Decays the learning rate so we get less aggressive searches over time.

    Returns:
        str: The plotly figure to json so we can use it on the plotlyview.
        data: dictionary of the maximum iteration and calculated distance.
    """

    # If method is an int change to Enum
    if type(method) == int:
        method = Method(method)

    # Select the correct method
    if method == Method.two_opt:
        routes, i, distance = two_opt(cities, improvement_threshold)
    elif method == Method.GA:
        routes, i, distance = geneticAlgorithm(cities, popSize, eliteSize, mutationRate, generations)
    elif method == Method.SOM:
        routes, i, distance = self_organizing_maps(cities, generations, learning_rate, popSize, decay)
    else:
        raise NotImplementedError(f"Method {method.name} not implemented.")

    # Reorder the cities matrix by route order in a new matrix for plotting.
    new_cities_orders = [
        np.concatenate((np.array([cities[route[i]] for i in range(len(route))]), np.array([cities[route[0]]])))
        for route in routes
    ]

    # Create figure for plotly view
    fig = create_animation(new_cities_orders)

    # Create data for data view
    data = {"Max iteration": i, "Calculated distance": distance}

    return fig.to_json(), data
