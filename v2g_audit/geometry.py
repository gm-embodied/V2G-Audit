from dataclasses import dataclass
from typing import Tuple, List, Optional
import math

@dataclass(frozen=True)
class Point:
    x: float
    y: float

def dist(a: Point, b: Point) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)

@dataclass
class Segment:
    p1: Point
    p2: Point

def _orientation(a: Point, b: Point, c: Point) -> int:
    val = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)
    if abs(val) < 1e-9: return 0
    return 1 if val > 0 else 2

def _on_segment(a: Point, b: Point, c: Point) -> bool:
    return min(a.x, c.x) - 1e-9 <= b.x <= max(a.x, c.x) + 1e-9 and            min(a.y, c.y) - 1e-9 <= b.y <= max(a.y, c.y) + 1e-9

def segments_intersect(s1: Segment, s2: Segment) -> bool:
    a, b, c, d = s1.p1, s1.p2, s2.p1, s2.p2
    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)
    if o1 != o2 and o3 != o4: return True
    # Colinear special cases
    if o1 == 0 and _on_segment(a, c, b): return True
    if o2 == 0 and _on_segment(a, d, b): return True
    if o3 == 0 and _on_segment(c, a, d): return True
    if o4 == 0 and _on_segment(c, b, d): return True
    return False

def intersection_point(s1: Segment, s2: Segment) -> Optional[Point]:
    # Compute intersection point (if not parallel), else None
    x1, y1, x2, y2 = s1.p1.x, s1.p1.y, s1.p2.x, s1.p2.y
    x3, y3, x4, y4 = s2.p1.x, s2.p1.y, s2.p2.x, s2.p2.y
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom) < 1e-12:
        return None
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom
    p = Point(px, py)
    # Ensure within both segments
    if _on_segment(s1.p1, p, s1.p2) and _on_segment(s2.p1, p, s2.p2):
        return p
    return None

def is_endpoint(p: Point, s: Segment, tau: float) -> bool:
    return dist(p, s.p1) <= tau or dist(p, s.p2) <= tau

def mid_cross_without_junction(s1: Segment, s2: Segment, tau: float) -> bool:
    # Returns True if the intersection is not near any endpoint (i.e., a "visual crossing")
    if not segments_intersect(s1, s2):
        return False
    ip = intersection_point(s1, s2)
    if ip is None:
        return False
    # If intersection is far from all endpoints -> likely mid-crossing
    return (not is_endpoint(ip, s1, tau)) and (not is_endpoint(ip, s2, tau))