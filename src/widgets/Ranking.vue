<script setup>
/* Ranking - top artists by out-influence (how many others they influenced). Linked: click selects. */
import { computed } from 'vue'
import { genreColor, displayName } from '../lib/colors.js'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  selectedId: { type: [Number, null], default: null },
})
const emit = defineEmits(['select'])

const top = computed(() => {
  const max = Math.max(1, ...props.nodes.map((n) => n.influencedCount || 0))
  return [...props.nodes]
    .sort((a, b) => (b.influencedCount || 0) - (a.influencedCount || 0))
    .slice(0, 12)
    .map((n) => ({ ...n, pct: ((n.influencedCount || 0) / max) * 100 }))
})
</script>

<template>
  <ul class="flex flex-col gap-1">
    <li
      v-for="n in top"
      :key="n.id"
      class="cursor-pointer rounded px-1.5 py-1 text-xs hover:bg-slate-800"
      :class="n.id === selectedId ? 'bg-slate-800 ring-1 ring-yellow-400/60' : ''"
      @click="emit('select', n.id)"
    >
      <div class="flex items-center justify-between gap-2">
        <span class="truncate text-slate-200">{{ displayName(n) }}</span>
        <span class="shrink-0 tabular-nums text-slate-400">{{ n.influencedCount }}</span>
      </div>
      <div class="mt-0.5 h-1.5 w-full overflow-hidden rounded bg-slate-700/60">
        <div class="h-full rounded" :style="{ width: n.pct + '%', background: genreColor(n.top_genre) }"></div>
      </div>
    </li>
    <li v-if="!top.length" class="px-1 py-2 text-xs text-slate-500">No artists in the current filter.</li>
  </ul>
</template>
