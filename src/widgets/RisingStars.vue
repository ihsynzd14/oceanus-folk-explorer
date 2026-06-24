<script setup>
/*
 * RisingStars — MC1 Task 3 trajectory comparison.
 * Multi-line chart of each selected artist's CUMULATIVE notable works (chart hits)
 * over time — the popularity curve. Steep recent slopes = rising; Sailor Shift is
 * drawn dashed as the established benchmark to compare careers against.
 */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as d3 from 'd3'
import { artistColor } from '../lib/colors.js'

const props = defineProps({
  traj: { type: Object, default: () => ({}) },     // id -> [[year, cumNotable, cumWorks]]
  selectedIds: { type: Array, default: () => [] },  // numeric ids to draw
  names: { type: Object, default: () => ({}) },     // id -> name
  benchmarkId: { type: [Number, null], default: null },
})

const svgRef = ref(null)
let tip = null
const W = 900, H = 380, M = { top: 16, right: 150, bottom: 28, left: 34 }

function render() {
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()
  const ids = props.selectedIds.filter((id) => props.traj[String(id)])
  if (!ids.length) return

  const series = ids.map((id) => ({
    id,
    name: props.names[id] || `#${id}`,
    values: props.traj[String(id)].map((d) => ({ year: d[0], cum: d[1] })),
  }))

  const allPts = series.flatMap((s) => s.values)
  const x = d3.scaleLinear().domain(d3.extent(allPts, (d) => d.year)).range([M.left, W - M.right])
  const y = d3.scaleLinear().domain([0, d3.max(allPts, (d) => d.cum) || 1]).nice().range([H - M.bottom, M.top])

  const ax = svg.append('g').attr('transform', `translate(0,${H - M.bottom})`)
    .call(d3.axisBottom(x).ticks(10).tickFormat(d3.format('d')))
  ax.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10)
  ax.selectAll('line').attr('stroke', '#334155'); ax.select('.domain').attr('stroke', '#334155')
  const ay = svg.append('g').attr('transform', `translate(${M.left},0)`).call(d3.axisLeft(y).ticks(5))
  ay.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 10)
  ay.selectAll('line').attr('stroke', '#334155'); ay.select('.domain').attr('stroke', '#334155')
  svg.append('text').attr('x', M.left).attr('y', M.top - 4)
    .attr('fill', '#64748b').attr('font-size', 10).text('cumulative chart hits (notable works)')

  const line = d3.line().x((d) => x(d.year)).y((d) => y(d.cum)).curve(d3.curveMonotoneX)

  for (const s of series) {
    const isBench = s.id === props.benchmarkId
    const c = isBench ? '#f8fafc' : artistColor(String(s.id))
    svg.append('path').datum(s.values).attr('fill', 'none')
      .attr('stroke', c).attr('stroke-width', isBench ? 2 : 2.2)
      .attr('stroke-dasharray', isBench ? '5 4' : null)
      .attr('opacity', 0.95).attr('d', line)
      .on('mousemove', (event) => {
        const last = s.values[s.values.length - 1]
        tip.style.display = 'block'
        tip.style.left = event.clientX + 12 + 'px'
        tip.style.top = event.clientY + 12 + 'px'
        tip.innerHTML = `<b>${s.name}</b>${isBench ? ' (benchmark)' : ''}<br>${last.cum} notable works by ${last.year}`
      })
      .on('mouseout', () => { tip.style.display = 'none' })
  }

  // legend
  const lg = svg.append('g').attr('transform', `translate(${W - M.right + 12},${M.top})`)
  series.forEach((s, i) => {
    const isBench = s.id === props.benchmarkId
    const c = isBench ? '#f8fafc' : artistColor(String(s.id))
    const row = lg.append('g').attr('transform', `translate(0,${i * 16})`)
    row.append('line').attr('x1', 0).attr('x2', 12).attr('y1', 5).attr('y2', 5)
      .attr('stroke', c).attr('stroke-width', 2).attr('stroke-dasharray', isBench ? '5 4' : null)
    row.append('text').attr('x', 17).attr('y', 9).attr('fill', '#cbd5e1').attr('font-size', 10)
      .text(s.name + (isBench ? ' ★' : ''))
  })
}

onMounted(() => {
  tip = document.createElement('div'); tip.className = 'tip'; tip.style.display = 'none'
  document.body.appendChild(tip); render()
})
onBeforeUnmount(() => { if (tip) tip.remove() })
watch(() => [props.traj, props.selectedIds], render, { deep: true })
</script>

<template>
  <svg ref="svgRef" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="xMidYMid meet" class="h-full w-full"></svg>
</template>
