<script>
  let { title, value, subtitle = "", icon = "📊", color = "#58a6ff" } = $props();
</script>

<div class="bg-gh-card rounded-xl p-5 flex flex-col gap-2 transition-transform hover:-translate-y-0.5 border-l-4" style="border-left-color: {color}">
  <div class="flex items-center gap-4">
    <span class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl" style="background: {color}20; color: {color}">{icon}</span>
    <div class="flex flex-col">
      <span class="text-[28px] font-bold text-gh-text leading-none">{value.toLocaleString()}</span>
      <span class="text-[13px] text-gh-muted mt-1">{title}</span>
    </div>
  </div>
  {#if subtitle}
    <span class="text-xs text-gh-success">{subtitle}</span>
  {/if}
</div>
