<script setup>
/*
 * InfluenceNetwork — the original D3 centerpiece (CLAUDE.md §7.1).
 * "Influence over time": the X axis is the year an artist became active, so
 * influence edges flow left (older / influencer) → right (newer / influenced).
 * A force layout spreads nodes vertically while a strong forceX pins them to
 * their year — this keeps the temporal reading and avoids the force "hairball".
 */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as d3 from 'd3'
import { genreColor, edgeColor, dominantType, displayName } from '../lib/colors.js'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  links: { type: Array, default: () => [] },
  selectedId: { type: [Number, null], default: null },
  center: { type: [Number, null], default: null },
})
const emit = defineEmits(['select'])

const svgRef = ref(null)
let tip = null

const W = 960
const H = 540
const M = { top: 18, right: 26, bottom: 30, left: 28 }

// persistent layout state so re-styling on selection doesn't recompute positions
let pos = new Map()      // id -> node copy with x,y
let drawnLinks = []      // link copies with resolved endpoints
let xScale = null

function radius(d) {
  const base = 3 + Math.sqrt(d.influencedCount || 0) * 2.2
  return d.id === props.center ? Math.max(base, 9) : base
}

function computeLayout() {
  const nodesCopy = props.nodes.map((d) => ({ ...d }))
  const byId = new Map(nodesCopy.map((d) => [d.id, d]))
  const linksCopy = props.links
    .filter((e) => byId.has(e.source) && byId.has(e.target))
    .map((e) => ({ ...e }))

  const years = nodesCopy.map((d) => d.year).filter((y) => y != null)
  const minYear = d3.min(years) ?? 2000
  const maxYear = d3.max(years) ?? 2030
  xScale = d3.scaleLinear().domain([minYear, maxYear]).range([M.left + 24, W - M.right]).nice()

  // seed positions: x by year, y fanned out so the sim starts untangled
  nodesCopy.forEach((d, i) => {
    d.x = xScale(d.year ?? minYear)
    d.y = H / 2 + (i % 2 ? 1 : -1) * (12 + (i % 40))
  })

  const sim = d3.forceSimulation(nodesCopy)
    .force('x', d3.forceX((d) => xScale(d.year ?? minYear)).strength((d) => (d.year != null ? 0.92 : 0.97)))
    .force('y', d3.forceY(H / 2).strength(0.045))
    .force('charge', d3.forceManyBody().strength(-16))
    .force('collide', d3.forceCollide((d) => radius(d) + 2))
    .force('link', d3.forceLink(linksCopy).id((d) => d.id).distance(26).strength(0.04))
    .stop()
  for (let i = 0; i < 320; i++) sim.tick()

  // keep inside the plot vertically
  for (const d of nodesCopy) {
    d.y = Math.max(M.top + radius(d), Math.min(H - M.bottom - radius(d), d.y))
  }

  pos = byId
  drawnLinks = linksCopy
}

function draw() {
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()
  if (!props.nodes.length) return

  const sel = props.selectedId
  const neighborIds = new Set()
  if (sel != null) {
    for (const e of drawnLinks) {
      const s = e.source.id ?? e.source
      const t = e.target.id ?? e.target
      if (s === sel) neighborIds.add(t)
      if (t === sel) neighborIds.add(s)
    }
    neighborIds.add(sel)
  }
  const dim = (id) => sel != null && !neighborIds.has(id)

  // X axis (years)
  const axis = svg.append('g')
    .attr('transform', `translate(0,${H - M.bottom + 2})`)
    .call(d3.axisBottom(xScale).ticks(8).tickFormat(d3.format('d')))
  axis.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10)
  axis.selectAll('line').attr('stroke', '#334155')
  axis.select('.domain').attr('stroke', '#334155')

  // directional hints in the top corners (kept clear of the year axis)
  svg.append('text')
    .attr('x', M.left).attr('y', M.top + 2)
    .attr('fill', '#64748b').attr('font-size', 10)
    .text('← earlier · influencers')
  svg.append('text')
    .attr('x', W - M.right).attr('y', M.top + 2)
    .attr('text-anchor', 'end')
    .attr('fill', '#64748b').attr('font-size', 10)
    .text('later · influenced →')

  // links (curved, influencer → influenced)
  svg.append('g').attr('class', 'links')
    .selectAll('path')
    .data(drawnLinks)
    .join('path')
    .attr('class', 'link')
    .attr('d', (e) => {
      const a = e.target, b = e.source // target = influencer (older), source = influenced (newer)
      const mx = (a.x + b.x) / 2
      return `M${a.x},${a.y} Q${mx},${(a.y + b.y) / 2 - 18} ${b.x},${b.y}`
    })
    .attr('stroke', (e) => edgeColor(dominantType(e.types)))
    .attr('stroke-width', (e) => Math.min(1 + (e.weight || 1) * 0.5, 3))
    .attr('opacity', (e) => {
      const s = e.source.id ?? e.source, t = e.target.id ?? e.target
      if (sel == null) return 0.22
      return s === sel || t === sel ? 0.85 : 0.04
    })

  // nodes
  svg.append('g')
    .selectAll('circle')
    .data([...pos.values()])
    .join('circle')
    .attr('class', 'node')
    .attr('cx', (d) => d.x)
    .attr('cy', (d) => d.y)
    .attr('r', (d) => radius(d))
    .attr('fill', (d) => genreColor(d.top_genre))
    .attr('stroke', (d) => (d.id === sel ? '#fde047' : d.id === props.center ? '#fff' : '#0b1020'))
    .attr('stroke-width', (d) => (d.id === sel ? 3 : d.id === props.center ? 2 : 1))
    .attr('opacity', (d) => (dim(d.id) ? 0.15 : 1))
    .on('click', (_, d) => emit('select', d.id))
    .on('mousemove', (event, d) => showTip(event, d))
    .on('mouseout', hideTip)

  // center label
  const c = pos.get(props.center)
  if (c) {
    svg.append('text')
      .attr('x', c.x).attr('y', c.y - radius(c) - 5)
      .attr('text-anchor', 'middle').attr('fill', '#fff')
      .attr('font-size', 11).attr('font-weight', 600)
      .text('Sailor Shift')
  }
}

function showTip(event, d) {
  if (!tip) return
  tip.style.display = 'block'
  tip.style.left = event.clientX + 12 + 'px'
  tip.style.top = event.clientY + 12 + 'px'
  tip.innerHTML =
    `<b>${displayName(d)}</b><br>` +
    `${d.top_genre || 'unknown genre'}${d.year ? ' · ' + d.year : ''}<br>` +
    `influenced ${d.influencedCount} · influenced-by ${d.influencedByCount}<br>` +
    `${d.n_works} works${d.oceanus_works ? ` · ${d.oceanus_works} Oceanus Folk` : ''}`
}
function hideTip() { if (tip) tip.style.display = 'none' }

function render() { computeLayout(); draw() }

onMounted(() => {
  tip = document.createElement('div')
  tip.className = 'tip'
  tip.style.display = 'none'
  document.body.appendChild(tip)
  render()
})
onBeforeUnmount(() => { if (tip) tip.remove() })

watch(() => [props.nodes, props.links], render)
watch(() => props.selectedId, draw)
</script>

<template>
  <svg
    ref="svgRef"
    :viewBox="`0 0 ${W} ${H}`"
    preserveAspectRatio="xMidYMid meet"
    class="h-full w-full"
  ></svg>
</template>
