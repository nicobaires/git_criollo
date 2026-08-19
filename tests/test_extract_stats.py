import importlib.util
from datetime import datetime, timedelta
from pathlib import Path

from git_criollo.git_service import GitService

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "git_criollo_analisis"
    / "script"
    / "extract_stats.py"
)


def _load_extractor():
    spec = importlib.util.spec_from_file_location("extract_stats", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extract_stats = _load_extractor()


class TestCalculateStreak:
    def test_empty(self):
        assert extract_stats._calculate_streak(set()) == 0

    def test_no_recent_activity(self):
        days = {"2026-01-01", "2026-01-02"}
        assert extract_stats._calculate_streak(days) == 0

    def test_consecutive_ending_today(self):
        today = datetime.now()
        days = {(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)}
        assert extract_stats._calculate_streak(days) == 5

    def test_consecutive_ending_yesterday(self):
        today = datetime.now()
        days = {(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)}
        assert extract_stats._calculate_streak(days) == 3

    def test_gap_breaks_streak(self):
        today = datetime.now()
        days = {
            today.strftime("%Y-%m-%d"),
            (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            (today - timedelta(days=3)).strftime("%Y-%m-%d"),
        }
        assert extract_stats._calculate_streak(days) == 2


class TestExtractAll:
    def test_full_extraction(self, repo_with_branches):
        git = GitService(repo_with_branches)
        data = extract_stats.extract_all(git, None, None, 100)

        assert data["kpis"]["total_commits"] == 5
        assert data["kpis"]["total_authors"] == 1
        assert data["kpis"]["total_added"] > 0
        assert data["kpis"]["total_changes"] == (
            data["kpis"]["total_added"] + data["kpis"]["total_deleted"]
        )

        assert data["life_metrics"]["active_days"] == 1
        assert data["life_metrics"]["current_streak_days"] >= 1

        assert data["timeline"]["months"]
        assert len(data["timeline"]["commits_by_author"]["Test"]) == len(
            data["timeline"]["months"]
        )
        assert len(data["timeline"]["loc_by_month"]["added"]) == len(
            data["timeline"]["months"]
        )

        assert len(data["hot_files"]) == 5
        assert len(data["heatmap"]) == 1
        assert data["distribution"][0]["percentage"] == 100.0
        assert data["meta"]["total_commits_analyzed"] == 5
        assert data["meta"]["branch"] == "main"

    def test_since_filter_excludes_all(self, repo_with_commits):
        git = GitService(repo_with_commits)
        since = datetime.now() + timedelta(days=1)
        data = extract_stats.extract_all(git, since, None, 100)

        assert data["kpis"]["total_commits"] == 0
        assert data["timeline"]["months"] == []
        assert data["heatmap"] == []
        assert data["distribution"] == []
        assert data["life_metrics"]["current_streak_days"] == 0