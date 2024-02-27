import time
from graph_tool import load_graph

print("Começou a carregar o gráfico")
tempo = time.time()
graph_limeira = load_graph('graphs/loaded_graphs/limeira-city.graphml')
print("Carregou o gráfico em ", time.time() - tempo)