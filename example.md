
# V2G-Audit (Lightweight)

A practical, end-to-end pipeline to audit electrical schematics from **DXF** using a **Vector-to-Graph (V2G)** transformation
and **Graph Signal Processing (GSP)** checks. It follows four stages:

1. **DXF → Primitives** (`ezdxf`): extract LINE/ARC/TEXT/INSERT.
2. **Primitives → Property Graph**: group blocks to components, cluster/snap endpoints within tolerance `tau`, build edges while filtering "visual crossings".
3. **GSP Verifier**: run deterministic checks (connectivity, attribute consistency, grounding uniqueness, loop/short detection).
4. **Compliance Report**: structured JSON + human-readable summary.

> This repository is intentionally lightweight and _project-ready_. You can extend symbol rules, add new verifiers, or integrate with your own benchmark.

## Quickstart

```bash
pip install -r requirements.txt
python -m v2g_audit.cli --dxf your.dxf --out out --tau 2.0   --config examples/sample_config.yaml --rules examples/sample_rules.json
```

Outputs go to `out/`:
- `graph.json`: property graph (nodes/edges/attributes)
- `report.json`: compliance results
- `report.txt`: human-readable summary

## Key Ideas

- **Endpoint snap within τ**: endpoints closer than `tau` are considered connected _unless_ it's a **visual crossing** (mid-segment cross without junction node).
- **Deterministic math**: verifications use graph algebra (adjacency, Laplacian) or exact combinatorial logic.
- **Planner hook**: `rules.json` mimics MLLM planner output (region + function). You can plug your own planner if needed.

## Notes

- Provide a **block-name mapping** in config (e.g., `GROUND`, `CT`, `BREAKER`, `JUNCTION`) to maximize accuracy.
- Visual crossing filter assumes that **only endpoints** imply connections unless a `JUNCTION` block exists at the cross.
- For very noisy DXFs, you may need to refine symbol regex and layer filters in `examples/sample_config.yaml`.
