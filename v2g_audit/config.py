import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class Tolerance:
    tau_endpoint_snap: float = 2.0
    tau_junction_snap: float = 2.0

@dataclass
class LayerConfig:
    include: list = field(default_factory=list)
    exclude: list = field(default_factory=list)

@dataclass
class SymbolsConfig:
    patterns: Dict[str, List[str]]

@dataclass
class TextConfig:
    attach_distance: float = 3.0

@dataclass
class WireConfig:
    layers: List[str] = field(default_factory=list)

@dataclass
class Config:
    tolerance: Tolerance
    layers: LayerConfig
    symbols: SymbolsConfig
    text: TextConfig
    wires: WireConfig

def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    tol = data.get("tolerance", {})
    layers = data.get("layers", {})
    symbols = data.get("symbols", {})
    text = data.get("text", {})
    wires = data.get("wires", {})

    return Config(
        tolerance=Tolerance(**tol),
        layers=LayerConfig(**layers),
        symbols=SymbolsConfig(patterns=symbols),
        text=TextConfig(**text),
        wires=WireConfig(**wires)
    )