from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
from .geometry import Point, Segment, dist, mid_cross_without_junction, is_endpoint
from .symbols import SymbolMatcher

@dataclass
class Node:
    id: str
    type: str
    x: float
    y: float
    attrs: Dict[str, Any]

@dataclass
class Edge:
    u: str
    v: str
    attrs: Dict[str, Any]

def _cluster_points(points: List[Point], tau: float) -> List[Point]:
    # Simple agglomerative clustering by distance threshold
    clusters = []
    for p in points:
        found = False
        for i, c in enumerate(clusters):
            if dist(p, c) <= tau:
                # merge by averaging
                clusters[i] = Point((c.x + p.x)/2.0, (c.y + p.y)/2.0)
                found = True
                break
        if not found:
            clusters.append(p)
    return clusters

def build_property_graph(prims: Dict[str, List[Any]], symbol_matcher: SymbolMatcher, tau_endpoint: float, tau_junction: float, attach_dist: float):
    nodes: List[Node] = []
    edges: List[Edge] = []

    # 1) Collect wire endpoints
    lines = [p.data["segment"] for p in prims.get("LINE", [])]
    endpoints = []
    for s in lines:
        endpoints.extend([s.p1, s.p2])
    clusters = _cluster_points(endpoints, tau_endpoint)

    # 2) Create endpoint nodes
    for i, p in enumerate(clusters):
        nodes.append(Node(id=f"EP{i}", type="ENDPOINT", x=p.x, y=p.y, attrs={}))

    # 3) Map raw endpoints to nearest cluster
    def nearest_cluster(p: Point) -> int:
        dmin, idx = 1e18, -1
        for i, c in enumerate(clusters):
            d = dist(p, c)
            if d < dmin:
                dmin, idx = d, i
        return idx

    # 4) Visual crossing filter & edges
    for seg in lines:
        a_idx = nearest_cluster(seg.p1)
        b_idx = nearest_cluster(seg.p2)
        if a_idx == b_idx:
            continue
        e = Edge(u=f"EP{a_idx}", v=f"EP{b_idx}", attrs={"kind": "WIRE"})
        edges.append(e)

    # TODO: mid-cross filter: ignore crossings that are not at endpoints unless a JUNCTION exists
    # For simplicity in this minimal version, we already only connect endpoints (not mid-cross),
    # so "visual crossing" is implicitly filtered out. If needed, enrich by checking INSERT JUNCTION near intersection.

    # 5) Create symbol nodes
    for ins in prims.get("INSERT", []):
        lab = ins.data.get("label") or "BLOCK"
        x, y = ins.data["insert"]
        nid = f"{lab}_{len(nodes)}"
        nodes.append(Node(id=nid, type=lab, x=x, y=y, attrs={"name": ins.data.get("name")}))

    # 6) Attach nearby text to nearest node
    texts = prims.get("TEXT", [])
    for t in texts:
        tx, ty = t.data["pos"]
        # nearest node
        dmin, idx = 1e18, -1
        for i, n in enumerate(nodes):
            d = ((n.x - tx)**2 + (n.y - ty)**2)**0.5
            if d < dmin:
                dmin, idx = d, i
        if idx >= 0 and dmin <= attach_dist:  # configurable in config.text.attach_distance if desired
            # store concatenated texts
            cur = nodes[idx].attrs.get("texts", [])
            cur.append(t.data["text"])
            nodes[idx].attrs["texts"] = cur

    # 7) Heuristic: connect GROUND to nearest endpoint (snap) within tau_junction
    for n in nodes:
        if n.type == "GROUND":
            # find nearest endpoint cluster
            dmin, ep = 1e18, None
            for e_i, c in enumerate(clusters):
                d = dist(Point(n.x, n.y), c)
                if d < dmin:
                    dmin, ep = d, e_i
            if dmin <= tau_junction and ep is not None:
                edges.append(Edge(u=n.id, v=f"EP{ep}", attrs={"kind": "GROUND_CONN"}))

    # Export graph as dict
    graph = {
        "nodes": [n.__dict__ for n in nodes],
        "edges": [e.__dict__ for e in edges],
    }
    return graph