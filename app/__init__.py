from viktor import InitialEntity

from .my_entity_type.controller import Controller as MyEntityType
from .my_folder.controller import Controller as MyFolder

initial_entities = [InitialEntity("MyFolder", name="Machine Learning")]
