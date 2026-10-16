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

    def test_resolve_conflict_ours(self, gs):
        conflict_content = (
            "linea 0\n"
            "<<<<<<< HEAD\n"
            "nuestro cambio\n"
            "=======\n"
            "cambio de ellos\n"
            ">>>>>>> feature\n"
            "linea final\n"
        )
        with open("conflict_file.txt", "w") as f:
            f.write(conflict_content)

        regions = gs.get_conflict_regions("conflict_file.txt")
        assert len(regions) == 1
        assert regions[0].ours == "nuestro cambio"
        assert regions[0].theirs == "cambio de ellos"

        gs.resolve_conflict_region("conflict_file.txt", regions[0], "ours")
        with open("conflict_file.txt") as f:
            result = f.read()

        assert "<<<<<<<" not in result
        assert "nuestro cambio" in result
        assert "cambio de ellos" not in result
        assert result.startswith("linea 0\n")
        assert result.endswith("linea final\n")

    def test_resolve_conflict_theirs(self, gs):
        conflict_content = (
            "<<<<<<< HEAD\n"
            "nuestro cambio\n"
            "=======\n"
            "cambio de ellos\n"
            ">>>>>>> feature\n"
        )
        with open("conflict_theirs.txt", "w") as f:
            f.write(conflict_content)

        regions = gs.get_conflict_regions("conflict_theirs.txt")
        assert len(regions) == 1

        gs.resolve_conflict_region("conflict_theirs.txt", regions[0], "theirs")
        with open("conflict_theirs.txt") as f:
            result = f.read()

        assert "cambio de ellos\n" == result

    def test_resolve_conflict_both(self, gs):
        conflict_content = (
            "<<<<<<< HEAD\n"
            "linea 1\n"
            "=======\n"
            "linea 2\n"
            ">>>>>>> feature\n"
        )
        with open("conflict_both.txt", "w") as f:
            f.write(conflict_content)

        regions = gs.get_conflict_regions("conflict_both.txt")
        assert len(regions) == 1

        gs.resolve_conflict_region("conflict_both.txt", regions[0], "both")
        with open("conflict_both.txt") as f:
            result = f.read()

        assert "linea 1\nlinea 2\n" == result
