import sys
import os
sys.path.append(os.getcwd())

import folium
from sklearn.datasets import make_blobs
from algorithms import lin_kernighan_heuristic
from graphs import calculate_distances_routes
from graphs import graph_limeira
import time


centers = [[-22.573213, -47.402682]] # Limeira
cluster_std = [[0.01]]
n_points = 500
points, _ = make_blobs(n_samples=n_points, centers=centers, cluster_std=cluster_std, random_state=0)
# distance_matrix = create_distance_matrix(points)
t_distances = time.time()
distance_matrix, routes_matrix = calculate_distances_routes(graph_limeira, points, False)
t_distances = time.time() - t_distances

print(f'Matriz {n_points}x{n_points} rotas pelas vias em {t_distances:.3f}s')

t_solve = time.time()
tour, length = lin_kernighan_heuristic(distance_matrix)
t_solve = time.time() - t_solve
# Plotar os pontos e a rota
# Criação do Mapa Folium
mapa = folium.Map(location=centers[0], zoom_start=15)

# Adicionando pontos ao mapa
for point in points:
    folium.CircleMarker(location=point, radius=5, color='blue', fill=True).add_to(mapa)

# Adiciona as rotas ao mapa
for i in range(len(tour)):
    # Obter a rota entre os pontos no tour
    route = routes_matrix[tour[i]][tour[(i + 1) % len(tour)]]
    # Inverter as coordenadas de long, lat para lat, long e adicionar o ponto final

    route_latlng = [[coord[1], coord[0]] for coord in route] + [[points[tour[(i + 1) % len(tour)]][0], points[tour[(i + 1) % len(tour)]][1]]]
    folium.PolyLine(route_latlng, color='red', weight=2.5, opacity=1).add_to(mapa)

# Salvar o mapa em um arquivo HTML
mapa.save("mapa_lin_kernighan.html")

print(f"TSP de {n_points} pontos em {t_solve:.3f}s")


