import os
import subprocess


class TestStash:
    def test_stash_push_and_pop(self, gs):
        with open("stash_test.txt", "w") as f:
            f.write("stash content")
        gs.stage_file("stash_test.txt")
        gs.stash_push("test stash")
        assert "stash_test.txt" not in [item.a_path for item in gs.repo.index.diff(None)]
        gs.stash_pop()
        assert os.path.exists(os.path.join(gs.repo.working_tree_dir, "stash_test.txt"))

    def test_stash_list(self, gs):
        with open("stash_list.txt", "w") as f:
            f.write("test")
        gs.stage_file("stash_list.txt")
        gs.stash_push()
        stashes = gs.stash_list()
        assert len(stashes) > 0


class TestTags:
    def test_create_and_delete(self, gs):
        gs.create_tag("test-tag")
        assert "test-tag" in [t.name for t in gs.repo.tags]
        gs.delete_tag("test-tag")
        assert "test-tag" not in [t.name for t in gs.repo.tags]

    def test_get_tags(self, gs):
        tags = gs.get_tags()
        assert "v1.0" in tags


class TestCherryPick:
    def test_cherry_pick(self, gs):
        gs.create_branch("cherry-source")
        gs.checkout("cherry-source")
        with open("cherry_unique.txt", "w") as f:
            f.write("solo en source")
        subprocess.run(["git", "add", "cherry_unique.txt"], capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "cherry pick me"], capture_output=True
        )
        sha = gs.repo.head.commit.hexsha[:7]
        gs.checkout("main")
        gs.cherry_pick(sha)
        ruta = os.path.join(gs.repo.working_tree_dir, "cherry_unique.txt")
        assert os.path.exists(ruta)
        with open(ruta) as f:
            assert f.read() == "solo en source"
