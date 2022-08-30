from typing import Union

import numpy as np
import plotly.express as px
from munch import Munch

from viktor.core import File
from viktor.core import Storage
from viktor.core import ViktorController
from viktor.utils import memoize
from viktor.views import DataGroup
from viktor.views import DataItem
from viktor.views import PlotlyAndDataResult
from viktor.views import PlotlyAndDataView
from viktor.views import PlotlyResult
from viktor.views import PlotlyView

from .parametrization import AppParametrization
from .patterns import get_circle_points
from .patterns import get_random_points
from .plotting import plot_fitness
from .traveling_saleman_problem import tsp


def update_highscore(score: float, key: int) -> float:
    """Updates the highscore for a particular topology for all the different methods.

    Args:
        score: The score of the current solution.
        key: The created by hash of the topolgy, used for accessing the storage.

    Returns:
        A float representing the highscore. Being it the score of the current solution or that from the storage.
    """

    key = str(key)  # Key is a hash so convert to string
    storage = Storage()  # Initialise the storage
    try:
        old_score = float(storage.get(key, scope="entity").getvalue())
    except FileNotFoundError as e:
        old_score = np.inf  # First score for this topology

    if score < old_score:  # New score better then old score
        storage.set(key, File(data=str(score)), scope="entity")  # Save new score
    else:
        score = old_score  # Return old score

    return score


@memoize  # Memoize because for the same input we don't need to run the algorithm again
def run_tsp(params: Munch) -> Union[px.line, dict, int]:
    """Run the traveling salesman problem with the selected topology and method.

    Args:
        params: The parameters from the parametrization class.

    Returns:
        fig: A plotly animation for the best route on each generation.
        data: A dictionary containing the generations and the distances for each generation.
        key: A hash key generated from the current topology. Used for the storage.
    """
    # Pars input
    topology = params.topology
    n = topology.n
    variables = params.variables

    # Build the topology
    if topology.topology == "circle":
        r = topology.r
        cities = get_circle_points(r, n)
    elif topology.topology == "random":
        seed = params.topology.seed
        cities = get_random_points(n, seed)

    # Get key for saving the highscore using a hash of the current topology
    key = hash(str(cities))

    # Parse the arguments
    fig, data = tsp(
        cities,
        int(variables.method),
        improvement_threshold=variables.improvement_threshold,
        popSize=variables.popSize,
        eliteSize=variables.eliteSize,
        mutationRate=variables.mutationRate,
        generations=variables.generations,
        learning_rate=variables.learning_rate,
        decay=variables.decay,
    )

    return fig, data, key


class Controller(ViktorController):
    label = "Traveling Salesman Problem"
    parametrization = AppParametrization

    @PlotlyAndDataView("Route", duration_guess=10)
    def get_tsp_result(self, params, **kwargs):
        """Plots the animation made by solving the traveling salesman problem."""
        fig, data, highscore_key = run_tsp(params)

        # Create datagroup
        items = []
        for key, value in data.items():
            items.append(DataItem(key, value[-1]))

        score = update_highscore(data["Calculated distance"][-1], highscore_key)
        items.append(DataItem("Topology highscore", score))

        return PlotlyAndDataResult(fig, DataGroup(*items))

    @PlotlyView("Fitness", duration_guess=10)
    def get_tsp_fitness(self, params, **kwargs):
        """Plot the fitness function."""
        _, data, _ = run_tsp(params)

        fig = plot_fitness(data["Max iteration"], data["Calculated distance"])

        return PlotlyResult(fig.to_json())
