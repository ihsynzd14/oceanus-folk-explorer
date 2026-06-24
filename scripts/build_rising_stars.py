"""
build_rising_stars.py — MC1 Task 3: profile rising stars, compare trajectories, predict next.

Data reality: influence edges are sparse and their endpoints may be works OR people OR
groups (the official doc says "source is a Song/Album", but the data also has group/person
sources). So influence is projected to PEOPLE by resolving both endpoints to artists
(work -> its creators, group -> its members, person -> itself), exactly like the ego build.

Popularity is the cleanest rising-star signal: every `notable` work carries a year
(notoriety_date = when it charted). The career trajectory is therefore the cumulative
count of notable works over time; influence reach is a secondary, static magnitude.

Rising Star Score (transparent, 5 normalized parts):
  recentNotable  chart hits in the last RECENT years (popularity, magnitude)
  notableGrowth  recent notable minus prior notable (acceleration)
  influenceReach distinct downstream artists influenced (peer impact)
  oceanusAffinity share of the artist's works that are Oceanus Folk
  youth          recency of debut (shorter career = more upside)

Emits data/processed/rising_stars.json (+ public/data copy).
Run: python scripts/build_rising_stars.py
"""
import json
import math
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
SAILOR_ID = 17255
GENRE = "Oceanus Folk"
INFLUENCE = {"InStyleOf", "InterpolatesFrom", "CoverOf", "LyricalReferenceTo", "DirectlySamples"}
CREATOR = {"PerformerOf", "ComposerOf", "LyricistOf"}
WORK = ("Song", "Album")
RECENT = 5
WEIGHTS = {"recentNotable": 0.30, "notableGrowth": 0.20, "influenceReach": 0.20,
           "oceanusAffinity": 0.20, "youth": 0.10}

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)
node = {n["id"]: n for n in g["nodes"]}
def ntype(i): return node[i]["Node Type"] if i in node else None
def genre_of(i): return node.get(i, {}).get("genre")
def release_year(i):
    w = node.get(i, {})
    for k in ("release_date", "written_date", "notoriety_date"):
        v = w.get(k)
        if v and str(v).strip().isdigit():
            return int(v)
    return None
def notable_year(i):  # when it charted
    w = node.get(i, {})
    for k in ("notoriety_date", "release_date", "written_date"):
        v = w.get(k)
        if v and str(v).strip().isdigit():
            return int(v)
    return None

creators_of = defaultdict(set)
works_of = defaultdict(set)
members_of = defaultdict(set)
for e in g["links"]:
    et, s, d = e["Edge Type"], e["source"], e["target"]
    if et in CREATOR and ntype(s) == "Person" and ntype(d) in WORK:
        creators_of[d].add(s); works_of[s].add(d)
    elif et == "MemberOf" and ntype(s) == "Person" and ntype(d) == "MusicalGroup":
        members_of[d].add(s)

def people_behind(i):
    tp = ntype(i)
    if tp == "Person": return {i}
    if tp in WORK: return set(creators_of.get(i, ()))
    if tp == "MusicalGroup": return set(members_of.get(i, ()))
    return set()

# influence reach: artist -> set of distinct downstream artists they influenced
reach = defaultdict(set)
for e in g["links"]:
    if e["Edge Type"] not in INFLUENCE:
        continue
    influencers = people_behind(e["target"])   # the earlier / inspiring side
    influenced = people_behind(e["source"])    # the later / drawing-from side
    for a in influencers:
        for b in influenced:
            if a != b:
                reach[a].add(b)

ref_year = max((release_year(i) for i in node if ntype(i) in WORK and release_year(i)), default=0)

def artist_record(a):
    ws = works_of.get(a, set())
    ry = [release_year(w) for w in ws if release_year(w) is not None]
    debut = min(ry) if ry else None
    oceanus = sum(1 for w in ws if genre_of(w) == GENRE)
    notable_years = sorted(notable_year(w) for w in ws if node[w].get("notable") and notable_year(w) is not None)
    rn = sum(1 for y in notable_years if y > ref_year - RECENT)
    pn = sum(1 for y in notable_years if ref_year - 2 * RECENT < y <= ref_year - RECENT)
    return {
        "id": a,
        "name": node[a].get("stage_name") or node[a].get("name"),
        "debut": debut,
        "total_works": len(ws),
        "oceanus_works": oceanus,
        "total_notable": len(notable_years),
        "recent_notable": rn,
        "prior_notable": pn,
        "influence_reach": len(reach.get(a, ())),
        "_notableyears": notable_years,
        "_workyears": sorted(ry),
    }

