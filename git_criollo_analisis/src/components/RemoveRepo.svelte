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

<div class="remove-repo">
  <button
    type="button"
    class="remove-btn"
    class:remove-btn-confirm={confirming}
    aria-label={confirming ? `Confirmar quitar ${name}` : `Quitar ${name}`}
    disabled={busy}
    onclick={remove}
    onmouseleave={reset}
  >
    {confirming ? "¿Quitar?" : "✕"}
  </button>
  {#if error}
    <span class="remove-error" role="alert">{error}</span>
  {/if}
</div>

<style>
  .remove-repo {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .remove-btn {
    border: none;
    background: none;
    color: #7d8590;
    font-size: 12px;
    cursor: pointer;
    padding: 2px 10px 2px 4px;
    border-radius: 6px;
    line-height: 1;
    transition: color 0.15s, background 0.15s;
  }
  .remove-btn:hover {
    color: #f85149;
    background: rgba(248, 81, 73, 0.1);
  }
  .remove-btn-confirm {
    color: #0d1117;
    background: #f85149;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 8px;
  }
  .remove-btn-confirm:hover {
    color: #0d1117;
    background: #ff7b72;
  }
  .remove-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }
  .remove-error {
    color: #f85149;
    font-size: 12px;
  }
</style>