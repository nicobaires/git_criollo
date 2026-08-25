<script lang="ts">
  let { repo, years, current, currentBranch } = $props();
  let open = $state(false);

  function selectYear(year: string) {
    if (year === current) { open = false; return; }
    const params = new URLSearchParams();
    if (currentBranch) params.set("branch", currentBranch);
    if (year !== "all") params.set("year", year);
    window.location.href = `/repo/${repo}?${params.toString()}`;
  }
</script>

<div class="relative">
  <button
    type="button"
    class="flex items-center gap-1.5 rounded-full border border-gh-border bg-gh-card text-gh-text text-[13px] px-3 py-1 cursor-pointer transition-colors hover:border-gh-accent hover:text-gh-hover"
    onclick={() => (open = !open)}
  >
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" class="text-gh-muted">
      <path d="M3.75 2a.75.75 0 01.75.75V4h7V2.75a.75.75 0 011.5 0V4h.25A2.75 2.75 0 0116 6.75v5.5A2.75 2.75 0 0113.25 15H2.75A2.75 2.75 0 010 12.25v-5.5A2.75 2.75 0 012.75 4H3V2.75A.75.75 0 013.75 2zM2.75 5.5a1.25 1.25 0 00-1.25 1.25v5.5c0 .69.56 1.25 1.25 1.25h10.5a1.25 1.25 0 001.25-1.25v-5.5a1.25 1.25 0 00-1.25-1.25H2.75z"/>
    </svg>
    {current === "all" ? "Todos los años" : current}
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" class="text-gh-muted">
      <path d="M4.427 7.427l3.396 3.396a.25.25 0 00.354 0l3.396-3.396A.25.25 0 0011.396 7H4.604a.25.25 0 00-.177.427z"/>
    </svg>
  </button>

  {#if open}
    <div class="absolute top-full left-0 mt-1 bg-gh-card border border-gh-border rounded-xl shadow-lg z-50 min-w-[180px]">
      {#each ["all", ...years].reverse() as y, i}
        {#if i > 0}<div class="border-t border-gh-border"></div>{/if}
        <button
          type="button"
          class:list={[
            "w-full text-left px-3 py-2 text-[13px] cursor-pointer",
            y === current
              ? "text-gh-accent bg-[rgba(88,166,255,0.1)]"
              : "text-gh-text hover:bg-[rgba(139,148,158,0.1)]",
          ]}
          onclick={() => selectYear(String(y))}
        >
          {y === "all" ? "Todos los años" : y}
        </button>
      {/each}
    </div>
  {/if}
</div>
