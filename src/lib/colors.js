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
