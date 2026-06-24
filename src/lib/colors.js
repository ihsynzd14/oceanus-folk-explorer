import * as d3 from 'd3'

// The five influence edge types (target = influencer, source = influenced).
export const INFLUENCE_TYPES = [
  'InStyleOf',
  'InterpolatesFrom',
  'CoverOf',
  'LyricalReferenceTo',
  'DirectlySamples',
]

export const edgeColor = d3.scaleOrdinal()
  .domain(INFLUENCE_TYPES)
  .range(['#5eead4', '#fbbf24', '#f472b6', '#a78bfa', '#fb7185'])

// Oceanus Folk gets a signature color; everything else from a categorical scale.
const OCEANUS = '#22d3ee'
const otherGenre = d3.scaleOrdinal(d3.schemeTableau10)

export function genreColor(genre) {
  if (!genre) return '#64748b'
  if (genre === 'Oceanus Folk') return OCEANUS
  return otherGenre(genre)
}

// Dominant influence type for an edge (the one with the highest count).
export function dominantType(types) {
  let best = null, max = -1
  for (const [t, c] of Object.entries(types || {})) {
    if (c > max) { max = c; best = t }
  }
  return best
}

export function displayName(n) {
  return n.stage_name || n.name || `#${n.id}`
}

// Rising Star Score components (Task 3) — order = stacking order in the breakdown bar.
export const SCORE_PARTS = ['recentNotable', 'notableGrowth', 'influenceReach', 'oceanusAffinity', 'youth']
export const SCORE_LABELS = {
  recentNotable: 'Recent chart hits',
  notableGrowth: 'Momentum (acceleration)',
  influenceReach: 'Influence reach',
  oceanusAffinity: 'Oceanus Folk affinity',
  youth: 'Career youth',
}
export const scoreColor = d3.scaleOrdinal()
  .domain(SCORE_PARTS)
  .range(['#22d3ee', '#34d399', '#a78bfa', '#fbbf24', '#fb7185'])

// Stable per-artist line color for the trajectory comparison.
export const artistColor = d3.scaleOrdinal(d3.schemeTableau10)
