<script lang="ts">
  export let name: string;

  let confirming = false;
  let error = "";
  let busy = false;

  async function remove() {
    error = "";
    if (!confirming) {
      confirming = true;
      return;
    }
    busy = true;
    try {
      const res = await fetch("/api/repos", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      const data = await res.json();
      if (!res.ok) {
        error = data.error ?? "No se pudo quitar el repositorio";
        confirming = false;
        busy = false;
        return;
      }
      window.location.reload();
    } catch {
      error = "Error de conexión con el servidor";
      confirming = false;
      busy = false;
    }
  }

  function reset() {
    confirming = false;
    error = "";
  }
</script>

<div class="inline-flex items-center gap-2">
  <button
    type="button"
    class="border-none bg-none text-gh-subtle text-xs cursor-pointer py-0.5 pr-2.5 pl-1 rounded-md leading-none transition-colors hover:text-gh-danger hover:bg-[rgba(248,81,73,0.1)]"
    class:remove-btn-confirm={confirming}
    aria-label={confirming ? `Confirmar quitar ${name}` : `Quitar ${name}`}
    disabled={busy}
    onclick={remove}
    onmouseleave={reset}
  >
    {confirming ? "¿Quitar?" : "✕"}
  </button>
  {#if error}
    <span class="text-gh-danger text-xs" role="alert">{error}</span>
  {/if}
</div>

<style>
  .remove-btn-confirm {
    color: #0d1117 !important;
    background: #f85149 !important;
    font-size: 11px !important;
    font-weight: 600;
    padding: 4px 8px !important;
  }
  .remove-btn-confirm:hover {
    color: #0d1117 !important;
    background: #ff7b72 !important;
  }
</style>
