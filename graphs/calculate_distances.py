from graph_tool import Graph
import numpy as np
from graph_tool.topology import shortest_path
import haversine

def nearest_nodes_optimized(graph: Graph, points: np.ndarray):
    x_coords = graph.vp['x'].get_array()
    y_coords = graph.vp['y'].get_array()

    points_x = points[:, 1].round(6)
    points_y = points[:, 0].round(6)

    distances = np.sqrt((x_coords[:, np.newaxis] - points_x[np.newaxis, :])**2 +
                        (y_coords[:, np.newaxis] - points_y[np.newaxis, :])**2)
    nearest_indices = np.argmin(distances, axis=0)
    

    return nearest_indices.tolist()




def calculate_distances_routes(graph: Graph, array: np.ndarray, route_distances: bool = False):
    n_length = len(array)
    matrix_distance = np.zeros((n_length, n_length), dtype=float)
    matrix_routes = np.zeros((n_length, n_length), dtype=object)  
    
    for i in range(n_length):
        for j in range(n_length):
            matrix_distance[i, j] = haversine.haversine(array[i],  array[j])  * 10000
            matrix_routes[i, j] = [(array[i][1], array[i][0])]

    # Encontrar os 10 pontos mais próximos para cada ponto
    
        
        

    if route_distances:
        nearest_nodes = nearest_nodes_optimized(graph, array)
        for i in range(n_length):
            row_arg_sort = np.arange(n_length)
            if n_length > 30:
                row = matrix_distance[i, :]
                row_arg_sort = np.zeros(31, dtype=np.int32)
                row_arg_sort[1:] = np.argsort(row)[:30]
            
            for j in row_arg_sort:
                vlist, elist = shortest_path(graph, nearest_nodes[i], nearest_nodes[j], weights=graph.ep['length'])
                distance = np.sum(np.array([float(graph.ep['length'][e]) for e in elist], dtype=float))
                path = [(graph.vp['x'][v], graph.vp['y'][v]) for v in vlist]

                matrix_distance[i, j] = distance
                matrix_routes[i, j] = path
                matrix_distance[j, i] = distance
                matrix_routes[j, i] = path[::-1]

    return matrix_distance, matrix_routes