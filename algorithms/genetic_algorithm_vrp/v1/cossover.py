from numba import jit
import numpy as np
from .fitness import calculate_fitness

@jit(nopython=True, cache=True)
def mutate_individual(individual: np.ndarray):
    idx1, idx2 = np.random.choice(len(individual), 2, replace=False)
    individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
    return individual


@jit(nopython=True, cache=True)
def one_point_crossover(parent1: np.ndarray, parent2: np.ndarray, mutate_rate: float):
    size = parent1.shape[0]
    # Garante que 'point' seja um escalar
    point = np.random.randint(1, size - 1)

    offspring = np.zeros(size, dtype=parent1.dtype)
    offspring[:point] = parent1[:point]

    # Adiciona genes de parent2 que não estão em offspring
    fill_idx = point
    for gene in parent2:
        if gene not in offspring[:point]:
            offspring[fill_idx] = gene
            fill_idx += 1
            if fill_idx >= size:
                break

    # Mutação
    if np.random.rand() < mutate_rate:
        offspring = mutate_individual(offspring)

    return offspring

@jit(nopython=True, cache=True)
def perform_crossover(
    older_population: np.ndarray,
    mutate_rate: float,
    volumes: np.ndarray,
    max_volume: int,
    distance_matrix: np.ndarray
    ):
    num_best = int(0.2 * older_population.shape[0])
    best_parents = older_population[:num_best]
    # rest_parents = older_population[num_best:]

    new_population = np.zeros(older_population.shape, dtype=older_population.dtype)

    for i in np.arange(older_population.shape[0]):
        if np.random.rand() < 0.4:
            # Bons com bons
            idx1, idx2 = np.random.randint(0, num_best, 2)
        elif np.random.rand() < 0.8:
            # Bons com ruins
            idx1 = np.random.randint(0, num_best)
            idx2 = np.random.randint(num_best, older_population.shape[0])
        else:
            # Ruins com ruins
            idx1, idx2 = np.random.randint(num_best, older_population.shape[0], 2)

        parent1 = older_population[idx1]
        parent2 = older_population[idx2]
        offspring = one_point_crossover(parent1, parent2, mutate_rate)
        new_population[i] = offspring

    # Mantendo os melhores indivíduos da geração anterior
 
    sorted_new_population, sorted_new_fitness_scores = calculate_fitness(new_population, volumes, max_volume, distance_matrix)
    sorted_new_population = sorted_new_population[np.argsort(sorted_new_fitness_scores)]
    sorted_new_fitness_scores = sorted_new_fitness_scores[np.argsort(sorted_new_fitness_scores)]
    new_population[:num_best] = sorted_new_population[:num_best]
    new_population[num_best: 2*num_best] = best_parents


    return new_population