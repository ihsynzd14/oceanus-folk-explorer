"""
build_meta.py — whole-graph summary for the UI: node/edge counts, connected components,
and per-type counts. Emits data/processed/meta.json (+ public/data copy).
Run: python scripts/build_meta.py
"""
import json
import os
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "data", "raw", "MC1_release", "MC1_graph.json")
OUT_DIR = os.path.join(ROOT, "data", "processed")
SERVED = os.path.join(ROOT, "public", "data")

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)
nodes, links = g["nodes"], g["links"]

# connected components (treat the directed multigraph as undirected)
parent = {n["id"]: n["id"] for n in nodes}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb
for e in links:
    if e["source"] in parent and e["target"] in parent:
        union(e["source"], e["target"])
components = len({find(n["id"]) for n in nodes})

meta = {
    "nodes": len(nodes),
    "edges": len(links),
    "components": components,
    "nodeTypes": dict(Counter(n["Node Type"] for n in nodes).most_common()),
    "edgeTypes": dict(Counter(e["Edge Type"] for e in links).most_common()),
}
for d in (OUT_DIR, SERVED):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

print(f"nodes={meta['nodes']}  edges={meta['edges']}  components={meta['components']}")
print("nodeTypes:", meta["nodeTypes"])
