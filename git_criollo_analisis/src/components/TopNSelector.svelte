<script lang="ts">
  let { repo, totalAuthors, current, currentBranch, currentYear } = $props();
  let open = $state(false);

  const options = [6, 10, 15, 20];
  const showAll = current === "all";

  function selectTop(n: string) {
    if (n === String(current)) { open = false; return; }
    const params = new URLSearchParams();
    if (currentBranch) params.set("branch", currentBranch);
    if (currentYear && currentYear !== "all") params.set("year", currentYear);
    if (n !== "6") params.set("top", n);
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
      <path d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1h-8a1 1 0 00-1 1v6.708A2.486 2.486 0 014.5 9h8V1.5zM5 12.25a.25.25 0 01.25-.25h3.5a.25.25 0 01.25.25v3.25a.25.25 0 01-.4.2l-1.45-1.087a.25.25 0 00-.3 0L5.4 15.7a.25.25 0 01-.4-.2v-3.25z"/>
    </svg>
    Top {showAll ? "Todos" : current}
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" class="text-gh-muted">
      <path d="M4.427 7.427l3.396 3.396a.25.25 0 00.354 0l3.396-3.396A.25.25 0 0011.396 7H4.604a.25.25 0 00-.177.427z"/>
    </svg>
  </button>

  {#if open}
    <div class="absolute top-full left-0 mt-1 bg-gh-card border border-gh-border rounded-xl shadow-lg z-50 py-1 min-w-[140px]">
      {#each options as n}
        {#if n <= totalAuthors}
          {#if String(n) === current}
            <button
              type="button"
              class="w-full text-left px-3 py-1.5 text-[13px] text-gh-accent bg-[rgba(88,166,255,0.1)] cursor-default"
              onclick={() => (open = false)}
            >
              Top {n}
            </button>
          {:else}
            <button
              type="button"
              class="w-full text-left px-3 py-1.5 text-[13px] text-gh-text hover:bg-[rgba(139,148,158,0.1)] cursor-pointer"
              onclick={() => selectTop(String(n))}
            >
              Top {n}
            </button>
          {/if}
        {/if}
      {/each}
    </div>
  {/if}
</div>
