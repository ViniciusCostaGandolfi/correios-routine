from numba import jit
import numpy as np
from ...tsp import lin_kernighan_heuristic


@jit(nopython=True, cache=True)
def create_submatrix(distance_matrix, indices):
    size = len(indices)
    submatrix = np.empty((size, size), dtype=distance_matrix.dtype)
    for i in range(size):
        for j in range(size):
            submatrix[i, j] = distance_matrix[indices[i], indices[j]]
    return submatrix


@jit(nopython=True, cache=True)
def concatenate_routes(routes: np.ndarray, individual_length: int):
    new_individual = np.zeros(individual_length, dtype=np.int32)
    index = 0
    for route in routes:
        route_length = len(route)
        new_individual[index:index + route_length] = route
        index += route_length
    return new_individual


@jit(nopython=True, cache=True)
def calculate_fitness(
    population: np.ndarray,
    volumes: np.ndarray,
    max_volume: int,
    distance_matrix: np.ndarray):
    fitness_scores = np.zeros(population.shape[0], dtype=np.float32)
    new_pop = np.zeros(population.shape, dtype=population.dtype)

    for i in range(population.shape[0]):
        new_individual = np.zeros(population.shape[1], dtype=np.int32)
        current_route = np.zeros(population.shape[1] + 1, dtype=np.int32)  # Inclui espaço para o ponto de partida 0
        total_volume = 0.0
        ind_fitness = 0.0
        route_idx = 0  # Índice para inserir pontos na rota atual
        new_ind_idx = 0  # Índice para inserir rotas no novo indivíduo

        for point in population[i]:
            if total_volume + volumes[point] > max_volume:
                if route_idx > 0:  # Verifica se a rota atual não está vazia
                    current_route[0] = 0  # Ponto de partida é sempre 0
                    submatrix = create_submatrix(distance_matrix, current_route[:route_idx+1])
                    optimized_route, length = lin_kernighan_heuristic(submatrix)
                    ind_fitness += length
                    # Adiciona rota otimizada ao novo indivíduo
                    new_individual[new_ind_idx:new_ind_idx+route_idx] = current_route[optimized_route[1:route_idx+1]]
                    new_ind_idx += route_idx
                # Reinicia a rota atual
                route_idx = 1
                current_route[route_idx] = point
                total_volume = volumes[point]
            else:
                route_idx += 1
                current_route[route_idx] = point
                total_volume += volumes[point]

        # Adiciona a última rota se houver
        if route_idx > 0:
            current_route[0] = 0
            submatrix = create_submatrix(distance_matrix, current_route[:route_idx+1])
            optimized_route, length = lin_kernighan_heuristic(submatrix)
            ind_fitness += length
            new_individual[new_ind_idx:new_ind_idx+route_idx] = current_route[optimized_route[1:route_idx+1]]

        fitness_scores[i] = ind_fitness
        new_pop[i] = new_individual
        

    return new_pop, fitness_scores