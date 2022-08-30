from viktor.core import ViktorController


class Controller(ViktorController):
    label = "Machine Learning"
    children = ["MyEntityType"]
    show_children_as = "Table"
