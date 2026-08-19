<script>
  import { Chart, registerables } from "chart.js";

  Chart.register(...registerables);
  Chart.defaults.color = "#8b949e";
  Chart.defaults.borderColor = "rgba(139, 148, 158, 0.12)";
  Chart.defaults.font.family = "-apple-system, 'Segoe UI', Roboto, sans-serif";

  let { type = "bar", data, options = {} } = $props();
  let canvas;

  $effect(() => {
    const chart = new Chart(canvas, { type, data, options });
    return () => chart.destroy();
  });
</script>

<canvas bind:this={canvas}></canvas>