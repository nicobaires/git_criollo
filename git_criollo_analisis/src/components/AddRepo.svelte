<script lang="ts">
  let open = false;
  let repoPath = "";
  let loading = false;
  let error = "";
  let success = "";

  async function submit() {
    error = "";
    success = "";
    loading = true;
    try {
      const res = await fetch("/api/repos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: repoPath }),
      });
      const data = await res.json();
      if (!res.ok) {
        error = data.error ?? "No se pudo agregar el repositorio";
        return;
      }
      success = `Repo "${data.repo.name}" agregado. Generando datos...`;
      open = false;
      setTimeout(() => window.location.reload(), 3500);
    } catch {
      error = "Error de conexión con el servidor";
    } finally {
      loading = false;
    }
  }

  function cancel() {
    open = false;
    error = "";
    repoPath = "";
  }
</script>

<div class="ml-auto">
  {#if !open}
    <button type="button" class="rounded-full border border-gh-border bg-gh-card text-gh-text text-[13px] px-3.5 py-1.5 cursor-pointer transition-colors hover:text-gh-hover hover:border-gh-accent" onclick={() => (open = true)}>
      + Agregar repo
    </button>
  {:else}
    <form class="flex gap-2 flex-wrap" onsubmit={(e) => { e.preventDefault(); submit(); }}>
      <input
        type="text"
        class="py-1.5 px-3 rounded-lg border border-gh-border bg-gh-bg text-gh-text font-mono text-[13px] min-w-[260px] outline-none focus:border-gh-accent"
        bind:value={repoPath}
        placeholder="/ruta/al/repo"
        aria-label="Ruta de la carpeta del repositorio"
      />
      <button type="submit" class="rounded-full border border-gh-border bg-gh-card text-gh-text text-[13px] px-3.5 py-1.5 cursor-pointer transition-colors hover:text-gh-hover hover:border-gh-accent disabled:opacity-60 disabled:cursor-default" disabled={loading}>
        {loading ? "Verificando..." : "Agregar"}
      </button>
      <button type="button" class="rounded-full border border-gh-border bg-gh-card text-gh-muted text-[13px] px-3.5 py-1.5 cursor-pointer transition-colors hover:text-gh-hover hover:border-gh-accent" onclick={cancel}>
        Cancelar
      </button>
    </form>
  {/if}
  {#if error}
    <p class="text-gh-danger text-[13px] mt-2">{error}</p>
  {/if}
  {#if success}
    <p class="text-gh-success text-[13px] mt-2">{success}</p>
  {/if}
</div>
