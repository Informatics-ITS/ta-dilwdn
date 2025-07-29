<script>
	import * as d3 from "d3";
	
	export let stats;
	export let xAccessorScaled;
	export let yAccessorScaled;

	const interpolation = d3.curveMonotoneX;

	$: lineGenerator = d3.line().x(xAccessorScaled).y(yAccessorScaled).curve(interpolation);

	$: line = lineGenerator(stats);
</script>

<path 
	class="line" 
	d={line} 
/>

<style>
  .line {
    fill: none;
    stroke: #4427ca;
    stroke-width: 3px;
    stroke-linecap: round;
  }
</style>
