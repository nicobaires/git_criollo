<script>
  // Heatmap de actividad estilo GitHub, renderizado server-side (sin JS).
  // data: [{ date: "YYYY-MM-DD", count: n }, ...]
  // Rango dinámico: lunes de la semana del primer día activo → hoy.
  let { data = [] } = $props();

  const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  const DIAS = ["L", "M", "X", "J", "V", "S", "D"];

  function fmt(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  // parsea "YYYY-MM-DD" como fecha LOCAL (new Date("YYYY-MM-DD") es UTC y
  // desplaza el día en husos negativos: medianoche UTC = 21:00 del día anterior)
  function parseDate(key) {
    const [y, m, d] = key.split("-").map(Number);
    return new Date(y, m - 1, d);
  }

  const { counts, maxCount, totalCommits, topDay, hasData, weeks, monthLabels } = $derived.by(() => {
    const counts = new Map(data.map((d) => [d.date, d.count]));
    const maxCount = data.length ? Math.max(...data.map((d) => d.count)) : 0;
    const totalCommits = data.reduce((a, d) => a + d.count, 0);
    const topDay = data.reduce((a, b) => (b.count > (a?.count ?? 0) ? b : a), null);

    const today = new Date();
    const end = today;

    let start;
    if (data.length) {
      const first = parseDate([...data.map((d) => d.date)].sort()[0]);
      const dow = (first.getDay() + 6) % 7; // lunes = 0
      start = new Date(first);
      start.setDate(first.getDate() - dow);
    } else {
      const dow = (today.getDay() + 6) % 7;
      start = new Date(today);
      start.setDate(today.getDate() - dow);
    }

    const hasData = data.length > 0 && start <= end;

    function level(count) {
      if (count <= 0 || maxCount <= 0) return 0;
      const pct = count / maxCount;
      if (pct <= 0.25) return 1;
      if (pct <= 0.5) return 2;
      if (pct <= 0.75) return 3;
      return 4;
    }

    const weeks = [];
    const monthLabels = [];
    if (hasData) {
      let week = [];
      let prevMonthKey = null;
      const cursor = new Date(start);
      while (cursor <= end) {
        if (week.length === 0) {
          const monthKey = `${cursor.getFullYear()}-${cursor.getMonth()}`;
          monthLabels.push(prevMonthKey === monthKey ? "" : MESES[cursor.getMonth()]);
          prevMonthKey = monthKey;
        }
        const key = fmt(cursor);
        const count = counts.get(key) ?? 0;
        week.push({ key, count, level: level(count) });
        if (week.length === 7) {
          weeks.push(week);
          week = [];
        }
        cursor.setDate(cursor.getDate() + 1);
      }
      if (week.length) weeks.push(week);
    }

    return { counts, maxCount, totalCommits, topDay, hasData, weeks, monthLabels };
  });
</script>

{#if !hasData}
  <p class="empty">Sin actividad en el periodo analizado</p>
{:else}
  <div class="heatmap-summary">
    {counts.size} días activos · {totalCommits} commits
    {#if topDay}· pico de {topDay.count} el {topDay.date}{/if}
  </div>
  <div class="heatmap">
    <div class="heatmap-months">
      {#each weeks as _, wi}
        <span class="heatmap-month-label">{monthLabels[wi]}</span>
      {/each}
    </div>
    <div class="heatmap-body">
      <div class="heatmap-days">
        {#each DIAS as d}
          <span class="heatmap-day-label">{d}</span>
        {/each}
      </div>
      <div class="heatmap-grid">
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
    </div>
    <div class="heatmap-legend">
      <span>Menos</span>
      <span class="heatmap-cell level-0"></span>
      <span class="heatmap-cell level-1"></span>
      <span class="heatmap-cell level-2"></span>
      <span class="heatmap-cell level-3"></span>
      <span class="heatmap-cell level-4"></span>
      <span>Más</span>
    </div>
  </div>
{/if}

<style>
  .empty { color: #8b949e; font-size: 14px; }
  .heatmap-summary {
    color: #8b949e;
    font-size: 12px;
    margin-bottom: 12px;
  }
  .heatmap {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .heatmap-months {
    display: flex;
    gap: 3px;
    margin-left: 20px;
  }
  .heatmap-month-label {
    flex: 0 0 12px;
    font-size: 10px;
    color: #8b949e;
    white-space: nowrap;
  }
  .heatmap-body {
    display: flex;
    gap: 6px;
  }
  .heatmap-days {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .heatmap-day-label {
    width: 10px;
    font-size: 10px;
    line-height: 12px;
    color: #8b949e;
    text-align: center;
  }
  .heatmap-grid {
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
  .heatmap-legend {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    font-size: 11px;
    color: #8b949e;
  }
  .heatmap-legend .heatmap-cell {
    width: 10px;
    height: 10px;
  }
</style>