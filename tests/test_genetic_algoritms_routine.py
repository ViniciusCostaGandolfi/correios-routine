import sys
import os


sys.path.append(os.getcwd())

import time
import folium
from sklearn.datasets import make_blobs
from algorithms import genetic_algorithm_cvrp_v1
from graphs import calculate_distances_routes
from matplotlib import colormaps
import matplotlib.colors as mcolors
import numpy as np
from dtos import AddressDto, OrderDto, RouteDto, VrpInDto, VrpOutDto, GeneticAlgorithmStatsDto, GraphStatsDto
from graphs import graph_limeira


centers = [[-22.573213, -47.402682]] # Limeira
cluster_std = [[0.01]]
n_points = 100
points, _ = make_blobs(n_samples=n_points, centers=centers, cluster_std=cluster_std, random_state=1)
points[0] = centers[0]
t_distances = time.time()
distance_matrix, routes_matrix = calculate_distances_routes(graph_limeira, points, True)
t_distances = time.time() - t_distances
t_seconds = 60*5
pop_size = 30
mutation_rate = 0.1
volumes = np.ones(n_points)
max_volume = 10

print(f'Matriz {n_points}x{n_points} rotas pelas vias em {t_distances:.3f}s')
grath_stats = GraphStatsDto(
    distances_matrix=f'Matriz {n_points}x{n_points} rotas pelas vias',
    seconds_to_calculate=t_distances
)
t_solve = time.time()
best_solution, best_fitness, plot_fitness, plot_generations, plot_times = genetic_algorithm_cvrp_v1(points, volumes, distance_matrix, max_volume, mutation_rate=mutation_rate, time_limit=t_seconds, pop_size=pop_size)
t_solve = time.time() - t_solve


ga_stats = GeneticAlgorithmStatsDto(
    processor_type='Intel Core i3 10 Geração',
    plot_generations=plot_generations,
    plot_fitness=plot_fitness,
    plot_times = plot_times,
    population_size=pop_size,
    mutation_rate=mutation_rate,
    converge=t_solve <= t_seconds,
    graph_stats=grath_stats
)

# Plotar os pontos e a rota
# Criação do Mapa Folium


routes = []
route_volumes = []  
current_route = [0]
total_volume = 0

for point in best_solution:
    if total_volume + volumes[point] > max_volume:
        if current_route != [0]:
            current_route.append(0)  # Voltar ao depósito
            routes.append(np.array(current_route))
            route_volumes.append(total_volume)  # Adiciona o volume da rota
        current_route = [0, point]
        total_volume = volumes[point]
    else:
        current_route.append(point)
        total_volume += volumes[point]

if current_route != [0]:
    current_route.append(0)  # Voltar ao depósito
    routes.append(np.array(current_route))
    route_volumes.append(total_volume)  # Adiciona o volume da rota

# Visualizar as rotas
colors = colormaps['viridis'](np.linspace(0, 1, len(routes)))


mapa = folium.Map(location=centers[0], zoom_start=15)

# Gerar cores do colormap
colorlist = [mcolors.to_hex(color) for color in colors]
# Adicionando pontos e rotas ao mapa
orders_dtos = []
orders_id = 1
street_points = []
for index, route in enumerate(routes):
    route_color = colorlist[index]
    full_route = []
    
    for point_index in route:
        point = points[point_index]
        orders_dtos.append(
            OrderDto(
                id=orders_id,
                volume=1,
                address=AddressDto(
                    formatted_address='Rua, numero, bairro, cidade, UF - CEP', 
                    street_name='Rua', 
                    street_number='Numero', 
                    city='Cidade', 
                    postal_code='CEP', 
                    neighborhood='Bairro', 
                    state='UF', 
                    complement='', 
                    latitude=point[0], 
                    longitude=point[1]
                )
            )
        )
        folium.CircleMarker(location=point, radius=5, color='red', fill=True).add_to(mapa)
    for i in range(len(route) - 1):
        # Obter a rota entre os pontos na rota
        rota_pontos = routes_matrix[route[i]][route[i + 1]]
        # Inverter as coordenadas de long, lat para lat, long e adicionar o ponto final
        rota_latlng = [[coord[1], coord[0]] for coord in rota_pontos] + [[points[route[i + 1]][0], points[route[i + 1]][1]]]
        full_route.extend(rota_latlng)
        folium.PolyLine(rota_latlng, color=route_color, weight=2.5, opacity=1).add_to(mapa)
        
    street_points.append([(coord[1], coord[0]) for coord in full_route])

# Adicionar um marcador grande para o centro de distribuição
folium.Marker(
    location=[centers[0][0], centers[0][1]], 
    popup="Centro de Distribuição", 
    color='black',
    icon=folium.Icon(color='green', icon='info-sign')
).add_to(mapa)

# Salvar o mapa em um arquivo HTML


print(f"CVRP de {n_points} pontos em {t_solve:.3f}s")

distribuitor_address = AddressDto(
        formatted_address='Rua, numero, bairro, cidade, UF - CEP', 
        street_name='Rua', 
        street_number='Numero', 
        city='Cidade', 
        postal_code='CEP', 
        neighborhood='Bairro', 
        state='UF', 
        complement='', 
        latitude=points[0][0], 
        longitude=points[1][1]
        )
vrp_in = VrpInDto(
    distribuitor=distribuitor_address,
    orders=orders_dtos,  # Supondo que orders_dtos seja uma lista de todas as OrderDto antes da otimização
    drivers_volume=max_volume
)


route_dtos = []
for index, route in enumerate(routes):
    orders_in_route = [orders_dtos[j] for j in route] 

    route_dtos.append(
        RouteDto(
            id=index,
            orders=orders_in_route,
            street_route=street_points[index],
            total_volume=route_volumes[index]
        )
    )

# Criar a instância VrpOutDto
vrp_out = VrpOutDto(
    distribuitor=distribuitor_address,
    routes=route_dtos,
    drivers_volume=max_volume
)

# Serializar para JSON
vrp_in_json = vrp_in.model_dump_json()
vrp_out_json = vrp_out.model_dump_json()
ga_stats_json = ga_stats.model_dump_json()

# Salvar em arquivos
with open(f'tests/data/v1/n_{n_points}_cvrp_in.json', 'w') as f:
    f.write(vrp_in_json)

with open(f'tests/data/v1/n_{n_points}_cvrp_out.json', 'w') as f:
    f.write(vrp_out_json)
    
with open(f'tests/data/v1/n_{n_points}_ga_stats.json', 'w') as f:
    f.write(ga_stats_json)
    
# mapa.save(f'tests/data/v1/n_{n_points}_mapa_cvrp.html')
mapa.save(f'mapa_cvrp.html')

    