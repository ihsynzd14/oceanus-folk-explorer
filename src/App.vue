<script setup>
import { ref, shallowRef, computed, onMounted } from 'vue'
import crossfilter from 'crossfilter2'
import InfluenceNetwork from './widgets/InfluenceNetwork.vue'
import Timeline from './widgets/Timeline.vue'
import Ranking from './widgets/Ranking.vue'
import DetailPanel from './widgets/DetailPanel.vue'
import GenreSpread from './widgets/GenreSpread.vue'
import BarList from './widgets/BarList.vue'
import RisingStars from './widgets/RisingStars.vue'
import StarLeaderboard from './widgets/StarLeaderboard.vue'
import { genreColor } from './lib/colors.js'

const loading = ref(true)
const error = ref(null)
const view = ref('artist') // 'artist' | 'genre' | 'stars'
const genre = shallowRef(null)
const stars = shallowRef(null)
const starSelection = ref([])

const allNodes = shallowRef([])
const allLinks = shallowRef([])
const idx = shallowRef(new Map())
const center = ref(null)
const hops = ref(null)

const selectedId = ref(null)
const yearRange = ref(null)          // [y0, y1] or null (= all years)
const filteredIds = shallowRef(null) // Set<id> or null (= all)

let cf, dYear

onMounted(async () => {
  try {
    const res = await fetch('/data/sailor_ego.json')
    if (!res.ok) throw new Error(`HTTP ${res.status} loading /data/sailor_ego.json`)
    const g = await res.json()

    const map = new Map(g.nodes.map((n) => [n.id, n]))
    // influence edge: { source = influenced, target = influencer }
    for (const n of g.nodes) { n.influencedCount = 0; n.influencedByCount = 0 }
    for (const e of g.influence) {
      const influencer = map.get(e.target)
      const influenced = map.get(e.source)
      if (influencer) influencer.influencedCount += 1
      if (influenced) influenced.influencedByCount += 1
    }

    allNodes.value = g.nodes
    allLinks.value = g.influence
    idx.value = map
    center.value = g.center
    hops.value = g.hops
    selectedId.value = g.center

    cf = crossfilter(g.nodes)
    dYear = cf.dimension((d) => (d.year == null ? -9999 : d.year))

    const gr = await fetch('/data/genre_spread.json') // Task 2 (non-fatal if absent)
    if (gr.ok) genre.value = await gr.json()

    const rs = await fetch('/data/rising_stars.json') // Task 3 (non-fatal if absent)
    if (rs.ok) {
      const data = await rs.json()
      stars.value = data
      const bench = data.benchmarks?.[0]?.id
      starSelection.value = [
        ...data.predicted.slice(0, 3).map((d) => d.id),
        ...(bench != null ? [bench] : []),
      ]
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

function applyYear(range) {
  yearRange.value = range
  if (!dYear) return
  if (!range) {
    dYear.filterAll()
    filteredIds.value = null
  } else {
    dYear.filterRange([range[0], range[1] + 1])
    filteredIds.value = new Set(dYear.top(Infinity).map((n) => n.id))
  }
}

const visibleNodes = computed(() => {
  const ids = filteredIds.value
  return ids ? allNodes.value.filter((n) => ids.has(n.id)) : allNodes.value
})
const visibleLinks = computed(() => {
  const ids = filteredIds.value
  return ids
    ? allLinks.value.filter((e) => ids.has(e.source) && ids.has(e.target))
    : allLinks.value
})

const selectedNode = computed(() =>
  selectedId.value == null ? null : idx.value.get(selectedId.value) || null
)
// who influenced the selected node (selected is the `source` / influenced)
const influencers = computed(() => {
  if (selectedId.value == null) return []
  return allLinks.value
    .filter((e) => e.source === selectedId.value)
    .map((e) => ({ node: idx.value.get(e.target), types: e.types, weight: e.weight }))
    .filter((d) => d.node)
    .sort((a, b) => b.weight - a.weight)
})
// whom the selected node influenced (selected is the `target` / influencer)
const influenced = computed(() => {
  if (selectedId.value == null) return []
  return allLinks.value
    .filter((e) => e.target === selectedId.value)
    .map((e) => ({ node: idx.value.get(e.source), types: e.types, weight: e.weight }))
    .filter((d) => d.node)
    .sort((a, b) => b.weight - a.weight)
})

function select(id) { selectedId.value = id }
function resetToCenter() { selectedId.value = center.value }

// cross-view linking: which artists exist in the influence network (Sailor's ego)
const egoIds = computed(() => new Set(allNodes.value.map((n) => n.id)))
function selectInNetwork(id) {
  selectedId.value = id
  view.value = 'artist'
}

// Task 2 derived lists (drop the genre's self-reference to highlight external genres)
const drewFrom = computed(() =>
  (genre.value?.drewFrom || [])
    .filter((d) => d.genre !== 'Oceanus Folk')
    .map((d) => ({ label: d.genre, count: d.count, color: genreColor(d.genre) }))
)
const influencedGenres = computed(() =>
  (genre.value?.influencedGenres || [])
    .filter((d) => d.genre !== 'Oceanus Folk')
    .map((d) => ({ label: d.genre, count: d.count, color: genreColor(d.genre) }))
)
const affectedArtists = computed(() =>
  (genre.value?.topAffectedArtists || []).map((d) => ({ label: d.name, count: d.works_influenced }))
)

// Task 3 helpers
const starNames = computed(() => {
  const m = {}
  for (const d of [...(stars.value?.predicted || []), ...(stars.value?.benchmarks || [])]) m[d.id] = d.name
  return m
})
const benchmarkId = computed(() => stars.value?.benchmarks?.[0]?.id ?? null)
function toggleStar(id) {
  const i = starSelection.value.indexOf(id)
  if (i === -1) starSelection.value = [...starSelection.value, id]
  else starSelection.value = starSelection.value.filter((x) => x !== id)
}
</script>

<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-700 bg-slate-900/80 px-5 py-3">
      <div>
        <h1 class="text-lg font-semibold tracking-tight text-cyan-300">
          Oceanus Folk Explorer
        </h1>
        <p class="text-xs text-slate-400">
          VAST 2025 · MC1 — the rise of Sailor Shift &amp; the spread of Oceanus Folk
        </p>
      </div>

      <nav class="flex gap-1 rounded-lg bg-slate-800 p-1 text-xs font-medium">
        <button
          class="rounded-md px-3 py-1.5 transition"
          :class="view === 'artist' ? 'bg-cyan-600 text-white' : 'text-slate-300 hover:text-white'"
          @click="view = 'artist'"
        >
          Artist · Sailor Shift
        </button>
        <button
          class="rounded-md px-3 py-1.5 transition"
          :class="view === 'genre' ? 'bg-cyan-600 text-white' : 'text-slate-300 hover:text-white'"
          @click="view = 'genre'"
        >
          Genre spread
        </button>
        <button
          class="rounded-md px-3 py-1.5 transition"
          :class="view === 'stars' ? 'bg-cyan-600 text-white' : 'text-slate-300 hover:text-white'"
          @click="view = 'stars'"
        >
          Rising stars
        </button>
      </nav>

      <div class="flex items-center gap-4 text-xs text-slate-400">
        <span v-if="!loading && !error && view === 'artist'">
          {{ allNodes.length }} artists · {{ allLinks.length }} influence links · {{ hops }}-hop ego-network
        </span>
        <span v-else-if="!loading && !error && view === 'genre' && genre">
          {{ genre.influencedGenres.length }} genres reached · {{ genre.yearRange[0] }}–{{ genre.yearRange[1] }}
        </span>
        <span v-else-if="!loading && !error && view === 'stars' && stars">
          {{ stars.predicted.length }} candidates scored · predicted to {{ stars.refYear }}
        </span>
        <span v-if="view === 'artist' && yearRange" class="rounded bg-slate-800 px-2 py-1 text-cyan-300">
          years {{ yearRange[0] }}–{{ yearRange[1] }}
          <button class="ml-1 text-slate-400 hover:text-white" @click="applyYear(null)">✕</button>
        </span>
        <button
          v-if="view === 'artist'"
          class="rounded bg-cyan-600 px-3 py-1.5 font-medium text-white hover:bg-cyan-500"
          @click="resetToCenter"
        >
          ↺ Sailor Shift
        </button>
      </div>
    </header>

    <!-- States -->
    <div v-if="loading" class="flex flex-1 items-center justify-center text-slate-400">
      Loading graph…
    </div>
    <div v-else-if="error" class="flex flex-1 items-center justify-center p-8 text-center text-rose-300">
      <div>
        <p class="font-semibold">Could not load the data.</p>
        <p class="mt-1 text-sm text-slate-400">{{ error }}</p>
        <p class="mt-3 text-xs text-slate-500">Run <code class="rounded bg-slate-800 px-1">npm run data</code> to generate <code>public/data/sailor_ego.json</code>.</p>
      </div>
    </div>

    <!-- Main -->
    <main v-else class="flex-1 overflow-hidden p-3">
    <!-- Artist view (Task 1) -->
    <div v-if="view === 'artist'" class="grid h-full grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_320px]">
      <section class="flex min-h-0 flex-col gap-3">
        <div class="min-h-0 flex-1 rounded-xl border border-slate-700 bg-slate-900/60 p-2">
          <InfluenceNetwork
            :nodes="visibleNodes"
            :links="visibleLinks"
            :selected-id="selectedId"
            :center="center"
            @select="select"
          />
        </div>
        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <div class="rounded-xl border border-slate-700 bg-slate-900/60 p-3">
            <h2 class="mb-1 text-sm font-semibold text-slate-200">Activity over time</h2>
            <p class="mb-2 text-xs text-slate-500">Drag to filter every view by year.</p>
            <Timeline :nodes="allNodes" :year-range="yearRange" @update:year-range="applyYear" />
          </div>
          <div class="rounded-xl border border-slate-700 bg-slate-900/60 p-3">
            <h2 class="mb-1 text-sm font-semibold text-slate-200">Top influencers</h2>
            <p class="mb-2 text-xs text-slate-500">Artists ranked by how many others they influenced.</p>
            <Ranking :nodes="visibleNodes" :selected-id="selectedId" @select="select" />
          </div>
        </div>
      </section>

      <aside class="min-h-0 overflow-auto rounded-xl border border-slate-700 bg-slate-900/60 p-3">
        <DetailPanel
          :node="selectedNode"
          :influencers="influencers"
          :influenced="influenced"
          @select="select"
        />
      </aside>
    </div>

    <!-- Genre-spread view (Task 2) -->
    <div v-else-if="view === 'genre'" class="grid h-full grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_300px]">
      <section class="flex min-h-0 flex-col rounded-xl border border-slate-700 bg-slate-900/60 p-3">
        <h2 class="text-sm font-semibold text-slate-200">How Oceanus Folk spread through the music world</h2>
        <p class="mb-2 text-xs text-slate-500">
          Works influenced by Oceanus Folk each year, banded by the genre they belong to.
          The dashed line is Oceanus Folk's own releases. Bursts (2017, 2020, 2023…) show an <em>intermittent</em> rise, not a gradual one.
        </p>
        <div class="min-h-0 flex-1">
          <GenreSpread
            v-if="genre"
            :spread="genre.spread"
            :of-releases="genre.ofReleasesByYear"
            :year-range="genre.yearRange"
          />
          <p v-else class="text-sm text-slate-500">
            Genre data not found. Run <code class="rounded bg-slate-800 px-1">python scripts/build_genre_spread.py</code>.
          </p>
        </div>
      </section>

      <aside class="flex min-h-0 flex-col gap-3 overflow-auto">
        <div class="rounded-xl border border-slate-700 bg-slate-900/60 p-3">
          <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Genres it drew from</h3>
          <BarList :items="drewFrom" :limit="10" />
        </div>
        <div class="rounded-xl border border-slate-700 bg-slate-900/60 p-3">
          <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Genres it influenced</h3>
          <BarList :items="influencedGenres" :limit="10" />
        </div>
        <div class="rounded-xl border border-slate-700 bg-slate-900/60 p-3">
          <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Top affected artists</h3>
          <BarList :items="affectedArtists" unit=" works" :limit="10" />
        </div>
      </aside>
    </div>

    <!-- Rising-stars view (Task 3) -->
    <div v-else class="grid h-full grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_340px]">
      <section class="flex min-h-0 flex-col rounded-xl border border-slate-700 bg-slate-900/60 p-3">
        <h2 class="text-sm font-semibold text-slate-200">Comparing career trajectories</h2>
        <p class="mb-2 text-xs text-slate-500">
          Cumulative chart hits over time. Sailor Shift (dashed) is the benchmark; steep recent
          slopes mark a rising star. Click candidates on the right to compare.
        </p>
        <div class="min-h-0 flex-1">
          <RisingStars
            v-if="stars"
            :traj="stars.traj"
            :selected-ids="starSelection"
            :names="starNames"
            :benchmark-id="benchmarkId"
          />
          <p v-else class="text-sm text-slate-500">
            Rising-star data not found. Run <code class="rounded bg-slate-800 px-1">python scripts/build_rising_stars.py</code>.
          </p>
        </div>
      </section>

      <aside class="min-h-0 overflow-auto rounded-xl border border-slate-700 bg-slate-900/60 p-3">
        <h3 class="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">Predicted next Oceanus Folk stars</h3>
        <p class="mb-2 text-[11px] text-slate-500">Ranked by Rising Star Score. Bar shows the score's makeup.</p>
        <StarLeaderboard
          v-if="stars"
          :predicted="stars.predicted"
          :benchmark="stars.benchmarks[0]"
          :weights="stars.weights"
          :selected-ids="starSelection"
          :ego-ids="egoIds"
          :selected-id="selectedId"
          @toggle="toggleStar"
          @open="selectInNetwork"
        />
      </aside>
    </div>
    </main>
  </div>
</template>
