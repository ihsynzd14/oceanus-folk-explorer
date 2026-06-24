<script setup>
/*
 * GenreSpread — MC1 Task 2. Stacked area of works *influenced by Oceanus Folk*
 * per year, banded by the genre of the influenced work: the silhouette shows
 * whether the spread was gradual or intermittent, the bands show which genres
 * it reached. A dashed line overlays Oceanus Folk's own releases for comparison.
 */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as d3 from 'd3'
import { genreColor } from '../lib/colors.js'

const props = defineProps({
  spread: { type: Array, default: () => [] },       // [{ year, genre, count }]
  ofReleases: { type: Object, default: () => ({}) },// { year: count }
  yearRange: { type: Array, default: () => null },
})

const svgRef = ref(null)
let tip = null
const W = 900, H = 360, M = { top: 16, right: 150, bottom: 28, left: 38 }
const TOP = 8

function render() {
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()
  if (!props.spread.length) return

  const totals = d3.rollup(props.spread, (v) => d3.sum(v, (d) => d.count), (d) => d.genre)
  const sorted = [...totals.entries()].sort((a, b) => b[1] - a[1])
  const topKeys = sorted.slice(0, TOP).map((d) => d[0])
  const hasOther = sorted.length > TOP
  const keys = hasOther ? [...topKeys, 'Other'] : topKeys

  const allYears = props.spread.map((d) => d.year)
  const minY = props.yearRange ? props.yearRange[0] : d3.min(allYears)
  const maxY = props.yearRange ? props.yearRange[1] : d3.max(allYears)

  const byYear = new Map()
  for (let y = minY; y <= maxY; y++) {
    byYear.set(y, { year: y, ...Object.fromEntries(keys.map((k) => [k, 0])) })
  }
  for (const d of props.spread) {
    const row = byYear.get(d.year)
    if (!row) continue
    const k = topKeys.includes(d.genre) ? d.genre : 'Other'
    row[k] += d.count
  }
  const rows = [...byYear.values()]
  const stacked = d3.stack().keys(keys)(rows)

  const maxStack = d3.max(rows, (r) => d3.sum(keys, (k) => r[k])) || 1
  const releases = []
  for (let y = minY; y <= maxY; y++) releases.push({ year: y, count: +props.ofReleases[y] || 0 })
  const maxRel = d3.max(releases, (d) => d.count) || 0
  const maxVal = Math.max(maxStack, maxRel)

  const x = d3.scaleLinear().domain([minY, maxY]).range([M.left, W - M.right])
  const y = d3.scaleLinear().domain([0, maxVal]).range([H - M.bottom, M.top]).nice()
  const color = (k) => (k === 'Other' ? '#475569' : genreColor(k))

  const area = d3.area().x((d) => x(d.data.year)).y0((d) => y(d[0])).y1((d) => y(d[1])).curve(d3.curveMonotoneX)

  // axes
  const ax = svg.append('g').attr('transform', `translate(0,${H - M.bottom})`)
    .call(d3.axisBottom(x).ticks(10).tickFormat(d3.format('d')))
  ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10)
  ax.selectAll('line').attr('stroke', '#334155'); ax.select('.domain').attr('stroke', '#334155')
  const ay = svg.append('g').attr('transform', `translate(${M.left},0)`)
    .call(d3.axisLeft(y).ticks(5))
  ay.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10)
  ay.selectAll('line').attr('stroke', '#334155'); ay.select('.domain').attr('stroke', '#334155')

  // bands
  svg.append('g').selectAll('path')
    .data(stacked)
    .join('path')
    .attr('d', area)
    .attr('fill', (s) => color(s.key))
    .attr('opacity', 0.85)
    .on('mousemove', (event, s) => {
      svg.selectAll('path').attr('opacity', (o) => (o === s ? 1 : 0.25))
      const total = d3.sum(rows, (r) => r[s.key])
      tip.style.display = 'block'
      tip.style.left = event.clientX + 12 + 'px'
      tip.style.top = event.clientY + 12 + 'px'
      tip.innerHTML = `<b>${s.key}</b><br>${total} works influenced by Oceanus Folk`
    })
    .on('mouseout', () => { svg.selectAll('path').attr('opacity', 0.85); tip.style.display = 'none' })

  // Oceanus Folk releases overlay
  const line = d3.line().x((d) => x(d.year)).y((d) => y(d.count)).curve(d3.curveMonotoneX)
  svg.append('path').datum(releases).attr('fill', 'none')
    .attr('stroke', '#f8fafc').attr('stroke-width', 1.6).attr('stroke-dasharray', '4 3')
    .attr('opacity', 0.9).attr('d', line)

  // legend
  const lg = svg.append('g').attr('transform', `translate(${W - M.right + 12},${M.top})`)
  keys.forEach((k, i) => {
    const g = lg.append('g').attr('transform', `translate(0,${i * 16})`)
    g.append('rect').attr('width', 10).attr('height', 10).attr('rx', 2).attr('fill', color(k))
    g.append('text').attr('x', 15).attr('y', 9).attr('fill', '#cbd5e1').attr('font-size', 10).text(k)
  })
  const gl = lg.append('g').attr('transform', `translate(0,${keys.length * 16 + 4})`)
  gl.append('line').attr('x1', 0).attr('x2', 10).attr('y1', 5).attr('y2', 5)
    .attr('stroke', '#f8fafc').attr('stroke-width', 1.6).attr('stroke-dasharray', '4 3')
  gl.append('text').attr('x', 15).attr('y', 9).attr('fill', '#cbd5e1').attr('font-size', 10).text('OF releases')
}

onMounted(() => {
  tip = document.createElement('div'); tip.className = 'tip'; tip.style.display = 'none'
  document.body.appendChild(tip); render()
})
onBeforeUnmount(() => { if (tip) tip.remove() })
watch(() => [props.spread, props.yearRange], render)
</script>

<template>
  <svg ref="svgRef" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="xMidYMid meet" class="h-full w-full"></svg>
</template>
