from typing import Dict, Any
import json, os

def write_reports(graph: Dict[str, Any], results: Dict[str, Any], outdir: str):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    # human summary
    lines = []
    for r in results.get("results", []):
        status = "PASS" if r.get("status") else "FAIL"
        lines.append(f"[{status}] {r.get('function')} @ {r.get('region')}: {r.get('detail')}")
    with open(os.path.join(outdir, "report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))