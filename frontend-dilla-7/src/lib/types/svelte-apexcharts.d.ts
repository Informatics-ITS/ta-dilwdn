declare module 'svelte-apexcharts' {
  import { SvelteComponentTyped } from 'svelte'

  export interface ApexChartProps {
    type: 'line' | 'bar' | 'pie' | string
    width?: number | string
    height?: number | string
    options: Record<string, unknown>
    series: unknown[]
  }

  export class ApexChart extends SvelteComponentTyped<ApexChartProps> {}
}
