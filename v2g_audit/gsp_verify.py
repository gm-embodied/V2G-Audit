from typing import Dict, Any, List, Tuple, Set
import numpy as np
import networkx as nx
from collections import defaultdict

class GSPVerifier:
    def __init__(self, graph: Dict[str, Any]):
        self.graph = graph
        self.G = nx.Graph()
        for n in graph["nodes"]:
            self.G.add_node(n["id"], **n)
        for e in graph["edges"]:
            self.G.add_edge(e["u"], e["v"], **e["attrs"])

    # ---------- helpers ----------
    def _subgraph_by_region(self, region: str) -> nx.Graph:
        if region == "All":
            return self.G
        # region-based selection example: CT_secondary -> nodes within k hops of CT and ENDPOINT
        # Simplified: all nodes connected to any CT
        ct_nodes = [n for n, d in self.G.nodes(data=True) if d.get("type") == "CT"]
        if not ct_nodes:
            return self.G  # fallback
        comp = set()
        for ct in ct_nodes:
            # collect connected component containing CT
            for cc in nx.connected_components(self.G):
                if ct in cc:
                    comp |= set(cc)
        return self.G.subgraph(comp).copy()

    def _ground_count(self, G: nx.Graph) -> int:
        return sum(1 for _, d in G.nodes(data=True) if d.get("type") == "GROUND")

    def _is_connected(self, G: nx.Graph) -> bool:
        if G.number_of_nodes() == 0:
            return True
        return nx.is_connected(G)

    # ---------- verifiers ----------
    def check_grounding_uniqueness(self, region: str) -> Dict[str, Any]:
        H = self._subgraph_by_region(region)
        g = self._ground_count(H)
        if g == 1:
            status = True; detail = "Exactly one grounding node."
        elif g == 0:
            status = False; detail = "Missing grounding."
        else:
            status = False; detail = f"Multiple grounding nodes: {g}."
        return {"function": "check_grounding_uniqueness", "region": region, "status": status, "detail": detail, "ground_count": g}

    def check_open_circuit(self, region: str) -> Dict[str, Any]:
        H = self._subgraph_by_region(region)
        # Heuristic: any ENDPOINT with degree 1 that is not connected to a TERMINAL/BREAKER could indicate open end
        deg = dict(H.degree())
        suspects = []
        for n, d in H.nodes(data=True):
            if d.get("type") == "ENDPOINT" and deg.get(n, 0) <= 1:
                # check if adjacent to terminal-like elements
                nbrs = list(H.neighbors(n))
                if not any(H.nodes[v].get("type") in ("BREAKER", "TERMINAL_BOX") for v in nbrs):
                    suspects.append(n)
        status = (len(suspects) == 0)
        return {"function": "check_open_circuit", "region": region, "status": status, "detail": f"open endpoints: {suspects}"}

    def check_inter_circuit_short(self, region: str) -> Dict[str, Any]:
        H = self._subgraph_by_region(region)
        # Simplified heuristic: if distinct CT-connected components get bridged by a wire, flag
        # Here we approximate: multiple CT nodes in same connected component -> potential inter-circuit short
        ct_nodes = [n for n, d in H.nodes(data=True) if d.get("type") == "CT"]
        status = True; detail = "OK"
        if len(ct_nodes) >= 2:
            # if they are in same connected component, flag as possible short (depending on domain)
            comps = list(nx.connected_components(H))
            for comp in comps:
                if sum(1 for c in ct_nodes if c in comp) >= 2:
                    status = False; detail = "Multiple CTs in one connected component (possible inter-circuit short)."
                    break
        return {"function": "check_inter_circuit_short", "region": region, "status": status, "detail": detail}

    def check_polarity_consistency(self, region: str) -> Dict[str, Any]:
        H = self._subgraph_by_region(region)
        # Example attribute check: all nodes with attrs['polarity'] must match along an edge (if both sides have polarity)
        violations = []
        for u, v in H.edges():
            pu = H.nodes[u].get("attrs", {}).get("polarity")
            pv = H.nodes[v].get("attrs", {}).get("polarity")
            if pu is not None and pv is not None and pu != pv:
                violations.append((u, v, pu, pv))
        status = (len(violations) == 0)
        return {"function": "check_polarity_consistency", "region": region, "status": status, "detail": f"violations: {violations}"}