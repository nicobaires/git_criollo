<script>
  import { Chart, registerables } from "chart.js";
  import { onMount } from "svelte";

  Chart.register(...registerables);
  Chart.defaults.color = "#8b949e";
  Chart.defaults.borderColor = "rgba(139, 148, 158, 0.12)";
  Chart.defaults.font.family = "-apple-system, 'Segoe UI', Roboto, sans-serif";

  let { type = "bar", data, options = {} } = $props();
  let canvas;
  let chart;

  onMount(() => {
    if (!canvas) return;
    try {
      chart = new Chart(canvas, { type, data, options });
    } catch (err) {
      console.error("[Chart] error al crear el gráfico:", err);
    }
    return () => chart?.destroy();
  });
</script>

<div class="chart-container">
  <canvas bind:this={canvas}></canvas>
</div>

<style>
  .chart-container {
    position: relative;
    width: 100%;
    height: 100%;
  }
  canvas {
    display: block;
    width: 100% !important;
    height: 100% !important;
  }
</style>