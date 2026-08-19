# GitCriollo Analytics

Dashboard de analítica para repositorios Git construido con [Astro](https://astro.build/) y [Svelte](https://svelte.dev/). Tema oscuro estilo GitHub.

## Requisitos

- [pnpm](https://pnpm.io/) para las dependencias frontend
- Python 3 con las dependencias de `git_criollo` (GitPython, Textual) para el extractor

## Instalación

```bash
pnpm install
```

## Generar los datos

El dashboard lee `src/data/stats.json`, generado por el extractor que reutiliza `GitService` del proyecto principal:

```bash
python script/extract_stats.py /ruta/al/repo -o src/data/stats.json
```

Opciones del extractor:

| Flag | Descripción |
|------|-------------|
| `-o, --output` | Ruta de salida del JSON (default: `./data/stats.json`) |
| `--since` | Fecha inicio (YYYY-MM-DD) |
| `--until` | Fecha fin (YYYY-MM-DD) |
| `--max-commits` | Máximo de commits a analizar (default: 5000) |

> `src/data/stats.json` está en `.gitignore`: es un artefacto generado, no se versiona.

## Uso

```bash
pnpm dev       # servidor de desarrollo
pnpm build     # build estático a dist/
pnpm preview   # servir el build
```

## Estructura

```
git_criollo_analisis/
├── astro.config.mjs        # config Astro (integración Svelte)
├── package.json
├── script/
│   └── extract_stats.py    # extractor de métricas (KPIs, timeline, heatmap, etc.)
└── src/
    ├── components/
    │   └── KpiCard.svelte  # tarjeta KPI reutilizable
    ├── data/
    │   └── stats.json      # datos generados (no versionado)
    └── pages/
        └── index.astro     # dashboard principal
```

## Esquema de `stats.json`

Contrato entre el extractor (`script/extract_stats.py`) y el dashboard. Los scripts de extracción generan siempre la misma estructura:

```json
{
  "meta": {
    "repo_name": "git_criollo",
    "branch": "main",
    "generated_at": "2026-08-15T12:00:00",
    "since": "2024-01-01",
    "until": "2024-12-31",
    "total_commits_analyzed": 1500
  },
  "kpis": {
    "total_commits": 1500,
    "total_authors": 2,
    "total_added": 125000,
    "total_deleted": 32000,
    "total_changes": 157000
  },
  "life_metrics": {
    "active_days": 45,
    "total_days": 210,
    "active_days_percentage": 21.4,
    "average_commits_per_day": 7.1,
    "top_day": { "date": "2026-03-15", "commits": 28 },
    "current_streak_days": 3
  },
  "timeline": {
    "months": ["2024-01", "2024-02", "2024-03"],
    "commits_by_author": {
      "Nico": [10, 22, 31],
      "Otro": [2, 5, 8]
    },
    "loc_by_month": {
      "months": ["2024-01", "2024-02", "2024-03"],
      "added": [5000, 7200, 4100],
      "deleted": [1200, 2400, 3000]
    }
  },
  "hot_files": [
    { "path": "git_criollo/git_service.py", "changes": 120 }
  ],
  "heatmap": [
    { "date": "2024-01-15", "count": 3 }
  ],
  "distribution": [
    { "author": "Nico", "commits": 900, "percentage": 60.0 }
  ]
}
```

### Descripción de campos

| Sección | Campo | Descripción |
|---------|-------|-------------|
| `meta` | — | Metadatos del análisis (repo, rama, rango de fechas, commits analizados) |
| `kpis` | `total_*` | Totales de commits, autores, líneas añadidas/eliminadas y cambios |
| `life_metrics` | `active_days` | Días con al menos un commit |
| `life_metrics` | `total_days` | Días entre el primer y último commit |
| `life_metrics` | `average_commits_per_day` | `total_commits / total_days` |
| `life_metrics` | `top_day` | Día con más commits |
| `life_metrics` | `current_streak_days` | Racha actual (solo cuenta si hubo actividad hoy o ayer) |
| `timeline` | `months` | Meses ordenados (formato `YYYY-MM`), base de todos los arrays temporales |
| `timeline` | `commits_by_author` | Serie de commits por autor, alineada con `months` |
| `timeline` | `loc_by_month` | Líneas añadidas/eliminadas por mes, alineadas con `months` |
| `hot_files` | — | Top 10 archivos con más cambios |
| `heatmap` | — | Commits por día (para heatmap estilo GitHub) |
| `distribution` | — | Distribución de commits por autor con porcentaje |