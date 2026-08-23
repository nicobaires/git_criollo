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

El dashboard lee `src/data/stats/<repo>/<branch>.json`, generado por el extractor que reutiliza `GitService` del proyecto principal.

### Agregar repositorios desde la app (modo recomendado)

Con el servidor corriendo (`pnpm dev` o el build con Node), usá el botón **+ Agregar repo** del header y pegá la ruta de la carpeta. La app:

1. valida que la carpeta exista y sea un repositorio Git (toma la raíz real del repo);
2. la agrega a `repos.json` (lo crea si no existe) con un nombre derivado de la carpeta, sin duplicados;
3. genera sus stats automáticamente con el extractor (primer branch disponible).

El dashboard se sirve con Node (adaptador `@astrojs/node`, `output: 'server'`), así las páginas y los datos se leen por request: un repo recién agregado aparece sin reiniciar nada.

Para **quitar** un repo, pasá el mouse sobre su pill y usá el ✕: confirma y lo saca de `repos.json` (borrando también sus stats generados).

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

> `name` se usa para la URL del dashboard (`/repo/<name>`) y como nombre del directorio de stats: usar solo `a-z`, `0-9`, `-` y `_`.

Y generá los stats de todos:

```bash
python script/extract_stats.py --all
```

Esto escribe `src/data/stats/<name>/<branch>.json` por cada repo y branch.

### Un solo repositorio

```bash
python script/extract_stats.py /ruta/al/repo -o src/data/stats/mi-repo/main.json
```

### Un branch específico

```bash
python script/extract_stats.py /ruta/al/repo -o src/data/stats/mi-repo/feat-feature.json --branch feat/feature
```

Opciones del extractor:

| Flag | Descripción |
|------|-------------|
| `-o, --output` | Ruta de salida del JSON (default: `./data/stats.json`) |
| `--branch` | Branch a analizar (default: branch actual) |
| `--since` | Fecha inicio (YYYY-MM-DD) |
| `--until` | Fecha fin (YYYY-MM-DD) |
| `--max-commits` | Máximo de commits a analizar (default: 5000) |
| `--all` | Genera stats para todos los repos y branches de `repos.json` |

> `src/data/stats/` está en `.gitignore`: es un artefacto generado, no se versiona.

## Uso

```bash
pnpm dev       # servidor de desarrollo
pnpm build     # build de producción (cliente + servidor Node)
pnpm preview   # servir el build con el adaptador de Node
```

## API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/branches?repo=<name>` | Lista branches del repo con estado de stats |
| `POST` | `/api/branches` | Extrae stats para un branch específico (`{ repo, branch }`) |
| `POST` | `/api/repos` | Agrega un repo (`{ path }`) y genera stats del primer branch |
| `DELETE` | `/api/repos` | Quita un repo (`{ name }`) y borra sus stats |

## Funcionalidades

- **Multi-repositorio**: selector de repos en el header, navegación por `/repo/<name>`
- **Multi-branch**: dropdown de branches cargado desde git, selector de branch en la URL
- **Filtro por año**: heatmap y KPIs filtrables por año (visible cuando hay más de 1 año)
- **Heatmap calendario**: grilla estilo GitHub, Ene-Dic, 53 semanas × 7 días, un heatmap por año
- **Granularidad adaptiva**: ≤30 días → diario, ≤180 días → semanal, >180 días → mensual
- **Charts**: commits por autor (líneas), distribución (doughnut), LOC (barras), archivos más tocados
- **Gestión desde UI**: agregar/quitar repos sin tocar archivos manualmente

## Estructura

