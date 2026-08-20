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

<div class="add-repo">
  {#if !open}
    <button type="button" class="add-btn" onclick={() => (open = true)}>
      + Agregar repo
    </button>
  {:else}
    <form class="add-form" onsubmit={(e) => { e.preventDefault(); submit(); }}>
      <input
        type="text"
        class="add-input"
        bind:value={repoPath}
        placeholder="/ruta/al/repo"
        aria-label="Ruta de la carpeta del repositorio"
      />
      <button type="submit" class="add-btn" disabled={loading}>
        {loading ? "Verificando..." : "Agregar"}
      </button>
      <button type="button" class="add-btn add-btn-ghost" onclick={cancel}>
        Cancelar
      </button>
    </form>
  {/if}
  {#if error}
    <p class="add-error">{error}</p>
  {/if}
  {#if success}
    <p class="add-success">{success}</p>
  {/if}
</div>

<style>
  .add-repo {
    margin-left: auto;
  }
  .add-btn {
    padding: 6px 14px;
    border-radius: 999px;
    border: 1px solid #21262d;
    background: #161b22;
    color: #c9d1d9;
    font-size: 13px;
    cursor: pointer;
    transition: color 0.15s, border-color 0.15s;
  }
  .add-btn:hover:not(:disabled) {
    color: #e6edf3;
    border-color: #58a6ff;
  }
  .add-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }
  .add-btn-ghost {
    color: #8b949e;
  }
  .add-form {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .add-input {
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid #21262d;
    background: #0d1117;
    color: #c9d1d9;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 13px;
    min-width: 260px;
  }
  .add-input:focus {
    outline: none;
    border-color: #58a6ff;
  }
  .add-error {
    color: #f85149;
    font-size: 13px;
    margin: 8px 0 0;
  }
  .add-success {
    color: #3fb950;
    font-size: 13px;
    margin: 8px 0 0;
  }
</style>