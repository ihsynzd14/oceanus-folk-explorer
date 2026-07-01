<script setup>
/* DetailPanel - selected artist's profile + who influenced them / whom they influenced (clickable). */
import { computed } from 'vue'
import { genreColor, displayName, dominantType } from '../lib/colors.js'

const props = defineProps({
  node: { type: [Object, null], default: null },
  influencers: { type: Array, default: () => [] },
  influenced: { type: Array, default: () => [] },
})
const emit = defineEmits(['select'])

const title = computed(() => (props.node ? displayName(props.node) : ''))
const subtitle = computed(() => {
  if (!props.node) return ''
  return props.node.stage_name && props.node.name && props.node.stage_name !== props.node.name
    ? props.node.name
    : ''
})
function typesLabel(types) {
  return Object.entries(types || {}).map(([t, c]) => (c > 1 ? `${t}×${c}` : t)).join(', ')
}
</script>

<template>
  <div v-if="!node" class="flex h-full items-center justify-center text-center text-sm text-slate-500">
    Click an artist to see their profile and influence.
  </div>
  <div v-else class="flex flex-col gap-4 text-sm">
    <div>
      <div class="flex items-center gap-2">
        <span class="inline-block h-3 w-3 rounded-full" :style="{ background: genreColor(node.top_genre) }"></span>
        <h2 class="text-base font-semibold text-white">{{ title }}</h2>
      </div>
      <p v-if="subtitle" class="text-xs text-slate-400">a.k.a. {{ subtitle }}</p>
    </div>

    <div class="grid grid-cols-2 gap-2 text-xs">
      <div class="rounded bg-slate-800 p-2"><div class="text-slate-400">Main genre</div><div class="text-slate-100">{{ node.top_genre || '-' }}</div></div>
      <div class="rounded bg-slate-800 p-2"><div class="text-slate-400">Active</div><div class="text-slate-100">{{ node.year || '-' }}<span v-if="node.active_to && node.active_to !== node.year">–{{ node.active_to }}</span></div></div>
      <div class="rounded bg-slate-800 p-2"><div class="text-slate-400">Works</div><div class="text-slate-100">{{ node.n_works }}<span v-if="node.n_notable" class="text-slate-400"> · {{ node.n_notable }} notable</span></div></div>
      <div class="rounded bg-slate-800 p-2"><div class="text-slate-400">Oceanus Folk works</div><div class="text-slate-100">{{ node.oceanus_works }}</div></div>
    </div>

    <div>
      <h3 class="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">Influenced by ({{ influencers.length }})</h3>
      <ul class="flex flex-col gap-0.5">
        <li v-for="d in influencers.slice(0, 12)" :key="'in-' + d.node.id"
            class="cursor-pointer rounded px-1.5 py-1 text-xs hover:bg-slate-800" @click="emit('select', d.node.id)">
          <span class="text-slate-200">← {{ displayName(d.node) }}</span>
          <span class="ml-1 text-slate-500">{{ typesLabel(d.types) }}</span>
        </li>
        <li v-if="!influencers.length" class="px-1.5 text-xs text-slate-500">No recorded influences.</li>
      </ul>
    </div>

    <div>
      <h3 class="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">Influenced ({{ influenced.length }})</h3>
      <ul class="flex flex-col gap-0.5">
        <li v-for="d in influenced.slice(0, 12)" :key="'out-' + d.node.id"
            class="cursor-pointer rounded px-1.5 py-1 text-xs hover:bg-slate-800" @click="emit('select', d.node.id)">
          <span class="text-slate-200">→ {{ displayName(d.node) }}</span>
          <span class="ml-1 text-slate-500">{{ typesLabel(d.types) }}</span>
        </li>
        <li v-if="!influenced.length" class="px-1.5 text-xs text-slate-500">No one recorded yet.</li>
      </ul>
    </div>
  </div>
</template>
