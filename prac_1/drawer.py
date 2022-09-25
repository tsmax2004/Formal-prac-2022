from prac_1.DOA import DOA
from graphviz import Digraph


def draw_doa(doa, output):
    gr = Digraph()
    for node in doa.nodes:
        if node in doa.acceptance and node == doa.start:
            gr.node(node, node, color='orange')
        elif node in doa.acceptance:
            gr.node(node, node, color='red')
        elif node == doa.start:
            gr.node(node, node, color='green')
        else:
            gr.node(node, node)
    for out in doa.adj_lists:
        for symbol in doa.adj_lists[out]:
            for to in doa.adj_lists[out][symbol]:
                gr.edge(out, to, 'e' if not symbol else symbol)
    gr.render(output)