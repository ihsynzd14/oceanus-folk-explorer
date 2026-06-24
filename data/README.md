# MC1 Data — Schema & Findings

Source: `vast-challenge/2025-data` → `MC1_release.zip` (downloaded by `scripts/inspect_mc1.py`).
Raw files live in `data/raw/MC1_release/` (do **not** edit). Slim derived files for the browser go in `data/processed/`.

> All data is **synthetic**. Use **only** MC1 data to answer the questions (no external/other-year data).

## Graph at a glance

- File: `MC1_graph.json` — a `networkx` `node_link_data()` export.
- **Directed multigraph**, **17,412 nodes**, **37,857 edges**, **18 connected components**.
- Root keys: `directed` (true), `multigraph` (true), `graph`, `nodes` (list), `links` (list).
- Edges reference nodes by integer `id` via `source` / `target`.
- **Sailor Shift** = `Person`, `id = 17255`.

## Node types (5)

| Type | Count | Properties |
|------|-------|------------|
| `Person` | 11,361 | `id, name, stage_name?` |
| `Song` | 3,615 | `id, name, genre, single?, notable, release_date, notoriety_date?, written_date?` |
| `RecordLabel` | 1,217 | `id, name` |
| `Album` | 996 | `id, name, genre, notable, release_date, notoriety_date?, written_date?` |
| `MusicalGroup` | 223 | `id, name` |

Notes:
- Dates are **year strings** (e.g. `"2017"`). `release_date` = released; `notoriety_date` = first hit a top chart (popularity signal); `written_date` = written. `?` = optional/sometimes missing.
- `notable` (bool) = appeared on a top record chart. `single` (Song only) = standalone vs. part of an album.
- `genre` lives on **works** (Song/Album), not on people — a person's genre(s) are inferred from their works.

## Edge types (12) — direction matters

For every edge the only property is `Edge Type`. Direction is `source → target`.

**Role / creation edges** (Person/Group/Label ↔ Work):
| Edge | source → target | Meaning |
|------|-----------------|---------|
| `PerformerOf` (13,587) | Person/MusicalGroup → Song/Album | performed the work |
| `ComposerOf` (3,290) | Person → Song/Album | composed it |
| `ProducerOf` (3,209) | Person/RecordLabel → Song/Album/**Person/MusicalGroup** | produced the work/act |
| `LyricistOf` (2,985) | Person → Song/Album | wrote lyrics |
| `RecordedBy` (3,798) | Song/Album → RecordLabel | label aided recording |
| `DistributedBy` (3,013) | Song/Album → RecordLabel | label aided distribution |
| `MemberOf` (568) | Person → MusicalGroup | (was) a member |

**Influence edges** (Work → earlier Work/act it drew from). **The `target` is the influencer; the `source` is the influenced.**
| Edge | source → target | Meaning |
|------|-----------------|---------|
| `InStyleOf` (2,289) | Song/Album → Song/Album/**Person/MusicalGroup** | performed in the style of target |
| `InterpolatesFrom` (1,574) | Song/Album → Song/Album | reused a melody from target |
| `LyricalReferenceTo` (1,496) | Song/Album → Song/Album | lyrical reference to target |
| `CoverOf` (1,429) | Song/Album → Song/Album | is a cover of target |
| `DirectlySamples` (619) | Song/Album → Song/Album | samples target's audio |

## How this maps to the MC1 tasks

- **Influence is encoded at the work level.** Person→Person influence is *inferred*: `PersonA` made `WorkX`, `WorkX --influence--> WorkY`, `WorkY` was made by `PersonB` ⟹ `PersonB` influenced `PersonA`. (`InStyleOf`/`ProducerOf` can also point straight at a Person.)
- **Time axis** for the centerpiece: use `notoriety_date` when present (popularity moment), else `release_date`. Influence target (older) sits left of influence source (newer).
- **Oceanus Folk spread (task 2):** filter works where `genre == "Oceanus Folk"` and follow influence edges in/out across years.
- **Rising star / popularity (task 3):** `notable` + `notoriety_date` + influence out-degree over time.

## Two data sources behind the graph (per official description)

1. A crowdsourced repository of musical influence (who sampled/covered/drew inspiration from whom) — the influence edges.
2. Journalist Silas Reed's popularity labels (`notable`, `notoriety_date`) from sales/streams/chart appearances.
