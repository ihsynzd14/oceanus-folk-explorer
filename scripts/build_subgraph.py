"""
build_subgraph.py — derive a slim, browser-ready ego-network around Sailor Shift.

Influence in MC1 is encoded at the WORK level. We project it to PEOPLE:
  PersonA --created--> WorkS --influence--> WorkT <--created-- PersonB
  ==> PersonB influenced PersonA  (target of an influence edge = the influencer).
We then take Sailor Shift's k-hop neighborhood on that person-influence graph and
emit nodes + influence edges + collaboration edges to data/processed/sailor_ego.json.

Run: python scripts/build_subgraph.py [hops]   (default hops=1, the readable view)
"""
import json
import os
import sys
from collections import Counter, defaultdict, deque

try:  # Windows consoles default to cp1252 and choke on names like "Nørgaard"
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "data", "raw", "MC1_release", "MC1_graph.json")
OUT_DIR = os.path.join(ROOT, "data", "processed")
SAILOR_ID = 17255
HOPS = int(sys.argv[1]) if len(sys.argv) > 1 else 1

INFLUENCE = {"InStyleOf", "InterpolatesFrom", "CoverOf", "LyricalReferenceTo", "DirectlySamples"}
CREATOR = {"PerformerOf", "ComposerOf", "LyricistOf"}  # Person -> Work (authorship for influence)
COLLAB = {"PerformerOf", "ComposerOf", "LyricistOf", "ProducerOf"}

os.makedirs(OUT_DIR, exist_ok=True)
with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)

node = {n["id"]: n for n in g["nodes"]}
def ntype(i): return node[i]["Node Type"] if i in node else None

# ---- maps ----
creators_of = defaultdict(set)   # work id -> {person ids who created it}
works_of = defaultdict(set)      # person id -> {work ids they created}
members_of = defaultdict(set)    # group id -> {person ids}
for e in g["links"]:
    t, s, d = e["Edge Type"], e["source"], e["target"]
    if t in CREATOR and ntype(s) == "Person" and ntype(d) in ("Song", "Album"):
        creators_of[d].add(s); works_of[s].add(d)
    if t == "MemberOf" and ntype(s) == "Person" and ntype(d) == "MusicalGroup":
        members_of[d].add(s)

def people_behind(i):
    """Resolve a node to the set of people it represents (for influence projection)."""
    tp = ntype(i)
    if tp == "Person": return {i}
    if tp in ("Song", "Album"): return creators_of.get(i, set())
    if tp == "MusicalGroup": return members_of.get(i, set())
    return set()

# ---- person-level influence + collaboration ----
# influence[(influenced, influencer)] -> Counter of edge types
infl = defaultdict(Counter)
for e in g["links"]:
    if e["Edge Type"] not in INFLUENCE:
        continue
    s, d = e["source"], e["target"]          # s = newer/influenced work, d = older/influencer
    influenced = people_behind(s)
    influencer = people_behind(d)
    for a in influenced:
        for b in influencer:
            if a != b:
                infl[(a, b)][e["Edge Type"]] += 1

# collaboration: people sharing a work
collab = Counter()
for w, ppl in creators_of.items():
    ppl = sorted(ppl)
    for i in range(len(ppl)):
        for j in range(i + 1, len(ppl)):
            collab[(ppl[i], ppl[j])] += 1

# ---- person-influence adjacency (undirected for BFS neighborhood) ----
adj = defaultdict(set)
for (a, b) in infl:
    adj[a].add(b); adj[b].add(a)

# ---- BFS ego-network from Sailor ----
hop = {SAILOR_ID: 0}
q = deque([SAILOR_ID])
while q:
    cur = q.popleft()
    if hop[cur] >= HOPS:
        continue
    for nb in adj[cur]:
        if nb not in hop:
            hop[nb] = hop[cur] + 1
            q.append(nb)
ego = set(hop)

# ---- node attributes ----
def year_of(work):
    w = node[work]
    for k in ("notoriety_date", "release_date", "written_date"):
        v = w.get(k)
        if v and str(v).strip().isdigit():
            return int(v)
    return None

def person_record(pid):
    ws = works_of.get(pid, set())
    years = [year_of(w) for w in ws]
    years = [y for y in years if y]
    genres = Counter(node[w].get("genre") for w in ws if node[w].get("genre"))
    return {
        "id": pid,
        "name": node[pid].get("name"),
        "stage_name": node[pid].get("stage_name"),
        "hop": hop[pid],
        "year": min(years) if years else None,
        "active_to": max(years) if years else None,
        "n_works": len(ws),
        "n_notable": sum(1 for w in ws if node[w].get("notable")),
        "top_genre": genres.most_common(1)[0][0] if genres else None,
        "oceanus_works": sum(1 for w in ws if node[w].get("genre") == "Oceanus Folk"),
    }

nodes_out = [person_record(p) for p in sorted(ego)]
infl_out = [
    {"source": a, "target": b, "weight": sum(c.values()), "types": dict(c)}
    for (a, b), c in infl.items() if a in ego and b in ego
]
collab_out = [
    {"source": a, "target": b, "weight": w}
    for (a, b), w in collab.items() if a in ego and b in ego
]

out = {"center": SAILOR_ID, "hops": HOPS,
       "nodes": nodes_out, "influence": infl_out, "collab": collab_out}
# Default 1-hop is sailor_ego.json (used by the app); larger hops get suffixed.
fname = "sailor_ego.json" if HOPS == 1 else f"sailor_ego_{HOPS}hop.json"
out_path = os.path.join(OUT_DIR, fname)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
served = os.path.join(ROOT, "public", "data")
os.makedirs(served, exist_ok=True)
with open(os.path.join(served, fname), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

# ---- stats ----
def nm(i): return node[i].get("stage_name") or node[i].get("name")
influencers_of_sailor = [(b, c) for (a, b), c in infl.items() if a == SAILOR_ID]
influenced_by_sailor = [(a, c) for (a, b), c in infl.items() if b == SAILOR_ID]
print(f"hops={HOPS}  ego people={len(ego)}  influence edges={len(infl_out)}  collab edges={len(collab_out)}")
print("hop sizes:", dict(Counter(hop.values())))
print(f"Sailor: influenced BY {len(influencers_of_sailor)} people | influenced {len(influenced_by_sailor)} people (1-hop direct)")
print("\nTOP 15 WHO INFLUENCED SAILOR (target=influencer):")
for b, c in sorted(influencers_of_sailor, key=lambda x: -sum(x[1].values()))[:15]:
    print(f"  Sailor <- {nm(b):28} {dict(c)}")
print("\nTOP 15 WHOM SAILOR INFLUENCED:")
for a, c in sorted(influenced_by_sailor, key=lambda x: -sum(x[1].values()))[:15]:
    print(f"  {nm(a):28} <- Sailor  {dict(c)}")
print(f"\nwrote {out_path} ({os.path.getsize(out_path)} bytes)")
