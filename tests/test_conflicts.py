import pytest

from git_criollo.models import ConflictRegion


class TestConflictResolution:
    def test_get_conflict_regions(self, gs):
        regions = gs.get_conflict_regions("nonexistent.txt")
        assert regions == []

    def test_resolve_conflict_invalid_choice(self, gs):
        region = ConflictRegion(start=0, end=2, ours="a", theirs="b")
        with pytest.raises(ValueError, match="Opción de resolución inválida"):
            gs.resolve_conflict_region("f0.txt", region, "invalida")

    def test_is_merge_in_progress(self, gs):
        assert gs.is_merge_in_progress() is False