candidates = [artist_record(a) for a in works_of
              if any(genre_of(w) == GENRE for w in works_of[a])]
candidates = [c for c in candidates if c["debut"] is not None
              and c["total_works"] >= 3
              and (c["total_notable"] >= 1 or c["influence_reach"] >= 2)]

max_rn = max((c["recent_notable"] for c in candidates), default=1) or 1
max_growth = max((c["recent_notable"] - c["prior_notable"] for c in candidates), default=1) or 1
max_reach = max((c["influence_reach"] for c in candidates), default=1) or 1
max_career = max((ref_year - c["debut"] for c in candidates), default=1) or 1

def score(c):
    career = max(1, ref_year - c["debut"])
    parts = {
        "recentNotable": c["recent_notable"] / max_rn,
        "notableGrowth": max(0, c["recent_notable"] - c["prior_notable"]) / max_growth,
        # log-dampened: one outlier (a producer credited on hundreds of works) shouldn't flatten the rest
        "influenceReach": math.log1p(c["influence_reach"]) / math.log1p(max_reach),
        "oceanusAffinity": c["oceanus_works"] / max(1, c["total_works"]),
        "youth": 1 - (career / max_career),
    }
    return sum(WEIGHTS[k] * v for k, v in parts.items()), {k: round(v, 3) for k, v in parts.items()}

for c in candidates:
    c["score"], c["parts"] = score(c)
candidates.sort(key=lambda c: -c["score"])

def trajectory(c):
    """[year, cumulative notable, cumulative works] from debut..refYear."""
    notab, works = Counter(c["_notableyears"]), Counter(c["_workyears"])
    cn = cw = 0
    out = []
    for y in range(c["debut"], ref_year + 1):
        cn += notab.get(y, 0); cw += works.get(y, 0)
        out.append([y, cn, cw])
    while len(out) > 2 and out[-1][1] == out[-2][1] and out[-1][2] == out[-2][2]:
        out.pop()
    return out

sailor = artist_record(SAILOR_ID)
sailor["score"], sailor["parts"] = score(sailor)

predicted = [c for c in candidates if c["id"] != SAILOR_ID][:15]
traj_ids = {c["id"] for c in predicted[:8]} | {SAILOR_ID}
rec_by_id = {c["id"]: c for c in candidates}
rec_by_id[SAILOR_ID] = sailor
traj = {str(i): trajectory(rec_by_id[i]) for i in traj_ids}

def slim(c):
    return {k: c[k] for k in ("id", "name", "debut", "total_works", "oceanus_works",
            "total_notable", "recent_notable", "influence_reach", "score", "parts")}

out = {
    "refYear": ref_year, "recentWindow": RECENT, "weights": WEIGHTS,
    "predicted": [slim(c) for c in predicted],
    "benchmarks": [slim(sailor)],
    "traj": traj,
}
for d in (OUT_DIR, SERVED):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "rising_stars.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

# ---- summary ----
print(f"refYear={ref_year}  gated OF candidates={len(candidates)}  recent=last {RECENT}y")
print(f"\nSAILOR (benchmark): debut {sailor['debut']}, {sailor['total_notable']} notable "
      f"({sailor['recent_notable']} recent), reach {sailor['influence_reach']}, score {sailor['score']:.3f}")
print("\nPREDICTED NEXT OCEANUS FOLK STARS (top 12, Sailor excluded as benchmark):")
print(f"  {'name':22}{'score':>6}{'debut':>6}{'notbl':>6}{'recent':>7}{'reach':>6}{'OF':>4}")
for c in predicted[:12]:
    print(f"  {c['name'][:22]:22}{c['score']:6.3f}{c['debut']:>6}{c['total_notable']:>6}"
          f"{c['recent_notable']:>7}{c['influence_reach']:>6}{c['oceanus_works']:>4}")
