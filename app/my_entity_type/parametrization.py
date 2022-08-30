import json
from pathlib import Path

from viktor.parametrization import IsEqual
from viktor.parametrization import Lookup
from viktor.parametrization import NumberField
from viktor.parametrization import OptionField
from viktor.parametrization import OptionListElement
from viktor.parametrization import Or
from viktor.parametrization import Parametrization
from viktor.parametrization import Section
from viktor.parametrization import Text

_options = [OptionListElement("circle", "Circle"), OptionListElement("random", "Random")]

_method_options = [
    OptionListElement(0, "2-opt"),
    OptionListElement(1, "Genetic Algorithm"),
    OptionListElement(2, "Self-Organizing Maps"),
]

# Use a json file with all the descriptions to not clutter this file
with open(Path(__file__).parent.parent / "lib" / "descriptions.json") as json_file:
    descriptions = json.load(json_file)


class AppParametrization(Parametrization):
    topology = Section("Topology")
    topology.text = Text(descriptions["Topology"])
    topology.topology = OptionField("Topology", options=_options, default="circle")
    topology.n = NumberField("Nodes", min=3, max=100, step=1, default=5)
    topology.r = NumberField(
        "Radius", min=1, max=100, step=1, default=1, visible=IsEqual(Lookup("topology.topology"), "circle")
    )
    topology.seed = NumberField("Seed", default=1, visible=IsEqual(Lookup("topology.topology"), "random"))

    variables = Section("Variables")
    # Different texts depending on method selected
    variables.text_two_opt = Text(descriptions["Two opt"], visible=IsEqual(Lookup("variables.method"), 0))
    variables.text_ga = Text(descriptions["Genetical algorithm"], visible=IsEqual(Lookup("variables.method"), 1))
    variables.text_som = Text(descriptions["Self-organizing maps"], visible=IsEqual(Lookup("variables.method"), 2))

    # The method and its variables
    variables.method = OptionField("Method", options=_method_options, default=0)
    variables.improvement_threshold = NumberField(
        "Improvement threshold",
        default=0.001,
        step=0.001,
        visible=IsEqual(Lookup("variables.method"), 0),
        description=descriptions["Improvement threshold"],
    )

    variables.popSize = NumberField(
        "Population size",
        default=10,
        step=1,
        visible=Or(IsEqual(Lookup("variables.method"), 1), IsEqual(Lookup("variables.method"), 2)),
        description=descriptions["Population size"],
    )
    variables.eliteSize = NumberField(
        "Elite size",
        default=5,
        step=1,
        visible=IsEqual(Lookup("variables.method"), 1),
        description=descriptions["Elite size"],
    )
    variables.mutationRate = NumberField(
        "Mutation rate",
        default=0.01,
        step=0.01,
        visible=IsEqual(Lookup("variables.method"), 1),
        description=descriptions["Mutation rate"],
    )
    variables.generations = NumberField(
        "Generations",
        default=500,
        step=100,
        visible=Or(IsEqual(Lookup("variables.method"), 1), IsEqual(Lookup("variables.method"), 2)),
        description=descriptions["Generations"],
    )
    variables.learning_rate = NumberField(
        "Learning rate",
        default=0.8,
        min=0.1,
        max=1,
        step=0.1,
        visible=IsEqual(Lookup("variables.method"), 2),
        description=descriptions["Learning rate"],
    )
    variables.decay = NumberField(
        "Decay",
        default=0.0003,
        min=0,
        max=1,
        step=0.0001,
        visible=IsEqual(Lookup("variables.method"), 2),
        description=descriptions["Decay"],
    )
