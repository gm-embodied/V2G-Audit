import argparse, json, os, sys
from .config import load_config
from .symbols import SymbolMatcher
from .dxf_parser import parse_dxf
from .graph_builder import build_property_graph
from .gsp_verify import GSPVerifier
from .rules import RuleEngine
from .report import write_reports

def main():
    ap = argparse.ArgumentParser(description="V2G-style DXF schematic auditor")
    ap.add_argument("--dxf", required=True, help="Path to DXF file")
    ap.add_argument("--config", required=True, help="Path to YAML config")
    ap.add_argument("--rules", required=True, help="Path to rules JSON")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--tau", type=float, default=None, help="Override endpoint snap tolerance")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.tau is not None:
        cfg.tolerance.tau_endpoint_snap = args.tau

    matcher = SymbolMatcher(cfg.symbols.patterns)
    prims = parse_dxf(args.dxf, cfg.layers.include, cfg.layers.exclude, matcher)

    graph = build_property_graph(prims, matcher, cfg.tolerance.tau_endpoint_snap, cfg.tolerance.tau_junction_snap, cfg.text.attach_distance)

    verifier = GSPVerifier(graph)
    engine = RuleEngine(verifier)

    with open(args.rules, "r", encoding="utf-8") as f:
        rules = json.load(f)
    results = engine.run(rules)

    write_reports(graph, results, args.out)
    print(f"Done. Outputs saved to {args.out}")

if __name__ == "__main__":
    main()