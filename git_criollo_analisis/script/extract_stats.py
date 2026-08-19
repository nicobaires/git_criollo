#!/usr/bin/env python3
"""
extract_stats.py - Genera JSON de analytics para GitCriollo Dashboard

Uso:
    python extract_stats.py /ruta/al/repo
    python extract_stats.py /ruta/al/repo --output ./data/stats.json
    python extract_stats.py /ruta/al/repo --since 2024-01-01 --until 2024-12-31

Reutiliza GitService de git_criollo.git_service
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

try:
    from git_criollo.git_service import GitService
except ImportError:
    # Si git_criollo no está instalado, buscar la raíz del repo
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(REPO_ROOT))
    from git_criollo.git_service import GitService


def parse_args():
    parser = argparse.ArgumentParser(description="Extrae métricas de Git para el dashboard")
    parser.add_argument("repo_path", nargs="?", default=".", help="Ruta al repositorio Git")
    parser.add_argument("--output", "-o", default="./data/stats.json", help="Ruta de salida del JSON")
    parser.add_argument("--since", help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--until", help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--max-commits", type=int, default=5000, help="Máximo commits a analizar")
    return parser.parse_args()


def extract_all(git: GitService, since: datetime | None, until: datetime | None, max_commits: int):
    """Extrae todas las métricas del repo en una sola pasada de git log --numstat."""

    repo = git.repo

    # ── Una sola pasada de git log --numstat ──
    # (mucho más rápido que commit.stats, que calcula el diff de cada commit)
    # El filtro de fechas se hace en git, ANTES del límite de commits.
    args = ["--numstat", "--pretty=format:%x1e%H%x09%an%x09%cI"]
    if since:
        args.append(f"--since={since.strftime('%Y-%m-%d %H:%M:%S')}")
    if until:
        args.append(f"--until={until.strftime('%Y-%m-%d %H:%M:%S')}")
    args.append(f"--max-count={max_commits}")
    output = repo.git.log(*args)

    # ── KPIs básicos ──
    total_commits = 0
    authors = set()

    # ── LOC totales ──
    total_added = 0
    total_deleted = 0
    total_changes = 0

    # ── Commits por autor por mes ──
    # { "Nico": { "2024-01": 15, "2024-02": 23 } }
    commits_by_author_month = defaultdict(lambda: defaultdict(int))

    # ── LOC por mes ──
    # { "2024-01": { "added": 12456, "deleted": 8934 } }
    loc_by_month = defaultdict(lambda: {"added": 0, "deleted": 0})

    # ── Archivos hot (cuántas veces aparece en commits) ──
    file_changes = Counter()

    # ── Heatmap (commits por día) ──
    heatmap = Counter()

    # ── Distribución de commits por autor ──
    author_commits = Counter()

    for record in output.split("\x1e"):
        if not record.strip():
            continue
        lines = record.splitlines()
        meta = lines[0].split("\t")
        if len(meta) < 3:
            continue
        _, author, iso_date = meta[0], meta[1], meta[2]
        try:
            dt = datetime.fromisoformat(iso_date).replace(tzinfo=None)
        except ValueError:
            continue

        total_commits += 1
        authors.add(author)
        month_key = dt.strftime("%Y-%m")
        day_key = dt.strftime("%Y-%m-%d")

        # Commits por autor por mes
        commits_by_author_month[author][month_key] += 1

        # Distribución
        author_commits[author] += 1

        # Heatmap / métricas de vida
        heatmap[day_key] += 1

        # LOC por archivo (líneas numstat de este commit)
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            added_s, deleted_s, path = parts[0], parts[1], "\t".join(parts[2:])
            try:
                added = int(added_s)
                deleted = int(deleted_s)
            except ValueError:
                continue  # '-' = cambio binario, se cuenta como 0
            loc_by_month[month_key]["added"] += added
            loc_by_month[month_key]["deleted"] += deleted
            total_added += added
            total_deleted += deleted
            total_changes += added + deleted
            file_changes[path] += 1

    # ── Métricas de "vida" ──
    active_days = set(heatmap.keys())

    # ── Calcular racha actual ──
    streak = _calculate_streak(active_days)

    # ── Mayor día ──
    if heatmap:
        top_day, top_count = heatmap.most_common(1)[0]
    else:
        top_day, top_count = None, 0

    # ── Frecuencia promedio ──
    if active_days:
        first_day = min(active_days)
        last_day = max(active_days)
        days_span = (datetime.strptime(last_day, "%Y-%m-%d") - datetime.strptime(first_day, "%Y-%m-%d")).days + 1
        freq = round(total_commits / days_span, 1) if days_span > 0 else 0
    else:
        days_span = 0
        freq = 0

    # ── Formatear salida ──
    # Ordenar meses para las series temporales
    all_months = sorted(loc_by_month.keys())

    # Top 10 archivos hot
    hot_files = [
        {"path": path, "changes": count}
        for path, count in file_changes.most_common(10)
    ]

    # Heatmap como lista de objetos para el frontend
    heatmap_list = [
        {"date": day, "count": count}
        for day, count in sorted(heatmap.items())
    ]

    # Distribución para donut chart
    total_for_pct = sum(author_commits.values())
    distribution = [
        {"author": author, "commits": count, "percentage": round(count / total_for_pct * 100, 1)}
        for author, count in author_commits.most_common()
    ]

    # Commits por autor por mes → formato plano para Chart.js
    authors_series = {}
    for author, months in commits_by_author_month.items():
        authors_series[author] = [months.get(m, 0) for m in all_months]

    return {
        "meta": {
            "repo_name": os.path.basename(os.path.abspath(repo.working_tree_dir)),
            "branch": git.get_branches().active,
            "generated_at": datetime.now().isoformat(),
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else None,
            "total_commits_analyzed": total_commits,
        },
        "kpis": {
            "total_commits": total_commits,
            "total_authors": len(authors),
            "total_added": total_added,
            "total_deleted": total_deleted,
            "total_changes": total_changes,
        },
        "life_metrics": {
            "active_days": len(active_days),
            "total_days": days_span,
            "active_days_percentage": round(len(active_days) / days_span * 100, 1) if days_span else 0,
            "average_commits_per_day": freq,
            "top_day": {"date": top_day, "commits": top_count} if top_day else None,
            "current_streak_days": streak,
        },
        "timeline": {
            "months": all_months,
            "commits_by_author": authors_series,
            "loc_by_month": {
                "months": all_months,
                "added": [loc_by_month[m]["added"] for m in all_months],
                "deleted": [loc_by_month[m]["deleted"] for m in all_months],
            },
        },
        "hot_files": hot_files,
        "heatmap": heatmap_list,
        "distribution": distribution,
    }


def _calculate_streak(active_days: set[str]) -> int:
    """Calcula la racha actual de días con commits."""
    if not active_days:
        return 0

    sorted_days = sorted(active_days, reverse=True)
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # La racha solo cuenta si hoy o ayer hubo actividad
    if today not in active_days and yesterday not in active_days:
        return 0

    streak = 1
    current = datetime.strptime(sorted_days[0], "%Y-%m-%d")

    for day_str in sorted_days[1:]:
        day = datetime.strptime(day_str, "%Y-%m-%d")
        if (current - day).days == 1:
            streak += 1
            current = day
        else:
            break

    return streak


def main():
    args = parse_args()

    since = datetime.strptime(args.since, "%Y-%m-%d") if args.since else None
    until = datetime.strptime(args.until, "%Y-%m-%d") if args.until else None

    print(f"🔍 Analizando repo: {os.path.abspath(args.repo_path)}")
    if since:
        print(f"   Desde: {args.since}")
    if until:
        print(f"   Hasta: {args.until}")

    git = GitService(args.repo_path)
    data = extract_all(git, since, until, args.max_commits)

    # Asegurar que el directorio de salida existe
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Stats generados: {output_path}")
    print(f"   Commits: {data['kpis']['total_commits']}")
    print(f"   Autores: {data['kpis']['total_authors']}")
    print(f"   Racha: {data['life_metrics']['current_streak_days']} días")


if __name__ == "__main__":
    main()