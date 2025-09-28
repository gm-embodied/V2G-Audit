from typing import Dict, Any, List
import json

class RuleEngine:
    def __init__(self, verifier):
        self.verifier = verifier
        self.funcs = {
            "check_grounding_uniqueness": self.verifier.check_grounding_uniqueness,
            "check_open_circuit": self.verifier.check_open_circuit,
            "check_inter_circuit_short": self.verifier.check_inter_circuit_short,
            "check_polarity_consistency": self.verifier.check_polarity_consistency,
        }

    def run(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        for r in rules.get("rules", []):
            region = r.get("region", "All")
            fn = r.get("function")
            if fn not in self.funcs:
                results.append({"region": region, "function": fn, "status": False, "detail": "Unknown function"})
                continue
            out = self.funcs[fn](region)
            results.append(out)
        return {"results": results}