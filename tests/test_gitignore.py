import os


class TestGitignore:
    def test_get_content_missing(self, gs):
        content = gs.get_gitignore_content()
        assert "no existe" in content

    def test_get_content_exists(self, gs):
        gitignore = os.path.join(gs.repo.working_tree_dir, ".gitignore")
        with open(gitignore, "w") as f:
            f.write("*.log\n.env\n")
        content = gs.get_gitignore_content()
        assert "*.log" in content

    def test_add_to_gitignore(self, gs):
        gs.add_to_gitignore("*.tmp")
        gitignore = os.path.join(gs.repo.working_tree_dir, ".gitignore")
        with open(gitignore) as f:
            content = f.read()
        assert "*.tmp" in content

    def test_add_duplicate(self, gs):
        gs.add_to_gitignore("*.dup")
        gs.add_to_gitignore("*.dup")
        gitignore = os.path.join(gs.repo.working_tree_dir, ".gitignore")
        with open(gitignore) as f:
            lines = f.read().strip().split("\n")
        assert lines.count("*.dup") == 1
