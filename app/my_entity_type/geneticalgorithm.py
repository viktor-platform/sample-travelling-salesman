import operator

import numpy as np
import pandas as pd

from .helpers import path_distance


def _createRoute(cities: np.ndarray) -> np.ndarray:
    """Rearange the cities so we get a random route.

    Args:
        cities: list of cities as ndarray(size=(2,n)).

    Returns:
        Array containing the city id's in the order of the route.
    """
    route = np.arange(cities.shape[0])  # cities list to array with indices to cities
    np.random.shuffle(route)  # Shuffle the route
    return route


def _initialPopulation(popSize: int, cities: np.ndarray) -> list:
    """Initialise the population with different routes.

    Args:
        popSize: population size.
        cities: list of cities as ndarray(size=(2,n)).

    Returns:
        List of different routes.
    """
    population = []

    for i in range(0, popSize):
        population.append(_createRoute(cities))
    return population


def _rankRoutes(population: list, cities: np.ndarray) -> np.ndarray:
    """Sort the routes of the population so that we can select the best.

    Args:
        population: The population consisting of routes.
        cities list ofcities as ndarray(size=(2,n)).

    Returns:
        Sorted list with the best routes.
    """
    fitnessResults = {}
    for idx, route in enumerate(population):
        fitnessResults[idx] = 1 / float(path_distance(cities, route))

    return sorted(fitnessResults.items(), key=operator.itemgetter(1), reverse=True)


def _selection(popRanked: list, eliteSize: int) -> list:
    """Select the creme de la creme.

    Args:
        popRanked: population ranked from best to worst.
        eliteSize: size to be selected.

    Returns:
        Selection of the best routes used for the matingpool.
    """
    selectionResults = []
    df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
    df["cum_sum"] = df.Fitness.cumsum()
    df["cum_perc"] = 1000 * df.cum_sum / df.Fitness.sum()

    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100 * np.random.random()
        for j in range(0, len(popRanked)):
            if pick <= df.iat[j, 3]:
                selectionResults.append(popRanked[j][0])
                break
    return selectionResults


def _matingPool(population: list, selectionResults: list) -> list:
    """Put the selection into a pool for breeding.

    Args:
        population: The population.
        selectionResults: The index of the population to be added to the pool.

    Returns:
        List of the best roots used as matingpool.
    """
    matingpool = []
    for result in selectionResults:
        matingpool.append(population[result])
    return matingpool


def _breed(parent1: list, parent2: list) -> list:
    """Combine different genes from two different parents.

    Args:
        parent1: A route.
        parent2: A route.

    Returns:
        A child with random genes from both parents Uses two-point crossover.
    """
    child = []
    childP1 = []
    childP2 = []

    geneA = int(np.random.random() * len(parent1))
    geneB = int(np.random.random() * len(parent1))

    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])

    childP2 = [item for item in parent2 if item not in childP1]
    child = childP1 + childP2
    return child


def _breedPopulation(matingpool: list, eliteSize: int) -> list:
    """Uses the matingpool and combines different parents to create new solutions.

    Args:
        matingpool: The selected pops to mate.
        eliteSize: The size of the selection we want to give to the next generation.

    Returns:
        A new population generated from combining fit parents.
    """
    children = []
    length = len(matingpool) - eliteSize
    pool = np.copy(matingpool)
    np.random.shuffle(pool)

    for i in range(0, eliteSize):
        children.append(matingpool[i])

    for i in range(0, length):
        child = _breed(pool[i], pool[len(matingpool) - i - 1])
        children.append(child)

    return children


def _mutate(individual: list, mutationRate: float) -> list:
    """Mutate an individual. We use this so we do not deadlock our algorithm.

    Args:
        individual: Single child to mutate.
        mutationRate: The chance to swap a city.

    Returns:
        The original individual with random cities switched on its route.
    """
    for swapped in range(len(individual)):
        if np.random.random() < mutationRate:
            swapWith = int(np.random.random() * len(individual))

            city1 = individual[swapped]
            city2 = individual[swapWith]

            individual[swapped] = city2
            individual[swapWith] = city1

        return individual


def _mutatePopulation(population: list, mutationRate: float) -> list:
    """Mutate the whole population.

    Args:
        population: The population.
        mutationRate: The mutation rate of the population.

    Returns:
        The original population but with mutated routes.
    """
    mutatedPop = []
    for ind in range(0, len(population)):
        mutatedInd = _mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop


def _nextGeneration(currentGen: list, eliteSize: int, mutationRate: float, cities: np.ndarray) -> list:
    """Take steps to the next generation. Rank, select, mate, breed and mutate.

    Args:
        currentGen: The population of the current generation.
        eliteSize: Size of the best routes we want to select.
        mutationRate: The chance for each route to swap a city.
        cities: The problem definition.

    Returns:
        The population for the next generation.
    """
    popRanked = _rankRoutes(currentGen, cities)
    selectionResults = _selection(popRanked, eliteSize)
    matingpool = _matingPool(currentGen, selectionResults)
    children = _breedPopulation(matingpool, eliteSize)
    nextGeneration = _mutatePopulation(children, mutationRate)
    return nextGeneration


def geneticAlgorithm(
    cities: np.ndarray, popSize: int, eliteSize: int, mutationRate: float, generations: int
) -> (list, list, list):
    """This algorithm reflects the process of natural selection where the fittest individuals are selected for reproduction in order to produce offspring of the next generation. In this app each individual is a different route.

    Args:
        cities: The problem definition. A list of cities with x and y coordinates.
        popSize: Size of the population.
        eliteSize: Size of the best routes we want to select.
        mutationRate: The chance for each route to swap a city.
        generations: The number of generations we want to try getting a better solution.

    Returns:
        routes: A list of routes.
        iterations: The different generations.
        distances: The calculated distances for the best route of each generation.
    """
    route = np.arange(cities.shape[0])  # Make an array of row numbers corresponding to cities.
    best_distance = path_distance(cities, route)  # Calculate the distance of the initial path.

    iterations = [0]
    distances = [best_distance]
    routes = [route]

    pop = _initialPopulation(popSize, cities)
    for i in range(1, generations + 1):
        pop = _nextGeneration(pop, eliteSize, mutationRate, cities)
        best_route = pop[_rankRoutes(pop, cities)[0][0]]
        distance = path_distance(cities, best_route)
        iterations.append(i)
        distances.append(distance)
        routes.append(best_route)

    return routes, iterations, distances
