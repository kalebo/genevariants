#!/usr/bin/env python3

import networkx as nx
import aaindex

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4

def build_correlation_graph(aarecords: list):
    graph = {}
    for r in aarecords:
        for i,v in r.correlated.items():
            if r.key not in graph:
                graph[r.key] = []
            graph[r.key].append(i)
    G = nx.DiGraph(graph)
    return G

def build_correation_weighted_graph(aarecords: list):
    graph = nx.DiGraph()
    for r in aarecords:
        graph.add_node(r.key)
    for r in aarecords:
        for i,v in r.correlated.items():
            graph.add_edge(r.key, i, weight=v)
    return graph

if __name__ == "__main__":
    aaindex.init_from_file("data/aaindex1")
    all_records = aaindex._aaindex.values()

    graph = build_correation_weighted_graph(all_records)
    nx.write_graphml(graph, "graph.graphml")


    # plot = figure(title="AAIndex Correlation Network", x_range=(-1.1,1.1), y_range=(-1.1,1.1),
    #             tools="", toolbar_location=None)

    # graph = from_networkx(G, nx.spring_layout, scale=2, center=(0,0))
    # plot.renderers.append(graph)

    # output_file("Networkx_graph.html")
    # show(plot)

    #### --

    # plot = Plot(plot_width=1000, plot_height=1000,
    #         x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
    # plot.title.text = "AAIndex1 Correlation Network"

    # plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

    # graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0,0))

    # graph_renderer.node_renderer.glyph = Circle(size=5, fill_color=Spectral4[0])
    # graph_renderer.node_renderer.selection_glyph = Circle(size=5, fill_color=Spectral4[2])
    # graph_renderer.node_renderer.hover_glyph = Circle(size=5, fill_color=Spectral4[1])

    # graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=3)
    # graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=3)
    # graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=3)

    # graph_renderer.selection_policy = NodesAndLinkedEdges()
    # graph_renderer.inspection_policy = EdgesAndLinkedNodes()

    # plot.renderers.append(graph_renderer)

    # output_file("interactive_graphs.html")
    # show(plot)