#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualize a V2G property graph (nodes/edges) from JSON.
- Generates an interactive HTML (via pyvis, if installed).
- Generates a static PNG (via matplotlib).

Usage:
  python visualize_graph.py --graph out/graph.json --out out_vis --title "My Schematic Graph"
"""

import os
import json
import argparse
from typing import Dict, Any

import networkx as nx
import matplotlib.pyplot as plt

# Try to import pyvis for interactive HTML
try:
    from pyvis.network import Network
    _has_pyvis = True
except Exception:
    _has_pyvis = False


def load_graph(graph_path: str) -> Dict[str, Any]:
    with open(graph_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_nx_graph(gdict: Dict[str, Any]) -> nx.Graph:
    G = nx.Graph()
    for n in gdict.get("nodes", []):
        G.add_node(n["id"], **n)
    for e in gdict.get("edges", []):
        G.add_edge(e["u"], e["v"], **e.get("attrs", {}))
    return G


def make_positions(gdict: Dict[str, Any]) -> Dict[str, tuple]:
    pos = {}
    for n in gdict.get("nodes", []):
        if "x" in n and "y" in n:
            pos[n["id"]] = (float(n["x"]), float(n["y"]))
    return pos


def draw_png(G, pos, out_png, title=""):
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.patches import Patch

    plt.figure(figsize=(14, 10))

    # —— 边：按 kind 分样式 ——
    wire_edges   = [(u, v) for u, v, d in G.edges(data=True) if d.get("kind") == "WIRE"]
    ground_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("kind") == "GROUND_CONN"]

    nx.draw_networkx_edges(G, pos, edgelist=wire_edges,   width=0.8,  edge_color="#888888")
    nx.draw_networkx_edges(G, pos, edgelist=ground_edges, width=1.6,  edge_color="#2ca02c", style="dashed")

    # —— 节点：不同 type 分色 + 分尺寸 ——
    COLOR = {
        "GROUND": "#2ca02c",       # 绿色
        "CT": "#d62728",           # 红色
        "BREAKER": "#ff7f0e",      # 橙色
        "TERMINAL_BOX": "#9467bd", # 紫色
        "BUS": "#1f77b4",          # 蓝色
        "BLOCK": "#8c8c8c",        # 未识别块
        "ENDPOINT": "#7f7f7f",     # 端点灰
    }
    SIZE = {
        "GROUND": 900,
        "CT": 900,
        "BREAKER": 800,
        "TERMINAL_BOX": 800,
        "BUS": 800,
        "BLOCK": 600,
        "ENDPOINT": 120,
    }

    # 根据类型分组画点
    types = {}
    for n, d in G.nodes(data=True):
        t = d.get("type", "OTHER")
        types.setdefault(t, []).append(n)

    for t, nodes in types.items():
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodes,
            node_color=COLOR.get(t, "#aaaaaa"),
            node_size=SIZE.get(t, 300),
            edgecolors="#333333", linewidths=0.5,
        )

    # —— 标签：只给语义节点打（type + 最多两条挂靠文字） ——
    labels = {}
    for n, d in G.nodes(data=True):
        if d.get("type") != "ENDPOINT":
            texts = d.get("attrs", {}).get("texts", [])
            extra = (" " + "/".join(map(str, texts[:2]))) if texts else ""
            labels[n] = f"{d.get('type')}{extra}"
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

    # —— 图例（不包含 ENDPOINT） ——
    legend_patches = [
        Patch(facecolor=COLOR[k], edgecolor="#333333", label=k)
        for k in ["GROUND", "CT", "BREAKER", "TERMINAL_BOX", "BUS", "BLOCK"]
        if k in types
    ]
    if legend_patches:
        plt.legend(handles=legend_patches, fontsize=9, loc="upper right")

    plt.title(title or "V2G Graph", fontsize=14)
    plt.subplots_adjust(top=0.95, right=0.98, left=0.02, bottom=0.02)
    plt.savefig(out_png, dpi=240)
    plt.close()



def draw_html(G, out_html, title=""):
    if not _has_pyvis:
        raise RuntimeError("pyvis is not installed. Run `pip install pyvis jinja2`")
    from pyvis.network import Network
    import json

    COLOR = {
        "GROUND": "#2ca02c",
        "CT": "#d62728",
        "BREAKER": "#ff7f0e",
        "TERMINAL_BOX": "#9467bd",
        "BUS": "#1f77b4",
        "BLOCK": "#8c8c8c",
        "ENDPOINT": "#7f7f7f",
    }
    SIZE = {
        "GROUND": 28,
        "CT": 28,
        "BREAKER": 24,
        "TERMINAL_BOX": 24,
        "BUS": 24,
        "BLOCK": 18,
        "ENDPOINT": 6,
    }

    net = Network(height="850px", width="100%", directed=False, notebook=False, bgcolor="#ffffff")
    net.barnes_hut()

    # 节点：ENDPOINT 不打 label，语义节点显示 type + 两条文本
    for n, d in G.nodes(data=True):
        t = d.get("type", "NODE")
        texts = d.get("attrs", {}).get("texts", [])
        label = "" if t == "ENDPOINT" else f"{t}\n{'/'.join(map(str, texts[:2]))}" if texts else t
        try:
            tip = json.dumps(d.get("attrs", {}), ensure_ascii=False)
        except Exception:
            tip = str(d.get("attrs", {}))
        net.add_node(
            n,
            label=label,
            title=tip,
            color=COLOR.get(t, "#aaaaaa"),
            size=SIZE.get(t, 10),
        )

    # 边：用 kind 作标签
    for u, v, ed in G.edges(data=True):
        net.add_edge(u, v, label=str(ed.get("kind", "")))

    net.set_options(
        '{"physics":{"stabilization":true},'
        ' "interaction":{"hover":true,"dragNodes":true,"zoomView":true}}'
    )

    # 避免 show() 的模板依赖问题，直接写 HTML
    try:
        net.write_html(out_html, notebook=False)
    except Exception:
        net.save_graph(out_html)




def main():
    ap = argparse.ArgumentParser(description="Visualize V2G graph JSON as HTML/PNG")
    ap.add_argument("--graph", required=True, help="Path to graph.json")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--title", default="V2G Graph", help="Figure/HTML title")
    ap.add_argument("--no-html", action="store_true", help="Skip HTML export")
    ap.add_argument("--no-png", action="store_true", help="Skip PNG export")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    gdict = load_graph(args.graph)
    G = build_nx_graph(gdict)
    pos = make_positions(gdict)

    if not args.no_png:
        out_png = os.path.join(args.out, "graph.png")
        draw_png(G, pos, out_png, title=args.title)
        print(f"[OK] PNG saved: {out_png}")

    if not args.no_html:
        try:
            out_html = os.path.join(args.out, "graph.html")
            draw_html(G, out_html, title=args.title)
            print(f"[OK] HTML saved: {out_html}")
        except Exception as e:
            print(f"[WARN] HTML export skipped: {e}")


if __name__ == "__main__":
    main()
