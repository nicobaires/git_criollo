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

El dashboard lee `src/data/stats/<repo>.json`, generado por el extractor que reutiliza `GitService` del proyecto principal.

### Agregar repositorios desde la app (modo recomendado)

Con el servidor corriendo (`pnpm dev` o el build con Node), usá el botón **+ Agregar repo** del header y pegá la ruta de la carpeta. La app:

1. valida que la carpeta exista y sea un repositorio Git (toma la raíz real del repo);
2. la agrega a `repos.json` (lo crea si no existe) con un nombre derivado de la carpeta, sin duplicados;
3. genera sus stats automáticamente con el extractor.

El dashboard se sirve con Node (adaptador `@astrojs/node`, `output: 'server'`), así las páginas y los datos se leen por request: un repo recién agregado aparece sin reiniciar nada.

### Varios repositorios (manual)

Configurá los repos a analizar en `repos.json` (copiá `repos.example.json`; está en `.gitignore` porque contiene rutas locales):

```json
{
  "repos": [
    { "name": "git_criollo", "path": "/ruta/al/repo/git_criollo" },
    { "name": "otro-proyecto", "path": "/ruta/al/repo/otro-proyecto" }
  ]
}
```

> `name` se usa para la URL del dashboard (`/repo/<name>`) y como nombre del archivo de stats: usar solo `a-z`, `0-9`, `-` y `_`.

Y generá los stats de todos:

```bash
python script/extract_stats.py --all
```

Esto escribe `src/data/stats/<name>.json` por cada repo.

### Un solo repositorio

```bash
python script/extract_stats.py /ruta/al/repo -o src/data/stats/mi-repo.json
```

Opciones del extractor:

| Flag | Descripción |
|------|-------------|
| `-o, --output` | Ruta de salida del JSON (default: `./data/stats.json`) |
| `--since` | Fecha inicio (YYYY-MM-DD) |
| `--until` | Fecha fin (YYYY-MM-DD) |
| `--max-commits` | Máximo de commits a analizar (default: 5000) |
| `--all` | Genera stats para todos los repos de `repos.json` |

> `src/data/stats/` está en `.gitignore`: es un artefacto generado, no se versiona.

## Uso

```bash
pnpm dev       # servidor de desarrollo
pnpm build     # build de producción (cliente + servidor Node)
pnpm preview   # servir el build con el adaptador de Node
```

## Estructura

```
git_criollo_analisis/
├── astro.config.mjs        # config Astro (Svelte + adaptador Node, output server)
├── package.json
├── repos.example.json      # ejemplo de config de repositorios (copiar a repos.json)
├── script/
│   └── extract_stats.py    # extractor de métricas (KPIs, timeline, heatmap, etc.)
└── src/
    ├── components/
    │   ├── Dashboard.astro # dashboard completo + selector de repositorios
    │   ├── AddRepo.svelte  # alta de repos desde la app (POST /api/repos)
    │   ├── KpiCard.svelte  # tarjeta KPI reutilizable
    │   ├── Chart.svelte    # wrapper genérico de chart.js (hidrata con client:load)
    │   └── Heatmap.svelte  # grid de actividad estilo GitHub (SSR, sin JS)
    ├── data/
    │   └── stats/          # stats por repo: <name>.json (no versionado)
    ├── lib/
    │   ├── paths.ts        # resuelve la raíz del proyecto en runtime
    │   ├── repos.ts        # carga repos.json (config de repositorios)
    │   └── stats.ts        # carga src/data/stats/*.json + tipos del esquema
    └── pages/
        ├── index.astro     # dashboard del primer repo de repos.json
        ├── api/
        │   └── repos.ts    # POST /api/repos: valida, agrega y genera stats
        └── repo/
            └── [repo].astro # página por repo (/repo/<name>), por request
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