import json
import sys
import os
from typing import List


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


center = {
    'nome': 'Correios - CENTRO DE ENTREGAS DE ENCOMENDAS',
    'address': {
        'logradouro': 'R. Dr. Custódio Moreira César',
        'numero': '352',
        'bairro': 'Vila Santa Lina',
        'cidade': 'Limeira',
        'estado': 'SP',
        'latitude': -22.582746,
        'longitude': -47.403675
    }
}

n_points = 500
with open('orders.json', 'r') as arquivo:
    orders = json.load(arquivo)
    
points = [[center['address']['latitude'], center['address']['longitude']]]

# Restante do código permanece o mesmo
volumes = [0]
for order in orders[:n_points]:
    points.append([
        order['address']['latitude'], order['address']['longitude']
    ])
    volumes.append(order['volume'])

# Convertendo para arrays do NumPy
points = np.array(points)
volumes = np.array(volumes)

t_distances = time.time()
distance_matrix, routes_matrix = calculate_distances_routes(graph_limeira, points, True)
t_distances = time.time() - t_distances
t_seconds = 60*5
pop_size = 100
mutation_rate = 0.1
max_volume = 100

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
            current_route.append(0)  
            routes.append(np.array(current_route))
            route_volumes.append(total_volume)  
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


mapa = folium.Map(location=points[0], zoom_start=15)

# Gerar cores do colormap
colorlist = [mcolors.to_hex(color) for color in colors]
# Adicionando pontos e rotas ao mapa
orders_dtos: List[OrderDto] = []
orders_id = 1
street_points = []
for index, route in enumerate(routes):
    route_color = colorlist[index]
    full_route = []
    
    for point_index in route:
        point = points[point_index]
        order = orders[point_index]
        orders_dtos.append(
            OrderDto(
                id=orders_id,
                volume=float(order['volume']),
                address=AddressDto(
                    formatted_address='', 
                    street_name=str(order['address']['logradouro']), 
                    street_number=str(order['address']['numero']), 
                    city=str(order['address']['cidade']), 
                    postal_code=str(order['address']['cep']), 
                    neighborhood=str(order['address']['bairro']), 
                    state='SP', 
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
    location=[points[0][0], points[0][1]], 
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
    points_route = [[orders_dtos[j].address.latitude, orders_dtos[j].address.longitude] for j in route]
    link_google = 'https://www.google.com/maps/dir/'
    route_dtos.append(
        RouteDto(
            id=index,
            orders=orders_in_route,
            street_route=street_points[index],
            total_volume=route_volumes[index],
            points_route=points_route
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
with open(f'tests/data/v1/correios_n_{n_points}_cvrp_in.json', 'w') as f:
    f.write(vrp_in_json)

with open(f'tests/data/v1/correios_n_{n_points}_cvrp_out.json', 'w') as f:
    f.write(vrp_out_json)
    
with open(f'tests/data/v1/correios_n_{n_points}_ga_stats.json', 'w') as f:
    f.write(ga_stats_json)
    
# mapa.save(f'tests/data/v1/n_{n_points}_mapa_cvrp.html')
mapa.save(f'mapa_cvrp.html')

    