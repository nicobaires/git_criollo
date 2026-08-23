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
    parser.add_argument("--branch", "-b", default=None, help="Branch a analizar (default: activa)")
    parser.add_argument("--max-commits", type=int, default=5000, help="Máximo commits a analizar")
    parser.add_argument("--all", action="store_true", help="Genera stats para todos los repos de repos.json")
    return parser.parse_args()


def extract_all(git: GitService, since: datetime | None, until: datetime | None, max_commits: int, branch: str | None = None):
    """Extrae todas las métricas del repo en una sola pasada de git log --numstat."""

    repo = git.repo

    # ── Una sola pasada de git log --numstat ──
    # (mucho más rápido que commit.stats, que calcula el diff de cada commit)
    # El filtro de fechas se hace en git, ANTES del límite de commits.
    args = ["--numstat", "--pretty=format:%x1e%H%x09%ae%x09%an%x09%cI"]
    if since:
        args.append(f"--since={since.strftime('%Y-%m-%d %H:%M:%S')}")
    if until:
        args.append(f"--until={until.strftime('%Y-%m-%d %H:%M:%S')}")
    args.append(f"--max-count={max_commits}")
    if branch:
        args.append(branch)
    output = repo.git.log(*args)

    # ── KPIs básicos ──
    total_commits = 0
    emails = set()

    # ── LOC totales ──
    total_added = 0
    total_deleted = 0
    total_changes = 0

    # ── Commits por autor por mes (agrupado por email) ──
    commits_by_author_month = defaultdict(lambda: defaultdict(int))

    # ── LOC por mes ──
    loc_by_month = defaultdict(lambda: {"added": 0, "deleted": 0})

    # ── Archivos hot (cuántas veces aparece en commits) ──
    file_changes = Counter()

    # ── Archivos ignorados para hot_files (no entran en métricas de frecuencia) ──
    IGNORED_FILES = {
        ".gitignore", ".gitattributes", ".gitmodules",
        "pnpm-lock.yaml", "package-lock.json", "yarn.lock",
        "uv.lock", "poetry.lock", "Pipfile.lock",
        "composer.lock", "Gemfile.lock",
        "go.sum", "Cargo.lock",
    }
    IGNORED_PREFIXES = (".",)  # archivos que empiezan con .
    IGNORED_SUFFIXES = {
        ".json", ".lock", ".sum", ".map", ".min.js", ".min.css",
        ".svg", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2",
    }

    def is_ignored(path: str) -> bool:
        base = os.path.basename(path)
        if base in IGNORED_FILES:
            return True
        if base.startswith(".") and base not in {".env", ".env.example"}:
            return True
        for suffix in IGNORED_SUFFIXES:
            if base.endswith(suffix):
                return True
        return False

    # ── Heatmap (commits por día) ──
    heatmap = Counter()

    # ── Distribución de commits por autor (agrupado por email) ──
    author_commits = Counter()

    # ── Mapeo email → nombre más frecuente ──
    email_to_names: dict[str, Counter] = defaultdict(Counter)

    for record in output.split("\x1e"):
        if not record.strip():
            continue
        lines = record.splitlines()
        meta = lines[0].split("\t")
        if len(meta) < 4:
            continue
        _, email, author_name, iso_date = meta[0], meta[1], meta[2], meta[3]
        try:
            dt = datetime.fromisoformat(iso_date).replace(tzinfo=None)
        except ValueError:
            continue

        total_commits += 1
        emails.add(email)
        month_key = dt.strftime("%Y-%m")
        day_key = dt.strftime("%Y-%m-%d")

        # Trackear nombre más frecuente por email
        email_to_names[email][author_name] += 1

        # Commits por autor por mes (key=email)
        commits_by_author_month[email][month_key] += 1

        # Distribución (key=email)
        author_commits[email] += 1

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
            if not is_ignored(path):
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

    # ── Resolver nombre display para cada email ──
    def resolve_name(email: str) -> str:
        names = email_to_names[email]
        return names.most_common(1)[0][0] if names else email

    # Distribución para donut chart
    total_for_pct = sum(author_commits.values())
    distribution = [
        {"author": resolve_name(email), "commits": count, "percentage": round(count / total_for_pct * 100, 1)}
        for email, count in author_commits.most_common()
    ]

    # Commits por autor por mes → formato plano para Chart.js (key=nombre display)
    authors_series = {}
    for email, months in commits_by_author_month.items():
        authors_series[resolve_name(email)] = [months.get(m, 0) for m in all_months]

    return {
        "meta": {
            "repo_name": os.path.basename(os.path.abspath(repo.working_tree_dir)),
            "branch": branch or git.get_branches().active,
            "generated_at": datetime.now().isoformat(),
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else None,
            "total_commits_analyzed": total_commits,
        },
        "kpis": {
            "total_commits": total_commits,
            "total_authors": len(emails),
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


def _write_stats(data, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _sanitize_branch(branch: str) -> str:
    return branch.replace("/", "-").replace(" ", "-")


def _analyze_one(repo_path, since, until, max_commits, output_path, branch=None):
    print(f"🔍 Analizando repo: {os.path.abspath(repo_path)}")
    if branch:
        print(f"   Branch: {branch}")
    if since:
        print(f"   Desde: {args_since_str(since)}")
    if until:
        print(f"   Hasta: {args_since_str(until)}")

    git = GitService(repo_path)
    data = extract_all(git, since, until, max_commits, branch)

    _write_stats(data, output_path)

    print(f"✅ Stats generados: {output_path}")
    print(f"   Commits: {data['kpis']['total_commits']}")
    print(f"   Autores: {data['kpis']['total_authors']}")
    print(f"   Racha: {data['life_metrics']['current_streak_days']} días")


def args_since_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def main():
    args = parse_args()

    since = datetime.strptime(args.since, "%Y-%m-%d") if args.since else None
    until = datetime.strptime(args.until, "%Y-%m-%d") if args.until else None

    if args.all:
        config_path = Path(__file__).resolve().parent.parent / "repos.json"
        if not config_path.exists():
            sys.exit(f"❌ No existe {config_path}. Crealo con el formato del README (lista de repos).")
        config = json.loads(config_path.read_text(encoding="utf-8"))
        repos = config.get("repos", [])
        if not repos:
            sys.exit("❌ repos.json no tiene repos en la lista 'repos'.")
        stats_dir = Path(__file__).resolve().parent.parent / "src" / "data" / "stats"
        for repo in repos:
            branch = args.branch
            branch_dir = stats_dir / repo["name"]
            branch_dir.mkdir(parents=True, exist_ok=True)
            if branch:
                safe = _sanitize_branch(branch)
                _analyze_one(repo["path"], since, until, args.max_commits, branch_dir / f"{safe}.json", branch)
            else:
                git = GitService(repo["path"])
                active = git.get_branches().active
                safe = _sanitize_branch(active)
                _analyze_one(repo["path"], since, until, args.max_commits, branch_dir / f"{safe}.json", active)
        return

    repo_path = args.repo_path
    branch = args.branch
    if branch:
        stats_dir = Path(__file__).resolve().parent.parent / "src" / "data" / "stats"
        repo_name = os.path.basename(os.path.abspath(repo_path))
        branch_dir = stats_dir / repo_name
        branch_dir.mkdir(parents=True, exist_ok=True)
        safe = _sanitize_branch(branch)
        _analyze_one(repo_path, since, until, args.max_commits, branch_dir / f"{safe}.json", branch)
    else:
        _analyze_one(repo_path, since, until, args.max_commits, Path(args.output))


if __name__ == "__main__":
    main()