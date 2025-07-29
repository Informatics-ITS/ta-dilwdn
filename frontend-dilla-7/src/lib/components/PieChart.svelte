<script lang="ts">
  import * as d3 from 'd3'

  export let data: { name: string; value: number }[] = []

  const size = 200
  const radius = size / 2 - 10

  const pie = d3
    .pie<{ name: string; value: number }>()
    .sort(null)
    .value((d) => d.value)

  const arc = d3.arc<d3.PieArcDatum<{ name: string; value: number }>>().innerRadius(0).outerRadius(radius)

  const arcLabel = d3
    .arc<d3.PieArcDatum<{ name: string; value: number }>>()
    .innerRadius(radius * 0.6)
    .outerRadius(radius * 0.6)

  // Manual color mapping
  const colorMap = {
    Lulus: '#7B1FA2',
    'Tidak Lulus': '#E040FB'
  }

  $: arcs = pie(data)
</script>

<div class="flex flex-col items-center gap-4">
  <svg viewBox={`0 0 ${size} ${size}`} class="w-full max-w-xs h-auto">
    <g transform={`translate(${size / 2}, ${size / 2})`}>
      {#each arcs as arcData}
        <path d={arc(arcData) ?? ''} fill={colorMap[arcData.data.name] ?? '#ccc'} stroke="#fff" />
        <text transform="translate({arcLabel.centroid(arcData)})" text-anchor="middle" font-size="13" font-weight="bold" fill="#fff">
          {arcData.data.value} orang
        </text>
      {/each}
    </g>
  </svg>

  <!-- Legend -->
  <div class="flex gap-12 text-sm">
    {#each data as item}
      <div class="flex items-center gap-2">
        <span class="w-6 h-6 rounded-full" style="background-color: {colorMap[item.name]};"></span>
        <span class="text-lg">{item.name}</span>
      </div>
    {/each}
  </div>
</div>

<style>
  svg {
    font-family: 'Inter', sans-serif;
  }
</style>
