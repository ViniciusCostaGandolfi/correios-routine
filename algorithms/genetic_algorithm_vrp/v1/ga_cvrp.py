import numpy as np
from numba import jit
import time
from .inicial_populaton import initialize_population
from .fitness import calculate_fitness
from .cossover import perform_crossover


def genetic_algorithm_cvrp(
    points: np.array,
    volumes: np.array,
    distances: np.array,
    max_volume: float,
    mutation_rate: float,
    time_limit: float,
    pop_size: int
):
    n_points = points.shape[0]
    population = initialize_population(points, pop_size, volumes, max_volume)

    start_time = time.time()  # Armazena o tempo de início
    generation = 0
    best_score_stagnation_count = 0
    best_score = None

    population, fitness_scores = calculate_fitness(population, volumes, max_volume, distances)
    population = population[np.argsort(fitness_scores)]
    fitness_scores = fitness_scores[np.argsort(fitness_scores)]
    best_score = fitness_scores[0]
    
    plot_fitness = [0]
    plot_generations = [0]
    plot_time = [0]

    while time.time() - start_time < time_limit:
        if generation % 100 == 0:
            population, fitness_scores = calculate_fitness(population, volumes, max_volume, distances)
            current_best_score = np.min(fitness_scores)
            plot_fitness.append(current_best_score)
            plot_generations.append(generation)
            plot_time.append(time.time() - start_time)

            if current_best_score == best_score:
                best_score_stagnation_count += 1
            else:
                best_score = current_best_score
                best_score_stagnation_count = 0

            if best_score_stagnation_count >= 3:
                print("\n\nMelhor score estagnado, interrompendo o algoritmo.")
                break

            draw_progress_bar(generation, current_best_score, time.time(), start_time, time_limit, 30)

        population = perform_crossover(population, mutation_rate, volumes, max_volume, distances)
        generation += 1

    population, fitness_scores = calculate_fitness(population, volumes, max_volume, distances)
    population = population[np.argsort(fitness_scores)]
    fitness_scores = fitness_scores[np.argsort(fitness_scores)]
    print(f'\nGeração final: {generation} com Fitness: {fitness_scores[0]}')
    return population[0], fitness_scores[0], plot_fitness, plot_generations, plot_time


def draw_progress_bar(generation, best_score ,current_time, start_time, time_limit, length=30):
    elapsed_time = current_time - start_time
    progress = elapsed_time / time_limit
    filled_length = int(length * progress)
    bar = '=' * filled_length + '-' * (length - filled_length)
    return print(f'''\r
    Geração {generation}  - Best-Fitness: {best_score}
    Tempo restante: {int(time_limit - elapsed_time)} segundos |{bar}| {progress * 100:.2f}%''', end='')
