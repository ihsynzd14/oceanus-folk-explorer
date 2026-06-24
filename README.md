# Oceanus Folk Explorer — VAST 2025 MC1

Interactive tool to explore **the rise of Sailor Shift and the spread of Oceanus Folk**, built for the
Visual Analytics (602AA) final project. It lets an analyst answer the MC1 challenge questions through
linked, interactive widgets centered on an original D3 "influence-over-time" network.

## What it shows

- **Influence-over-time network** (the original D3 centerpiece): artists placed on a time axis
  (X = year they became active); influence edges flow left (influencers) → right (influenced),
  anchored on Sailor Shift's ego-network. Avoids the force-directed "hairball".
- **Timeline**: artists active per year, with a **brush that filters every other view**.
- **Top influencers**: ranking by how many other artists each one influenced.
- **Detail panel**: the selected artist's profile, who influenced them, and whom they influenced.
- **Linked views**: selecting in any widget updates the others (crossfilter on the year dimension).

## Prerequisites

- Node.js 18+ and npm
- Python 3 (only for regenerating the data; `pypdf`/`fitz` not required for the app)

## Setup

```bash
npm install
npm run data        # downloads MC1_release.zip + builds public/data/sailor_ego.json (1-hop ego-network)
npm run dev         # http://localhost:5173
```

`npm run data` runs `scripts/build_subgraph.py`. Pass a hop count for a wider neighborhood:
`python scripts/build_subgraph.py 2` (≈1,200 artists — needs filtering to stay readable).

## Project layout

```
index.html            app entry
vite.config.js        Vite + Vue + Tailwind v4
src/
  main.js
  App.vue             coordinator: loads data, crossfilter, shared selection/year state
  widgets/
    InfluenceNetwork.vue   ← the original D3 centerpiece
    Timeline.vue           brushable year histogram
    Ranking.vue            top influencers
    DetailPanel.vue        selected-artist profile
  lib/colors.js       genre / edge-type color scales
scripts/
  inspect_mc1.py      downloads + prints the raw graph schema
  build_subgraph.py   projects work-level influence → people, extracts Sailor's ego-network
data/
  raw/                original VAST MC1 files (git-ignored; redistributable)
  processed/          slim derived JSON (canonical)
  README.md           full schema + edge-direction semantics
public/data/          served copy of sailor_ego.json
```

## Data

VAST 2025 Mini-Challenge 1 knowledge graph (`vast-challenge/2025-data` → `MC1_release.zip`):
17,412 nodes / 37,857 edges. Schema and edge semantics are documented in [`data/README.md`](data/README.md).
All data is synthetic; only MC1 data is used.
