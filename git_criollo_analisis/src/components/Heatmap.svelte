<script>
  const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  const DIAS = ["L", "M", "X", "J", "V", "S", "D"];

  let { data = [] } = $props();

  function fmt(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

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
      const dow = (first.getDay() + 6) % 7;
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

  const levelBg = ["bg-heat-0", "bg-heat-1", "bg-heat-2", "bg-heat-3", "bg-heat-4"];
</script>

{#if !hasData}
  <p class="text-gh-muted text-sm">Sin actividad en el periodo analizado</p>
{:else}
  <div class="text-gh-muted text-xs mb-3">
    {counts.size} días activos · {totalCommits} commits
    {#if topDay}· pico de {topDay.count} el {topDay.date}{/if}
  </div>
  <div class="flex flex-col gap-1">
    <div class="flex gap-[3px] ml-5">
      {#each weeks as _, wi}
        <span class="flex-none w-3 text-[10px] text-gh-muted whitespace-nowrap">{monthLabels[wi]}</span>
      {/each}
    </div>
    <div class="flex gap-1.5">
      <div class="flex flex-col gap-[3px]">
        {#each DIAS as d}
          <span class="w-2.5 text-[10px] leading-3 text-gh-muted text-center">{d}</span>
        {/each}
      </div>
      <div class="flex gap-[3px] overflow-x-auto pb-1">
        {#each weeks as week}
          <div class="flex flex-col gap-[3px]">
            {#each week as cell}
              <div
                class="w-3 h-3 rounded-sm {levelBg[cell.level]}"
                title="{cell.key}: {cell.count} commit{cell.count === 1 ? "" : "s"}"
              ></div>
            {/each}
          </div>
        {/each}
      </div>
    </div>
    <div class="flex items-center gap-1 mt-2 text-[11px] text-gh-muted">
      <span>Menos</span>
      {#each [0,1,2,3,4] as l}
        <span class="w-2.5 h-2.5 {levelBg[l]}"></span>
      {/each}
      <span>Más</span>
    </div>
  </div>
{/if}
