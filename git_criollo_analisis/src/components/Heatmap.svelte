<script>
  // Heatmap de actividad estilo GitHub, renderizado server-side (sin JS).
  // data: [{ date: "YYYY-MM-DD", count: n }, ...]
  let { data = [] } = $props();

  const counts = new Map(data.map((d) => [d.date, d.count]));

  const today = new Date();
  const dow = (today.getDay() + 6) % 7; // lunes = 0
  const start = new Date(today);
  start.setDate(today.getDate() - dow - 52 * 7);

  function level(count) {
    if (count <= 0) return 0;
    if (count <= 2) return 1;
    if (count <= 4) return 2;
    if (count <= 7) return 3;
    return 4;
  }

  function fmt(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  const weeks = [];
  for (let w = 0; w < 53; w++) {
    const column = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + w * 7 + i);
      const key = fmt(d);
      const count = counts.get(key) ?? 0;
      column.push({ key, count, level: level(count) });
    }
    weeks.push(column);
  }
</script>

<div class="heatmap">
  {#each weeks as week}
    <div class="heatmap-week">
      {#each week as cell}
        <div
          class="heatmap-cell level-{cell.level}"
          title="{cell.key}: {cell.count} commit{cell.count === 1 ? "" : "s"}"
        ></div>
      {/each}
    </div>
  {/each}
</div>

<style>
  .heatmap {
    display: flex;
    gap: 3px;
    overflow-x: auto;
    padding-bottom: 4px;
  }
  .heatmap-week {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .heatmap-cell {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    background: #161b22;
  }
  .level-1 { background: #0e4429; }
  .level-2 { background: #006d32; }
  .level-3 { background: #26a641; }
  .level-4 { background: #39d353; }
</style>