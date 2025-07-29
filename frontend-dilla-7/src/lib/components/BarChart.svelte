<script lang="ts">
  import * as d3 from 'd3'

  export let players: { name: string; threePointers: number }[] = []

  const formatLabel = d3.format(',.0f')

  const margin = { top: 30, right: 60, bottom: 20, left: 30 }

  let containerWidth = 700
  let barHeight = 28

  $: chartHeight = players.length * barHeight + margin.top + margin.bottom
  $: innerWidth = containerWidth - margin.left - margin.right
  $: innerHeight = chartHeight - margin.top - margin.bottom

  $: xScale = d3
    .scaleLinear()
    .domain([0, d3.max(players, (d) => d.threePointers) ?? 100])
    .range([0, innerWidth])

  // Gunakan index sebagai domain untuk support nama duplikat
  $: yScale = d3
    .scaleBand()
    .domain(players.map((_, i) => i.toString()))
    .range([0, innerHeight])
    .padding(0.1)

  const colorScale = d3.scaleOrdinal(d3.schemeTableau10)
</script>

<div class="wrapper" bind:clientWidth={containerWidth}>
  <svg viewBox={`0 0 ${containerWidth} ${chartHeight}`} preserveAspectRatio="xMinYMin meet" class="w-full h-auto">
    <g transform={`translate(${margin.left}, ${margin.top})`}>
      {#each players as player, i}
        <g>
          <path
            d={`M0,${yScale(i.toString())}
                h${xScale(player.threePointers) - 6}
                a6,${yScale.bandwidth() / 2} 0 0 1 0,${yScale.bandwidth()}
                h-${xScale(player.threePointers) - 6}
                z`}
            fill={colorScale(player.name + i)}
          />
          <text x={10} y={yScale(i.toString()) + yScale.bandwidth() / 2} dy=".35em" fill="white" font-size="11px" font-weight="bold">
            {player.name}
          </text>
          <text x={xScale(player.threePointers) + 10} y={yScale(i.toString()) + yScale.bandwidth() / 2} dy=".35em" fill="#333" font-size="12px" font-weight="bold">
            {formatLabel(player.threePointers)}
          </text>
        </g>
      {/each}
    </g>
  </svg>
</div>

<style>
  .wrapper {
    width: 100%;
  }

  svg {
    display: block;
  }
</style>
