<script>
  let { title, value, subtitle = "", icon = "📊", color = "#58a6ff" } = $props();
</script>

<div class="kpi-card" style="border-left: 4px solid {color}">
  <div class="kpi-header">
    <span class="kpi-icon" style="background: {color}20; color: {color}">{icon}</span>
    <div class="kpi-info">
      <span class="kpi-value">{value.toLocaleString()}</span>
      <span class="kpi-title">{title}</span>
    </div>
  </div>
  {#if subtitle}
    <span class="kpi-subtitle">{subtitle}</span>
  {/if}
</div>

<style>
  .kpi-card {
    background: #161b22;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: transform 0.2s;
  }
  .kpi-card:hover {
    transform: translateY(-2px);
  }
  .kpi-header {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .kpi-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
  }
  .kpi-info {
    display: flex;
    flex-direction: column;
  }
  .kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #c9d1d9;
    line-height: 1;
  }
  .kpi-title {
    font-size: 13px;
    color: #8b949e;
    margin-top: 4px;
  }
  .kpi-subtitle {
    font-size: 12px;
    color: #3fb950;
  }
</style>