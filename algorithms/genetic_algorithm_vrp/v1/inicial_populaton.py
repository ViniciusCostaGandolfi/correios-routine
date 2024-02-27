import numpy as np
from sklearn.cluster import KMeans

def calculate_angles(points, depot):
    angles = np.arctan2(points[:, 1] - depot[1], points[:, 0] - depot[0])
    return np.mod(angles, 2 * np.pi)

def initialize_population(points: np.array, size: int, volumes: np.ndarray, max_volume: float):
    num_clusters = int(np.ceil(np.sum(volumes) / max_volume))

    population = np.empty((size, points.shape[0] - 1), dtype=np.int32)
    kmeans_population_size = size // 2

    for i in range(kmeans_population_size):
        kmeans = KMeans(n_clusters=num_clusters, random_state=i, n_init=10)
        labels = kmeans.fit_predict(points[1:])

        routes = [[] for _ in range(num_clusters)]

        for j, label in enumerate(labels):
            routes[label].append(j + 1)

        individual = np.concatenate([np.array(route) for route in routes])
        population[i] = individual

    # Parte K-Means baseada em Angulação
    
    angles = calculate_angles(points[1:], points[0]).reshape(-1, 1)
    for i in range(kmeans_population_size, size):
        kmeans = KMeans(n_clusters=num_clusters, random_state=i, n_init=10)
        labels = kmeans.fit_predict(angles)

        routes = [[] for _ in range(num_clusters)]

        for j, label in enumerate(labels):
            routes[label].append(j + 1)

        individual = np.concatenate([np.array(route) for route in routes])
        population[i] = individual

    return population