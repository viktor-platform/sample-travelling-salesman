import pandas as pd
import plotly.express as px


def create_animation(new_cities_orders: list) -> px.line:
    """Creates an animation of the different routes found over different generations.

    Args:
        new_cities_orders: A list containing city lists in the order of the route taken.

    Returns:
        A plotly figure with animation frames.
    """
    data = {"x": [], "y": [], "frame": [], "city": []}
    for frame, new_cities_order in enumerate(new_cities_orders):
        # print(new_cities_order)
        for city in new_cities_order:
            data["x"].append(city[0])
            data["y"].append(city[1])
            data["frame"].append(frame)
            data["city"].append(city)
    df = pd.DataFrame(data=data)

    fig = px.line(df, x="x", y="y", animation_frame="frame", markers=True, animation_group="city")

    return fig


def plot_fitness(generations: list, distances: list) -> px.line:
    """Creates a plot for the fitness function. Here we use distance to measure the fitness.

    Args:
        generations: The different generations of the results.
        distances: The distances corresponding the generations.

    Returns:
        A plotly figure visualizing the distance over the generations.
    """
    fig = px.line(x=generations, y=distances, title="Fitness")
    fig.update_layout(xaxis_title="Iteration", yaxis_title="Distance")
    return fig
