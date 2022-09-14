import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_animation(new_cities_orders: list) -> px.line:
    """Creates an animation of the different routes found over different generations.

    Args:
        new_cities_orders: A list containing city lists in the order of the route taken.

    Returns:
        A plotly figure with animation frames.
    """
    data = {"x": [], "y": [], "frame": [], "city": []}
    for frame, new_cities_order in enumerate(new_cities_orders):
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


def plot_animation_and_fitness(route_fig: dict, data: dict) -> go.Figure:
    """Creates a subplot with the one, a plot for the fitness function. Here we use distance to measure the fitness.
    The other plot is an animation of the different routes found over different generations.

    Args:
        route_fig: A plotly Figure object converted to a dict format.
        data: A dictionary containing the "Max iteration" and "Calculated distance" data points.

    Returns:
        A plotly figure visualizing the distance over the generations, as well as the route frames.
    """
    fig = make_subplots(
        cols=2,
        column_widths=[0.5, 0.5],
        horizontal_spacing=0.02,
        subplot_titles=('Route', 'Fitness')
    )
    fig.add_trace(go.Scatter(
        x=route_fig['data'][0]['x'],
        y=route_fig['data'][0]['y'],
        name='Route',
        showlegend=True,
        hoverinfo='name',
        legendgroup='Route',
        mode='markers+lines',
    ))
    fig.add_trace(go.Scatter(
        x=[data["Max iteration"][0]],
        y=[data["Calculated distance"][0]],
        name='Fitness',
        showlegend=True,
        hoverinfo='name',
        legendgroup='Fitness',
        mode='markers+lines',
    ), row=1, col=2)
    fig_dict = fig.to_dict()
    fig_dict['frames'] = route_fig['frames']
    for i, frame in enumerate(fig_dict['frames']):
        frame['data'].append(go.Scatter(x=data["Max iteration"][0: i + 1],
                                        y=data["Calculated distance"][0: i + 1]))
    fig_dict['layout']['updatemenus'] = route_fig['layout']['updatemenus']
    fig_dict['layout']['sliders'] = route_fig['layout']['sliders']

    fig_dict['layout']['xaxis2']['range'] = [min(data["Max iteration"]) - 0.5, max(data["Max iteration"]) + 0.5]
    fig_dict['layout']['yaxis2']['range'] = [min(data["Calculated distance"]) - 0.5, max(data["Calculated distance"]) + 0.5]
    return go.Figure(fig_dict)
