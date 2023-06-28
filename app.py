import json
from typing import Union

import numpy as np
import plotly.express as px
from munch import Munch
from pathlib import Path

from viktor.core import File
from viktor.core import Storage
from viktor.core import ViktorController
from viktor.utils import memoize
from viktor.views import PlotlyResult
from viktor.views import PlotlyView
from viktor.views import WebResult
from viktor.views import WebView

from parametrization import AppParametrization
from source.patterns import get_circle_points
from source.patterns import get_random_points
from source.plotting import plot_animation_and_fitness
from source.traveling_saleman_problem import tsp


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

    @PlotlyView("Route and fitness function", duration_guess=10)
    def get_tsp_result_and_fitness(self, params, **kwargs):
        """Plot an animation made by solving the traveling salesman problem, together with the fitness
        function."""
        fig_animation, data, highscore_key = run_tsp(params)

        fig = plot_animation_and_fitness(json.loads(fig_animation), data)

        return PlotlyResult(fig.to_json())


    @WebView("What's next?", duration_guess=1)
    def whats_next(self, params, **kwargs):
        """Initiates the process of rendering the "What's next" tab."""
        html_path = Path(__file__).parent / "next_step.html"
        with html_path.open(encoding="utf-8") as _file:
            html_string = _file.read()
        return WebResult(html=html_string)

