import networkx as nx
import matplotlib.pyplot as plt
from src.auto import *


def visualize(A: Automaton):
    G = nx.DiGraph(directed=True)
    G.add_edges_from(A.Delta)

    pos = nx.spring_layout(G)
    edge_labels = dict([((u, v,), d['w'])
                        for u, v, d in G.edges(data=True)])
    nx.draw(G, pos, with_labels=True, font_color='red', connectionstyle='arc3, rad = 0.2')

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', label_pos=0.5,
                                 connectionstyle='arc3, rad = 0.2')

    plt.show()
