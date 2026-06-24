"""
build_genre_spread.py — global view for MC1 Task 2: how Oceanus Folk spread.

Outward spread: an influence edge source(S) -> target(T) means S drew from T.
  - T is Oceanus Folk  ==> Oceanus Folk INFLUENCED S. S's genre = a genre OF reached;
    S's release year = when that spread happened; S's creators = artists affected.
  - S is Oceanus Folk  ==> Oceanus Folk DREW FROM T (genre T = an inspiration source).

Emits data/processed/genre_spread.json (+ public/data copy).
Run: python scripts/build_genre_spread.py
"""
import json
import os
import sys
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "data", "raw", "MC1_release", "MC1_graph.json")
OUT_DIR = os.path.join(ROOT, "data", "processed")
SERVED = os.path.join(ROOT, "public", "data")
GENRE = "Oceanus Folk"
INFLUENCE = {"InStyleOf", "InterpolatesFrom", "CoverOf", "LyricalReferenceTo", "DirectlySamples"}
CREATOR = {"PerformerOf", "ComposerOf", "LyricistOf"}
WORK = ("Song", "Album")

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)
node = {n["id"]: n for n in g["nodes"]}
def ntype(i): return node[i]["Node Type"] if i in node else None
def genre_of(i): return node[i].get("genre") if i in node else None
def year_of(i):
    w = node.get(i, {})
    for k in ("release_date", "notoriety_date", "written_date"):
        v = w.get(k)
        if v and str(v).strip().isdigit():
            return int(v)
    return None

creators_of = defaultdict(set)
for e in g["links"]:
    if e["Edge Type"] in CREATOR and ntype(e["source"]) == "Person" and ntype(e["target"]) in WORK:
        creators_of[e["target"]].add(e["source"])

of_releases = Counter()                       # year -> # Oceanus Folk works released
spread_works = defaultdict(set)               # (year, genre) -> set of influenced work ids
drew_from = Counter()                          # genre -> count (OF drawing from it)
influenced_genres = Counter()                  # genre -> count of influenced works
affected_artist_works = defaultdict(set)       # person -> set of their works influenced by OF

for i, n in node.items():
    if n.get("genre") == GENRE and ntype(i) in WORK:
        y = year_of(i)
        if y:
            of_releases[y] += 1

for e in g["links"]:
    if e["Edge Type"] not in INFLUENCE:
        continue
    s, t = e["source"], e["target"]
    gs, gt = genre_of(s), genre_of(t)
    # Oceanus Folk influenced S
    if gt == GENRE and ntype(s) in WORK:
        y = year_of(s)
        if y and gs:
            spread_works[(y, gs)].add(s)
        if gs:
            influenced_genres[gs] += 1
        for p in creators_of.get(s, ()):
            affected_artist_works[p].add(s)
    # Oceanus Folk drew from T
    if gs == GENRE and ntype(t) in WORK and gt:
        drew_from[gt] += 1

spread = [{"year": y, "genre": gn, "count": len(ids)} for (y, gn), ids in spread_works.items()]
spread.sort(key=lambda d: (d["year"], -d["count"]))
years = [y for (y, _) in spread_works] + list(of_releases)
year_range = [min(years), max(years)] if years else [0, 0]

top_artists = sorted(affected_artist_works.items(), key=lambda kv: -len(kv[1]))[:15]
top_affected = [
    {"id": p, "name": node[p].get("stage_name") or node[p].get("name"),
     "works_influenced": len(ws)}
    for p, ws in top_artists
]

out = {
    "genre": GENRE,
    "yearRange": year_range,
    "ofReleasesByYear": {str(k): v for k, v in sorted(of_releases.items())},
    "spread": spread,
    "drewFrom": [{"genre": k, "count": v} for k, v in drew_from.most_common()],
    "influencedGenres": [{"genre": k, "count": v} for k, v in influenced_genres.most_common()],
    "topAffectedArtists": top_affected,
}
for d in (OUT_DIR, SERVED):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "genre_spread.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

# ---- summary ----
print(f"year range: {year_range}")
print(f"Oceanus Folk works released: {sum(of_releases.values())}")
print(f"distinct influenced works (OF -> others): {sum(len(v) for v in spread_works.values())}")
print(f"genres OF influenced: {len(influenced_genres)}  | genres OF drew from: {len(drew_from)}")
print("\nTOP GENRES OCEANUS FOLK INFLUENCED:")
for k, v in influenced_genres.most_common(12):
    print(f"  {k:28} {v}")
print("\nTOP GENRES OCEANUS FOLK DREW FROM:")
for k, v in drew_from.most_common(12):
    print(f"  {k:28} {v}")
print("\nTOP AFFECTED ARTISTS:")
for a in top_affected[:8]:
    print(f"  {a['name']:28} {a['works_influenced']} works")
print("\nOF RELEASES BY YEAR (nonzero):")
print("  " + ", ".join(f"{y}:{c}" for y, c in sorted(of_releases.items())))
