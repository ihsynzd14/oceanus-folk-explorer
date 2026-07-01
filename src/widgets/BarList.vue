<script setup>
/* BarList - simple horizontal ranked bars. Reused for genre / artist rankings. */
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }, // [{ label, count, color? }]
  unit: { type: String, default: '' },
  limit: { type: Number, default: 12 },
})
const rows = computed(() => {
  const max = Math.max(1, ...props.items.map((d) => d.count || 0))
  return props.items.slice(0, props.limit).map((d) => ({ ...d, pct: ((d.count || 0) / max) * 100 }))
})
</script>

<template>
  <ul class="flex flex-col gap-1">
    <li v-for="(d, i) in rows" :key="i" class="px-0.5 py-0.5 text-xs">
      <div class="flex items-center justify-between gap-2">
        <span class="truncate text-slate-200">{{ d.label }}</span>
        <span class="shrink-0 tabular-nums text-slate-400">{{ d.count }}{{ unit }}</span>
      </div>
      <div class="mt-0.5 h-1.5 w-full overflow-hidden rounded bg-slate-700/60">
        <div class="h-full rounded" :style="{ width: d.pct + '%', background: d.color || '#22d3ee' }"></div>
      </div>
    </li>
    <li v-if="!rows.length" class="px-1 py-2 text-xs text-slate-500">No data.</li>
  </ul>
</template>
