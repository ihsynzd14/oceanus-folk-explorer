# Oceanus Folk Explorer — VAST 2025 MC1

Interactive tool to explore **the rise of Sailor Shift and the spread of Oceanus Folk**, built for the
Visual Analytics (602AA) final project. It lets an analyst answer the MC1 challenge questions through
linked, interactive widgets centered on an original D3 "influence-over-time" network.

## What it shows

Three views, switched by tabs in the header, one per MC1 task.

**Artist · Sailor Shift** (Task 1) — who shaped Sailor Shift and whom she shaped:
- **Influence-over-time network** (the original D3 centerpiece): artists placed on a time axis
  (X = year they became active); influence edges flow left (influencers) → right (influenced),
  anchored on Sailor Shift's ego-network. Avoids the force-directed "hairball".
- **Timeline**: artists active per year, with a **brush that filters the network + ranking**.
- **Top influencers** ranking and a **detail panel** (profile, who influenced them, whom they influenced).
- Linked: selecting in any of these widgets updates the others (crossfilter on the year dimension).

**Genre spread** (Task 2) — how Oceanus Folk spread through the music world:
- **Stacked area** of works influenced by Oceanus Folk each year, banded by genre, with a dashed
  line of Oceanus Folk's own releases. The bursts show an intermittent (not gradual) rise.
- Rankings of the genres it drew from, the genres it influenced, and the most affected artists.

**Rising stars** (Task 3) — who is likely to break out next:
- **Trajectory comparison** of cumulative chart hits over time, with Sailor Shift as a benchmark.
- **Leaderboard** ranked by a transparent Rising Star Score; each bar is split into the score's
  five components. Click a candidate to add it to the comparison.

## Prerequisites

- Node.js 18+ and npm
- Python 3 (only for regenerating the data; `pypdf`/`fitz` not required for the app)

## Setup

```bash
npm install
npm run data        # downloads MC1_release.zip + builds all three datasets into public/data/
npm run dev         # http://localhost:5173
```

`npm run data` runs all three builders (`build_subgraph.py`, `build_genre_spread.py`,
`build_rising_stars.py`). The generated JSON is committed, so the app also runs straight after
`npm install` without this step. Individual builders: `npm run data:ego | data:genre | data:stars`.
For a wider artist neighborhood: `python scripts/build_subgraph.py 2` (≈1,200 artists).

## Project layout

```
index.html            app entry
vite.config.js        Vite + Vue + Tailwind v4
src/
  main.js
  App.vue             coordinator: loads data, crossfilter, shared selection/year state
  widgets/
    InfluenceNetwork.vue   ← the original D3 centerpiece (Task 1)
    Timeline.vue           brushable year histogram
    Ranking.vue            top influencers
    DetailPanel.vue        selected-artist profile
    GenreSpread.vue        stacked-area genre spread (Task 2)
    BarList.vue            reusable ranked bars
    RisingStars.vue        career-trajectory comparison (Task 3)
    StarLeaderboard.vue    scored rising-star leaderboard
  lib/colors.js       genre / edge-type / score color scales
scripts/
  inspect_mc1.py        downloads + prints the raw graph schema
  build_subgraph.py     work-level influence → people; Sailor's ego-network → sailor_ego.json
  build_genre_spread.py global Oceanus Folk spread by year/genre → genre_spread.json
  build_rising_stars.py Rising Star Score + trajectories → rising_stars.json
data/
  raw/                original VAST MC1 files (git-ignored; redistributable)
  processed/          slim derived JSON (canonical)
  README.md           full schema + edge-direction semantics
public/data/          served copies the app fetches (sailor_ego, genre_spread, rising_stars)
report/               LaTeX report + figures
```

## Data

VAST 2025 Mini-Challenge 1 knowledge graph (`vast-challenge/2025-data` → `MC1_release.zip`):
17,412 nodes / 37,857 edges. Schema and edge semantics are documented in [`data/README.md`](data/README.md).
All data is synthetic; only MC1 data is used.
