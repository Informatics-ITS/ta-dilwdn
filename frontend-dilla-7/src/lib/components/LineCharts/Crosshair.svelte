<script>
  export let xAccessorScaled
  export let yAccessorScaled
  export let xLabel
  export let yLabel
  export let innerHeight

  import * as d3 from 'd3'

  const formatYLabel = d3.format(',.0f')
</script>

<g transform={`translate(${xAccessorScaled} 0)`}>
  <text class="text-outline" y={innerHeight + 10} dy="0.8em" text-anchor="middle">
    {xLabel}
  </text>
  <text class="text" y={innerHeight + 10} dy="0.8em" text-anchor="middle">
    {xLabel}
  </text>
  <line class="line-outline" x1={0} x2={0} y1={yAccessorScaled} y2={innerHeight} />
  <line class="line" x1={0} x2={0} y1={yAccessorScaled} y2={innerHeight} />
</g>

<g transform={`translate(0 ${yAccessorScaled})`}>
  <text class="text-outline" dx={-10} dy="0.34em" text-anchor="end">
    {formatYLabel(yLabel)}
  </text>
  <text class="text" dx={-10} dy="0.34em" text-anchor="end">
    {formatYLabel(yLabel)}
  </text>
  <line class="line-outline" x1={xAccessorScaled} x2={0} y1={0} y2={0} />
  <line class="line" x1={xAccessorScaled} x2={0} y1={0} y2={0} />
</g>

<style>
  .text-outline {
    stroke: #ffffff;
    stroke-width: 8;
  }

  .text {
    fill: #dc267f;
  }

  .line-outline {
    stroke: #ffffff;
    stroke-width: 3;
  }

  .line {
    stroke: #dc267f;
    stroke-width: 1;
  }
</style>
