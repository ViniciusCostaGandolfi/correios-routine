import sys
import os
sys.path.append(os.getcwd())


import json
import dash
import plotly.graph_objects as go
import numpy as np
import matplotlib.colors as mcolors
from matplotlib import colormaps
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dtos import VrpOutDto, GeneticAlgorithmStatsDto


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.title = 'Dashboard Rotas'

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Dashboard de Otimização de Rotas", className="text-center mb-4"),
                width=12
            )
        ),

        dbc.Row(
            dbc.Col(
                html.P(
                    "Este Dashboard apresenta resultados de algoritmos genéticos para otimização de rotas de entrega. "
                    "Selecione uma configuração de VRP e visualize as estatísticas e o mapeamento das rotas.",
                    className="text-center mb-4"
                ),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id='vrp-selector',
                        options=[
                            {'label': 'VRP 30', 'value': 'n_30_cvrp_out.json'},
                            {'label': 'VRP 50', 'value': 'n_50_cvrp_out.json'},
                            {'label': 'VRP 100', 'value': 'n_100_cvrp_out.json'}
                        ],
                        value='n_30_cvrp_out.json',
                        style={'color': 'black'}
                    ),
                    width=8  
                ),
                dbc.Col(
                    dbc.Button("GA Estatísticas", id="show-gastats-button", className="mb-3"),
                    width=2  # Ajuste a largura conforme necessário
                ),
            ],
            className="mb-3"
        ),
        dbc.Collapse(
        dbc.Card(
            dbc.CardBody(
                id="gastats-content", 
                style={"overflowY": "scroll", "width": "100%", "height": "auto"}
            ),
            id="gastats-card",
            style={"width": "100%", "backgroundColor": "#343a40", "color": "white"}
        ),
        id="collapse-gastats",
        is_open=False
        ),
        dcc.Graph(
            id='map-plot',  
            style={'height': '100vh', 'border': '0', 'padding': '0', 'margin': '0'}
            ),
    ],
    fluid=True,
    style={"padding": "20px"}
)


@app.callback(
    Output("collapse-gastats", "is_open"),
    [Input("show-gastats-button", "n_clicks")],
    [State("collapse-gastats", "is_open")]
)
def toggle_gastats_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output("gastats-content", "children"),
    [Input('vrp-selector', 'value')]
)
def update_gastats_content(selected_vrp):
    with open(f'tests/data/v1/{selected_vrp.replace("cvrp_out", "ga_stats")}', 'r') as file:
        ga_stats = json.load(file)
        
        ga_stats = GeneticAlgorithmStatsDto.model_validate(ga_stats)
        
        fitness_graph = dcc.Graph(
            figure={
                'data': [
                    go.Scatter(
                        x=ga_stats.plot_generations[1:],
                        y=ga_stats.plot_fitness[1:],
                        mode='lines+markers',
                        name='Fitness'
                    )
                ],
                'layout': go.Layout(
                    title='Gerações x Fitnesss',
                    xaxis={'title': 'Gerações'},
                    yaxis={'title': 'Fitness'},
                    plot_bgcolor='rgb(35, 35, 35)',  
                    paper_bgcolor='rgb(17, 17, 17)',  
                    font=dict(color='white'), 
                    title_font=dict(color='white', size=20),
                )
            }
        )

        time_graph = dcc.Graph(
            figure={
                'data': [
                    go.Scatter(
                        x=ga_stats.plot_generations[1:],
                        y=ga_stats.plot_times[1:],
                        mode='lines+markers',
                        name='Gerações x Tempo'
                    )
                ],
                'layout': go.Layout(
                    title='Tempo de Processamento ao Longo das Gerações',
                    xaxis={'title': 'Gerações'},
                    yaxis={'title': 'Tempo (s)'},
                    plot_bgcolor='rgb(35, 35, 35)', 
                    paper_bgcolor='rgb(17, 17, 17)',  
                    font=dict(color='white'),  
                    title_font=dict(color='white', size=20), 
                )
            }
        )
        
        stats_layout = html.Div([
            html.H4("Estatísticas do Algoritmo Genético", className="card-title text-center"),
            html.H5(f"Generação Final           : {ga_stats.plot_generations[-1]}", className="card-text"),
            html.H5(f"Distancia Total           : {ga_stats.plot_fitness[-1]:.2f} Metros", className="card-text"),
            html.H5(f"Tempo Processamento       : {ga_stats.plot_times[-1]:.2f}s", className="card-text"),
            html.H5(f"Tamanho População         : {ga_stats.population_size}", className="card-text"),
            html.H5(f"Taxa Mutação              : {ga_stats.mutation_rate*100}%", className="card-text"),
            html.H5(f"Tempo Para Distancias     : {ga_stats.graph_stats.seconds_to_calculate:.2f}s para {ga_stats.graph_stats.distances_matrix}", className="card-text"),
        ],     )
        
        final_layout = html.Div([
            stats_layout,
            fitness_graph,
            time_graph
        ])

        card_layout = dbc.Card(
            dbc.CardBody(final_layout),
            className="mb-3"
        )

    return card_layout



@app.callback(
    Output('map-plot', 'figure'),
    [Input('vrp-selector', 'value')]
)
def update_map(selected_vrp):
    with open(f'tests/data/v1/{selected_vrp}', 'r') as file:
        data = json.load(file)

    vrp_out_dto = VrpOutDto.model_validate(data)
    routes = vrp_out_dto.routes
    colors = colormaps['viridis'](np.linspace(0, 1, len(routes)))
    colors = [mcolors.to_hex(color) for color in colors]
    fig = go.Figure()

    for i, route in enumerate(routes):
        lat = [coord[1] for coord in route.street_route]
        lon = [coord[0] for coord in route.street_route]
        fig.add_trace(go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='lines', 
            line=dict(
                width=2, 
                color=colors[i],
            ),
        ))

        for order in route.orders:
            fig.add_trace(go.Scattermapbox(
                lat=[order.address.latitude],
                lon=[order.address.longitude],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=7,
                    color='blue',
                ),
                text=["Pedido"],
            ))

    fig.add_trace(go.Scattermapbox(
        lat=[lat[0]],
        lon=[lon[0]],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=12,
            color='green'
        ),
        text=["Pedido"],
    ))
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            zoom=13,
            center=dict(lat=lat[0], lon=lon[0]) if lat and lon else dict(lat=0, lon=0),
        ),
        showlegend=False,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},  
        paper_bgcolor='rgba(0,0,0,0)',  
        plot_bgcolor='rgba(0,0,0,0)',  
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8000)