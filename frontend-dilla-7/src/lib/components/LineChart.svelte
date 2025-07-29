<script lang="ts">
  import * as d3 from 'd3'
  import Line from './LineCharts/Line.svelte'
  import GridLines from './LineCharts/GridLines.svelte'
  import Crosshair from './LineCharts/Crosshair.svelte'

  export let filteredKesalahan: { nomor: string; totalKesalahan: number }[]

  let width = 700
  let height = 250
  let margin = { top: 10, right: 20, bottom: 50, left: 40 }

  $: innerWidth = width - margin.left - margin.right
  $: innerHeight = height - margin.top - margin.bottom

  $: xScale = d3
    .scalePoint()
    .domain(filteredKesalahan.map((d) => d.nomor))
    .range([0, innerWidth])
    .padding(0.5)

  $: yScale = d3
    .scaleLinear()
    .domain([0, d3.max(filteredKesalahan, (d) => d.totalKesalahan) ?? 10])
    .nice()
    .range([innerHeight, 0])

  $: hoveredIndex = null
  $: hoveredPoint = hoveredIndex !== null ? filteredKesalahan[hoveredIndex] : null

  function handleMouseMove(event: MouseEvent) {
    const x = event.offsetX - margin.left
    const index = d3.scan(filteredKesalahan, (a, b) => Math.abs(xScale(a.nomor)! - x) - Math.abs(xScale(b.nomor)! - x))
    hoveredIndex = index
  }

  function handleMouseLeave() {
    hoveredIndex = null
  }
</script>

<div class="chart-wrapper">
  <svg role="presentation" viewBox={`0 0 ${width} ${height}`} on:mousemove={handleMouseMove} on:mouseleave={handleMouseLeave}>
    <g transform={`translate(${margin.left},${margin.top})`}>
      <GridLines {yScale} {innerWidth} label="Kesalahan" {hoveredPoint} />

      <Line stats={filteredKesalahan} xAccessorScaled={(d) => xScale(d.nomor)} yAccessorScaled={(d) => yScale(d.totalKesalahan)} />

      {#each filteredKesalahan as point}
        <text x={xScale(point.nomor)} y={innerHeight + 20} text-anchor="middle" font-size="10" fill="#555">
          {point.nomor}
        </text>
      {/each}

      {#if hoveredPoint}
        <circle cx={xScale(hoveredPoint.nomor)} cy={yScale(hoveredPoint.totalKesalahan)} r="5" fill="#206eff" />
        <Crosshair xAccessorScaled={xScale(hoveredPoint.nomor)} yAccessorScaled={yScale(hoveredPoint.totalKesalahan)} xLabel={hoveredPoint.nomor} yLabel={hoveredPoint.totalKesalahan} {innerHeight} />
      {/if}
    </g>
  </svg>
</div>

<style>
  .chart-wrapper {
    width: 100%;
    overflow-x: auto;
  }

  svg {
    display: block;
    height: auto;
  }

  text {
    font-family: sans-serif;
  }
</style>