```
git_criollo_analisis/
├── astro.config.mjs          # config Astro (Svelte + Tailwind v4 + adaptador Node)
├── package.json
├── repos.example.json         # ejemplo de config de repositorios (copiar a repos.json)
├── script/
│   └── extract_stats.py       # extractor de métricas (KPIs, timeline, heatmap, etc.)
└── src/
    ├── components/
    │   ├── Dashboard.astro    # dashboard principal + selector de repos
    │   ├── AddRepo.svelte     # alta de repos (POST /api/repos)
    │   ├── RemoveRepo.svelte  # baja de repos (DELETE /api/repos)
    │   ├── BranchSelector.svelte  # dropdown de branches
    │   ├── YearSelector.svelte    # filtro por año
    │   ├── KpiCard.svelte     # tarjeta KPI reutilizable
    │   ├── Chart.svelte       # wrapper genérico de Chart.js
    │   └── Heatmap.svelte     # grid de actividad estilo GitHub
    ├── data/
    │   └── stats/             # stats por repo/branch (no versionado)
    ├── lib/
    │   ├── api-common.ts      # funciones compartidas para API (config, git, extractor)
    │   ├── dashboard.ts       # lógica de granularidad, timeline, KPIs filtrados
    │   ├── paths.ts           # resuelve la raíz del proyecto en runtime
    │   ├── repos.ts           # carga repos.json
    │   └── stats.ts           # carga stats + tipos del esquema
    ├── styles/
    │   └── global.css         # Tailwind v4 + tema personalizado (gh-*, heat-*)
    └── pages/
        ├── index.astro        # dashboard del primer repo
        ├── api/
        │   ├── repos.ts       # POST/DELETE /api/repos
        │   └── branches.ts    # GET/POST /api/branches
        └── repo/
            └── [repo].astro   # página por repo (/repo/<name>)
```

## Tests

```bash
python -m pytest tests/ -q
```

Tests organizados por dominio:

| Archivo | Cobertura |
|---------|-----------|
| `test_branches.py` | Crear, eliminar, checkout, merge, detached HEAD |
| `test_commits.py` | Log, commits, detalle de commit |
| `test_changes.py` | Status, diff, stage/unstage, commit, amend, hunks |
| `test_sync.py` | Pull, push, fetch (sin remote) |
| `test_conflicts.py` | Regiones de conflicto, resolución |
| `test_rebase.py` | Commits para rebase, parent SHA, ejecutar rebase |
| `test_gitignore.py` | Leer, agregar, duplicados |
| `test_run_command.py` | Comandos válidos, inyección, metacaracteres |
| `test_stash_tags.py` | Stash push/pop/list, tags, cherry-pick |
| `test_extract_stats.py` | Streaks, extracción completa |
| `test_diff_utils.py` | Coloreado de diff |
| `test_error_utils.py` | Manejo de errores Git |

## Esquema de `stats.json`

Contrato entre el extractor (`script/extract_stats.py`) y el dashboard:

```json
{
  "meta": {
    "repo_name": "git_criollo",
    "branch": "main",
    "generated_at": "2026-08-15T12:00:00",
    "since": "2024-01-01",
    "until": "2024-12-31",
    "total_commits_analyzed": 1500,
    "repo_age_days": 450,
    "years": ["2024", "2025", "2026"]
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
    "months": ["2024-01", "2024-02"],
    "weeks": ["2024-W01", "2024-W02"],
    "days": ["2024-01-01", "2024-01-02"],
    "commits_by_author": { "Nico": [10, 22] },
    "commits_by_author_week": { "Nico": [45, 38] },
    "commits_by_author_day": { "Nico": [3, 5, 2] },
    "loc_by_month": { "months": ["2024-01"], "added": [5000], "deleted": [1200] },
    "loc_by_week": { "weeks": ["2024-W01"], "added": [1200], "deleted": [300] },
    "loc_by_day": { "days": ["2024-01-01"], "added": [200], "deleted": [50] }
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
| `meta` | `repo_age_days` | Días desde el primer commit |
| `meta` | `years` | Años con actividad (para el year selector) |
| `kpis` | `total_*` | Totales de commits, autores, líneas añadidas/eliminadas y cambios |
| `life_metrics` | `active_days` | Días con al menos un commit |
| `life_metrics` | `current_streak_days` | Racha actual (solo cuenta si hubo actividad hoy o ayer) |
| `timeline` | `months/weeks/days` | Keys temporales en3 granularidades |
| `timeline` | `commits_by_author*` | Serie de commits por autor, por mes/semana/día |
| `timeline` | `loc_by_*` | Líneas añadidas/eliminadas por mes/semana/día |
| `hot_files` | — | Top 10 archivos con más cambios (sin lockfiles, JSON, assets) |
| `heatmap` | — | Commits por día (para heatmap estilo GitHub) |
| `distribution` | — | Distribución de commits por autor con porcentaje |
