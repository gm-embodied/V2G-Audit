import re
from typing import Dict, List, Optional

class SymbolMatcher:
    def __init__(self, patterns: Dict[str, List[str]]):
        self._compiled = {
            k: [re.compile(pat, re.IGNORECASE) for pat in v]
            for k, v in patterns.items()
        }

    def match(self, name: str) -> Optional[str]:
        for label, regs in self._compiled.items():
            for r in regs:
                if r.search(name or ''):
                    return label
        return None