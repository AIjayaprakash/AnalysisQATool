# Create unified node-edge JSON for visualization, also compute layout placeholders
import networkx as nx
from typing import List, Dict, Any
import uuid

def build_graph_from_nodes_edges(nodes: List[Dict[str,Any]], edges: List[Dict[str,Any]]):
    G = nx.DiGraph()
    for n in nodes:
        nid = n["id"]
        label = n.get("label", nid)
        G.add_node(nid, **n)

    for e in edges:
        eid = e.get("id", f"edge-{uuid.uuid4().hex[:8]}")
        G.add_edge(e["source"], e["target"], id=eid, action=e.get("action",""))

    # compute naive positions if missing: simple left-to-right layering by BFS
    positions = {}
    try:
        layers = list(nx.topological_generations(G))
    except Exception:
        layers = [list(G.nodes())]
    y_gap = 120
    x_gap = 220
    for li, layer in enumerate(layers):
        for i, node in enumerate(layer):
            x = i * x_gap
            y = li * y_gap
            pos = {"x": x, "y": y}
            positions[node] = pos
            # attach to node data
            G.nodes[node]["position"] = pos

    # prepare node & edge arrays for frontend libs
    nodes_out = []
    for n in G.nodes(data=True):
        nodes_out.append({
            "id": n[0],
            "data": {"label": n[1].get("label", n[0]), "attributes": n[1].get("attributes", {})},
            "position": n[1].get("position", {"x":0,"y":0}),
            "type": n[1].get("type")
        })
    edges_out = []
    for u,v,data in G.edges(data=True):
        edges_out.append({
            "id": data.get("id", f"edge-{uuid.uuid4().hex[:8]}"),
            "source": u,
            "target": v,
            "label": data.get("action","")
        })
    return {"nodes": nodes_out, "edges": edges_out}
