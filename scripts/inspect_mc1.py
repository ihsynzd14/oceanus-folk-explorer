"""
inspect_mc1.py — download MC1_release.zip, extract, and print the real graph schema.
First data step per CLAUDE.md: confirm node/edge types, counts, properties before designing widgets.
Run: python scripts/inspect_mc1.py
"""
import json
import os
import urllib.request
import zipfile
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
ZIP_URL = "https://raw.githubusercontent.com/vast-challenge/2025-data/main/MC1_release.zip"
ZIP_PATH = os.path.join(RAW, "MC1_release.zip")

os.makedirs(RAW, exist_ok=True)

# 1. download
if not os.path.exists(ZIP_PATH):
    print(f"Downloading {ZIP_URL} ...")
    urllib.request.urlretrieve(ZIP_URL, ZIP_PATH)
print(f"zip: {ZIP_PATH} ({os.path.getsize(ZIP_PATH)} bytes)")

# 2. extract
with zipfile.ZipFile(ZIP_PATH) as z:
    names = z.namelist()
    print("zip contents:", names)
    z.extractall(RAW)

# 3. locate the graph json
json_files = [n for n in names if n.lower().endswith(".json")]
graph_path = os.path.join(RAW, json_files[0])
print(f"\nLoading graph: {graph_path}")
with open(graph_path, encoding="utf-8") as f:
    g = json.load(f)

print("\n=== TOP-LEVEL KEYS ===")
for k, v in g.items():
    kind = type(v).__name__
    n = len(v) if isinstance(v, (list, dict)) else v
    print(f"  {k}: {kind} (len/val={n})")

nodes = g.get("nodes", [])
links = g.get("links", g.get("edges", []))
print(f"\nNODES: {len(nodes)}    LINKS: {len(links)}")

# 4. node types + properties
node_types = Counter(n.get("Node Type", n.get("type")) for n in nodes)
print("\n=== NODE TYPES ===")
for t, c in node_types.most_common():
    print(f"  {t}: {c}")

props_by_type = defaultdict(set)
for n in nodes:
    t = n.get("Node Type", n.get("type"))
    props_by_type[t].update(n.keys())
print("\n=== NODE PROPERTIES BY TYPE ===")
for t in node_types:
    print(f"  {t}: {sorted(props_by_type[t])}")

# 5. edge types
edge_types = Counter(e.get("Edge Type", e.get("type")) for e in links)
print("\n=== EDGE TYPES ===")
for t, c in edge_types.most_common():
    print(f"  {t}: {c}")
edge_props = set()
for e in links:
    edge_props.update(e.keys())
print(f"\nEDGE PROPERTIES (union): {sorted(edge_props)}")

# 6. find Sailor Shift
def name_of(n):
    return n.get("name") or n.get("stage_name") or n.get("label") or ""

sailor = [n for n in nodes if "sailor shift" in str(name_of(n)).lower()]
print("\n=== SAILOR SHIFT NODE(S) ===")
for s in sailor:
    print(" ", json.dumps(s, ensure_ascii=False))

# 7. one sample per node type
print("\n=== SAMPLE NODE PER TYPE ===")
seen = set()
for n in nodes:
    t = n.get("Node Type", n.get("type"))
    if t not in seen:
        seen.add(t)
        print(f"  [{t}] {json.dumps(n, ensure_ascii=False)[:300]}")

# 8. sample link
print("\n=== SAMPLE LINKS ===")
for e in links[:5]:
    print("  ", json.dumps(e, ensure_ascii=False)[:200])
