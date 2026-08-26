<script>
  const MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
  // Solo algunos labels de día, como GitHub
  const DIAS = ["L", "", "X", "", "V", "", ""];

  const CELL = 12; // px
  const GAP = 3;  // px

  let { data = [], year = new Date().getFullYear() } = $props();

  function fmt(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  function level(count) {
    // Escala fija: más legible que relativa al max
    if (count <= 0) return 0;
    if (count === 1) return 1;
    if (count <= 3) return 2;
    if (count <= 6) return 3;
    return 4;
  }

  const { totalCommits, topDay, activeDays, weeks, monthMarkers } = $derived.by(() => {
    const counts = new Map(data.map((d) => [d.date, d.count]));
    const totalCommits = data.reduce((a, d) => a + d.count, 0);
    const topDay = data.reduce((a, b) => (b.count > (a?.count ?? 0) ? b : a), null);
    const activeDays = data.filter((d) => d.count > 0).length;

    // Lunes de la semana que contiene el 1 de enero
    const jan1 = new Date(year, 0, 1);
    const dec31 = new Date(year, 11, 31);
    const dowJan1 = (jan1.getDay() + 6) % 7; // lun=0 … dom=6
    const start = new Date(jan1);
    start.setDate(jan1.getDate() - dowJan1);

    const weeks = [];
    // month -> índice de la primera semana que toca ese mes (dentro de este año)
    const firstWeekOfMonth = new Map();

    let week = [];
    let weekIndex = 0;
    const cursor = new Date(start);

    while (cursor <= dec31 || week.length > 0) {
      // Cerrar última semana incompleta
      if (cursor > dec31 && week.length > 0) {
        while (week.length < 7) {
          week.push({ key: "", count: 0, level: 0, empty: true, outOfYear: true });
        }
        weeks.push(week);
        break;
      }

      const inYear = cursor.getFullYear() === year;
      const key = fmt(cursor);
      const count = inYear ? (counts.get(key) ?? 0) : 0;
      const month = cursor.getMonth(); // 0–11

      // Primera semana que tiene un día de este mes (solo del year)
      if (inYear && !firstWeekOfMonth.has(month)) {
        firstWeekOfMonth.set(month, weekIndex);
      }

      week.push({
        key: inYear ? key : "",
        count,
        level: inYear ? level(count) : 0,
        empty: false,
        outOfYear: !inYear,
      });

      if (week.length === 7) {
        weeks.push(week);
        week = [];
        weekIndex += 1;
      }
      cursor.setDate(cursor.getDate() + 1);
    }

    // Marcadores de mes: { label, weekIndex }
    const monthMarkers = [...firstWeekOfMonth.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([month, wi]) => ({
        label: MESES[month],
        weekIndex: wi,
      }));

    return { totalCommits, topDay, activeDays, weeks, monthMarkers };
  });

  const levelBg = ["bg-heat-0", "bg-heat-1", "bg-heat-2", "bg-heat-3", "bg-heat-4"];
  const step = CELL + GAP; // 15px
  const daysColWidth = 14; // espacio labels L/X/V
</script>

<div class="text-gh-muted text-xs mb-3">
  {activeDays} días activos · {totalCommits} commits
  {#if topDay}· pico de {topDay.count} el {topDay.date}{/if}
</div>

<div class="inline-flex flex-col gap-1">
  <!-- Fila de meses: posicionamiento absoluto por weekIndex -->
  <div
    class="relative h-4"
    style="margin-left: {daysColWidth}px; width: {weeks.length * step - GAP}px"
  >
    {#each monthMarkers as m}
      <span
        class="absolute top-0 text-[10px] text-gh-muted whitespace-nowrap"
        style="left: {m.weekIndex * step}px"
      >
        {m.label}
      </span>
    {/each}
  </div>

  <div class="flex gap-1.5">
    <!-- Días de la semana -->
    <div class="flex flex-col gap-[3px]" style="width: {daysColWidth}px">
      {#each DIAS as d}
        <span class="h-3 text-[10px] leading-3 text-gh-muted text-right pr-0.5">{d}</span>
      {/each}
    </div>

    <!-- Grilla -->
    <div class="flex gap-[3px]">
      {#each weeks as week}
        <div class="flex flex-col gap-[3px]">
          {#each week as cell}
            {#if cell.outOfYear}
              <div class="w-3 h-3 rounded-sm opacity-0"></div>
            {:else}
              <div
                class="w-3 h-3 rounded-sm {levelBg[cell.level]}"
                title={cell.key ? `${cell.key}: ${cell.count} commit${cell.count === 1 ? "" : "s"}` : ""}
              ></div>
            {/if}
          {/each}
        </div>
      {/each}
    </div>
  </div>

  <!-- Leyenda -->
  <div class="flex items-center gap-1 mt-2 text-[11px] text-gh-muted" style="margin-left: {daysColWidth}px">
    <span>Menos</span>
    {#each [0, 1, 2, 3, 4] as l}
      <span class="w-2.5 h-2.5 rounded-sm {levelBg[l]}"></span>
    {/each}
    <span>Más</span>
  </div>
</div>
