<script setup>
/*
 * StarLeaderboard - ranked rising-star candidates with a transparent score breakdown.
 * Each row's bar is the weighted Rising Star Score, segmented by its five components,
 * so the analyst sees WHY an artist ranks. Click a row to add/remove it from the chart.
 * The ↗ button (shown when the artist exists in Sailor's influence network) jumps to
 * the Artist view focused on them - linking the prediction back to the relationships.
 */
import { computed } from 'vue'
import { SCORE_PARTS, SCORE_LABELS, scoreColor } from '../lib/colors.js'

const props = defineProps({
  predicted: { type: Array, default: () => [] },
  benchmark: { type: [Object, null], default: null },
  weights: { type: Object, default: () => ({}) },
  selectedIds: { type: Array, default: () => [] },
  egoIds: { type: Object, default: () => new Set() },
  selectedId: { type: [Number, null], default: null },
})
const emit = defineEmits(['toggle', 'open'])

const maxScore = computed(() =>
  Math.max(0.001, ...[props.benchmark, ...props.predicted].filter(Boolean).map((d) => d.score))
)
function segments(row) {
  return SCORE_PARTS.map((p) => ({
    key: p,
    w: (row.parts?.[p] || 0) * (props.weights[p] || 0),
    color: scoreColor(p),
  }))
}
const inChart = (id) => props.selectedIds.includes(id)
const inNetwork = (id) => props.egoIds.has(id)
</script>

<template>
  <div class="flex flex-col gap-2 text-xs">
    <!-- benchmark -->
    <div
      v-if="benchmark"
      class="cursor-pointer rounded-lg border border-slate-600 bg-slate-800/70 p-2"
      :class="[inChart(benchmark.id) ? 'ring-1 ring-white/60' : '', benchmark.id === selectedId ? 'border-l-4 border-l-cyan-400' : '']"
      @click="emit('toggle', benchmark.id)"
    >
      <div class="flex items-center justify-between gap-1">
        <span class="truncate font-medium text-white">★ {{ benchmark.name }} <span class="text-slate-400">(benchmark)</span></span>
        <span class="flex shrink-0 items-center gap-1">
          <button v-if="inNetwork(benchmark.id)" class="rounded px-1 text-slate-400 hover:bg-slate-700 hover:text-cyan-300"
                  title="Show in influence network" @click.stop="emit('open', benchmark.id)">↗</button>
          <span class="tabular-nums text-slate-300">{{ benchmark.score.toFixed(2) }}</span>
        </span>
      </div>
      <div class="mt-1 flex h-2 w-full overflow-hidden rounded bg-slate-700/50">
        <div v-for="s in segments(benchmark)" :key="s.key"
             :style="{ width: (s.w / maxScore * 100) + '%', background: s.color }"></div>
      </div>
    </div>

    <!-- candidates -->
    <ol class="flex flex-col gap-1">
      <li
        v-for="(row, i) in predicted"
        :key="row.id"
        class="cursor-pointer rounded-lg p-2 hover:bg-slate-800"
        :class="[inChart(row.id) ? 'bg-slate-800 ring-1 ring-cyan-400/50' : '', row.id === selectedId ? 'border-l-4 border-l-cyan-400' : '']"
        @click="emit('toggle', row.id)"
      >
        <div class="flex items-center justify-between gap-1">
          <span class="truncate text-slate-200">
            <span class="text-slate-500">{{ i + 1 }}.</span> {{ row.name }}
            <span class="text-slate-500">· debut {{ row.debut }}</span>
          </span>
          <span class="flex shrink-0 items-center gap-1">
            <button v-if="inNetwork(row.id)" class="rounded px-1 text-slate-400 hover:bg-slate-700 hover:text-cyan-300"
                    title="Show in influence network" @click.stop="emit('open', row.id)">↗</button>
            <span class="tabular-nums text-slate-300">{{ row.score.toFixed(2) }}</span>
          </span>
        </div>
        <div class="mt-1 flex h-2 w-full overflow-hidden rounded bg-slate-700/40" :style="{ maxWidth: (row.score / maxScore * 100) + '%' }">
          <div v-for="s in segments(row)" :key="s.key"
               :style="{ width: (s.w / row.score * 100) + '%', background: s.color }"></div>
        </div>
        <div class="mt-0.5 text-[10px] text-slate-500">
          {{ row.total_notable }} notable · reach {{ row.influence_reach }} · {{ row.oceanus_works }} Oceanus Folk works
        </div>
      </li>
    </ol>

    <!-- component legend -->
    <div class="mt-1 flex flex-wrap gap-x-3 gap-y-1 border-t border-slate-700 pt-2 text-[10px] text-slate-400">
      <span v-for="p in SCORE_PARTS" :key="p" class="flex items-center gap-1">
        <span class="inline-block h-2 w-2 rounded-sm" :style="{ background: scoreColor(p) }"></span>{{ SCORE_LABELS[p] }}
      </span>
    </div>
  </div>
</template>
