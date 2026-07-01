import * as d3 from 'd3'

// The five influence edge types (target = influencer, source = influenced).
export const INFLUENCE_TYPES = [
  'InStyleOf',
  'InterpolatesFrom',
  'CoverOf',
  'LyricalReferenceTo',
  'DirectlySamples',
]

// All palettes use the Okabe-Ito colorblind-safe scheme
// (orange #E69F00, sky #56B4E9, green #009E73, yellow #F0E442, blue #0072B2,
//  vermillion #D55E00, purple #CC79A7, gray #999999).
export const edgeColor = d3.scaleOrdinal()
  .domain(INFLUENCE_TYPES)
  .range(['#E69F00', '#009E73', '#CC79A7', '#D55E00', '#0072B2'])

// Oceanus Folk gets a signature color (reserved); everything else from a categorical scale.
const OCEANUS = '#56B4E9'
const otherGenre = d3.scaleOrdinal()
  .range(['#E69F00', '#009E73', '#D55E00', '#CC79A7', '#F0E442', '#0072B2', '#999999'])

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
  .range(['#0072B2', '#009E73', '#CC79A7', '#F0E442', '#D55E00'])

// Stable per-artist line color for the trajectory comparison (Okabe-Ito, CB-safe).
export const artistColor = d3.scaleOrdinal()
  .range(['#E69F00', '#009E73', '#D55E00', '#CC79A7', '#F0E442', '#0072B2', '#999999', '#56B4E9'])
