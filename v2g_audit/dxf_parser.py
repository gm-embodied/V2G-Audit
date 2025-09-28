from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from .geometry import Point, Segment
from .symbols import SymbolMatcher
import ezdxf

@dataclass
class DXFPrimitive:
    kind: str                # 'LINE', 'ARC', 'TEXT', 'INSERT'
    data: Dict[str, Any]     # raw fields

def _layer_ok(name: str, include: list, exclude: list) -> bool:
    if include and name not in include: return False
    if exclude and name in exclude: return False
    return True

def _collect_insert(entity, prims: Dict[str, List[DXFPrimitive]], symbol_matcher: SymbolMatcher, layer: str):
    """Collect this INSERT itself (as a symbol)"""
    name = entity.dxf.name if hasattr(entity.dxf, "name") else getattr(entity, "name", "")
    label = symbol_matcher.match(name)
    ins = {
        "layer": layer,
        "name": name,
        "label": label,
        "insert": (entity.dxf.insert.x, entity.dxf.insert.y),
    }
    prims["INSERT"].append(DXFPrimitive("INSERT", ins))

def _collect_from_virtual(insert_ent, prims: Dict[str, List[DXFPrimitive]], symbol_matcher: SymbolMatcher, layers_include: list, layers_exclude: list):
    """
    Expand nested content of an INSERT using virtual_entities().
    All returned entities are already transformed到WCS（带上父块的平移/旋转/缩放）。
    """
    try:
        for ve in insert_ent.virtual_entities():
            lyr = ve.dxf.layer if hasattr(ve, "dxf") else ""
            if not _layer_ok(lyr, layers_include, layers_exclude):
                continue
            dxft = ve.dxftype()
            if dxft == "INSERT":
                # 子块（递归）：记作一个独立的 INSERT，方便 symbols.patterns 匹配（如“接地/接地2 …”）
                _collect_insert(ve, prims, symbol_matcher, lyr)
                # 继续向下展开（有的图库会多层嵌套）
                _collect_from_virtual(ve, prims, symbol_matcher, layers_include, layers_exclude)

            elif dxft in ("TEXT", "MTEXT"):
                # 把块内文字也拉出来，便于“文字驱动识别”
                try:
                    txt = ve.dxf.text if dxft == "TEXT" else ve.text
                except Exception:
                    txt = getattr(ve.dxf, "text", "")
                pos = (ve.dxf.insert.x, ve.dxf.insert.y) if hasattr(ve.dxf, "insert") else (0.0, 0.0)
                prims["TEXT"].append(DXFPrimitive("TEXT", {"layer": lyr, "text": txt, "pos": pos}))

            elif dxft == "LINE":
                p1 = Point(ve.dxf.start.x, ve.dxf.start.y)
                p2 = Point(ve.dxf.end.x,  ve.dxf.end.y)
                prims["LINE"].append(DXFPrimitive("LINE", {"layer": lyr, "segment": Segment(p1, p2)}))

            # 需要的话可继续支持 ARC/CIRCLE 等
    except Exception:
        # 某些旧版DXF/代理实体可能不支持virtual_entities，忽略即可
        pass

def parse_dxf(path: str, layers_include: list, layers_exclude: list, symbol_matcher: SymbolMatcher) -> Dict[str, List[DXFPrimitive]]:
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    prims: Dict[str, List[DXFPrimitive]] = {"LINE": [], "INSERT": [], "TEXT": [], "ARC": []}

    for e in msp:
        layer = e.dxf.layer if hasattr(e, "dxf") else ""
        if not _layer_ok(layer, layers_include, layers_exclude):
            continue

        dxft = e.dxftype()

        if dxft == "LINE":
            p1 = Point(e.dxf.start.x, e.dxf.start.y)
            p2 = Point(e.dxf.end.x,   e.dxf.end.y)
            prims["LINE"].append(DXFPrimitive("LINE", {"layer": layer, "segment": Segment(p1, p2)}))

        elif dxft == "ARC":
            center = e.dxf.center
            prims["ARC"].append(DXFPrimitive("ARC", {"layer": layer, "center": (center.x, center.y),
                                                     "r": e.dxf.radius, "start_angle": e.dxf.start_angle,
                                                     "end_angle": e.dxf.end_angle}))

        elif dxft == "INSERT":
            # 先收顶层 INSERT（CT 会在这里命中）
            _collect_insert(e, prims, symbol_matcher, layer)
            # 再展开子实体（GROUND 常常在这一步命中）
            _collect_from_virtual(e, prims, symbol_matcher, layers_include, layers_exclude)

        elif dxft in ("TEXT", "MTEXT"):
            pos = (e.dxf.insert.x, e.dxf.insert.y)
            txt = e.dxf.text if dxft == "TEXT" else e.text
            prims["TEXT"].append(DXFPrimitive("TEXT", {"layer": layer, "text": txt, "pos": pos}))

    return prims
