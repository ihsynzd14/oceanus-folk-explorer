<script setup>
/* Timeline - artists active per year, with a brush that filters every linked view. */
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  yearRange: { type: [Array, null], default: null },
})
const emit = defineEmits(['update:year-range'])

const svgRef = ref(null)
const W = 460, H = 130, M = { top: 8, right: 10, bottom: 22, left: 28 }
let xScale = null, brush = null, gBrush = null

function render() {
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()
  const years = props.nodes.map((n) => n.year).filter((y) => y != null)
  if (!years.length) return

  const counts = d3.rollup(years, (v) => v.length, (y) => y)
  const minYear = d3.min(years), maxYear = d3.max(years)
  xScale = d3.scaleLinear().domain([minYear, maxYear + 1]).range([M.left, W - M.right])
  const yMax = d3.max(counts.values())
  const y = d3.scaleLinear().domain([0, yMax]).range([H - M.bottom, M.top])

  // bars
  svg.append('g').selectAll('rect')
    .data([...counts.entries()].sort((a, b) => a[0] - b[0]))
    .join('rect')
    .attr('x', (d) => xScale(d[0]) + 0.5)
    .attr('y', (d) => y(d[1]))
    .attr('width', (d) => Math.max(1, xScale(d[0] + 1) - xScale(d[0]) - 1))
    .attr('height', (d) => H - M.bottom - y(d[1]))
    .attr('fill', '#56B4E9')
    .attr('opacity', 0.7)

  // axis
  const axis = svg.append('g')
    .attr('transform', `translate(0,${H - M.bottom})`)
    .call(d3.axisBottom(xScale).ticks(6).tickFormat(d3.format('d')))
  axis.selectAll('text').attr('fill', '#94a3b8').attr('font-size', 9)
  axis.selectAll('line').attr('stroke', '#334155')
  axis.select('.domain').attr('stroke', '#334155')

  // brush
  brush = d3.brushX()
    .extent([[M.left, M.top], [W - M.right, H - M.bottom]])
    .on('end', (event) => {
      if (!event.sourceEvent) return
      if (!event.selection) { emit('update:year-range', null); return }
      const [x0, x1] = event.selection
      const y0 = Math.floor(xScale.invert(x0))
      const y1 = Math.max(y0, Math.ceil(xScale.invert(x1)) - 1)
      emit('update:year-range', [y0, y1])
    })
  gBrush = svg.append('g').attr('class', 'brush').call(brush)
  gBrush.selectAll('.selection').attr('fill', '#fde047').attr('fill-opacity', 0.18).attr('stroke', '#fde047')
}

onMounted(render)
watch(() => props.nodes, render)
</script>

<template>
  <svg ref="svgRef" :viewBox="`0 0 ${W} ${H}`" class="w-full"></svg>
</template>
