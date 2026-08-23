<script lang="ts">
  let { repo, current } = $props();
  let branches = $state<{ name: string; hasStats: boolean }[]>([]);
  let loading = $state("");
  let open = $state(false);

  async function loadBranches() {
    try {
      const res = await fetch(`/api/branches?repo=${encodeURIComponent(repo)}`);
      const data = await res.json();
      branches = data.branches ?? [];
    } catch {
      branches = [];
    }
  }

  $effect(() => {
    if (open && branches.length === 0) {
      loadBranches();
    }
  });

  function switchBranch(branch: string) {
    if (branch === current) { open = false; return; }
    loading = branch;
    window.location.href = `/repo/${repo}?branch=${encodeURIComponent(branch)}`;
  }

  async function generateBranch(branch: string) {
    loading = branch;
    try {
      await fetch("/api/branches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo, branch }),
      });
      window.location.href = `/repo/${repo}?branch=${encodeURIComponent(branch)}`;
    } catch {
      loading = "";
    }
  }
</script>

<div class="relative">
  <button
    type="button"
    class="flex items-center gap-1.5 rounded-full border border-gh-border bg-gh-card text-gh-text text-[13px] px-3 py-1 cursor-pointer transition-colors hover:border-gh-accent hover:text-gh-hover"
    onclick={() => (open = !open)}
  >
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" class="text-gh-muted">
      <path d="M9.5 3.25a2.25 2.25 0 1 1-3 2.122V6A2.5 2.5 0 0 0 9 8.5h1.25a2.25 2.25 0 1 1 0 1.5H9A4 4 0 0 1 5 6V5.372a2.25 2.25 0 1 1 1.5 0V6a2.5 2.5 0 0 0 2.5 2.5h1.25v-.628a2.25 2.25 0 0 1 1.25-2.122zM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5zM8 12.5a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0z"/>
    </svg>
    {current}
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" class="text-gh-muted">
      <path d="M4.427 7.427l3.396 3.396a.25.25 0 00.354 0l3.396-3.396A.25.25 0 0011.396 7H4.604a.25.25 0 00-.177.427z"/>
    </svg>
  </button>

  {#if open}
    <div class="absolute top-full left-0 mt-1 bg-gh-card border border-gh-border rounded-xl shadow-lg z-50 py-1 min-w-[240px] max-h-[320px] overflow-y-auto">
      {#each branches as b}
        {#if b.name === current}
          <button
            type="button"
            class="w-full text-left px-3 py-1.5 text-[13px] text-gh-accent bg-[rgba(88,166,255,0.1)] cursor-default flex items-center gap-2"
            onclick={() => (open = false)}
          >
            <span class="truncate">{b.name}</span>
            <span class="text-gh-muted text-[11px] shrink-0">actual</span>
          </button>
        {:else if b.hasStats}
          <button
            type="button"
            class="w-full text-left px-3 py-1.5 text-[13px] text-gh-text hover:bg-[rgba(139,148,158,0.1)] cursor-pointer disabled:opacity-50 flex items-center gap-2"
            disabled={loading !== ""}
            onclick={() => switchBranch(b.name)}
          >
            <span class="truncate">{b.name}</span>
            {#if loading === b.name}
              <span class="text-gh-muted text-[11px] shrink-0">cargando...</span>
            {/if}
          </button>
        {:else}
          <button
            type="button"
            class="w-full text-left px-3 py-1.5 text-[13px] text-gh-subtle hover:bg-[rgba(139,148,158,0.1)] cursor-pointer disabled:opacity-50 flex items-center gap-2"
            disabled={loading !== ""}
            onclick={() => generateBranch(b.name)}
          >
            <span class="truncate">{b.name}</span>
            {#if loading === b.name}
              <span class="text-gh-accent text-[11px] shrink-0">generando...</span>
            {:else}
              <span class="text-gh-muted text-[11px] shrink-0">generar</span>
            {/if}
          </button>
        {/if}
      {/each}
      {#if branches.length === 0 && loading === ""}
        <p class="px-3 py-1.5 text-[13px] text-gh-muted m-0">Cargando branches...</p>
      {/if}
    </div>
  {/if}
</div>
