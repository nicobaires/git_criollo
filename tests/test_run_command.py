class TestRunCommand:
    def test_valid_command(self, gs):
        result = gs.run_command("log --oneline")
        assert len(result) > 0
        assert "commit" in result or "Error" not in result

    def test_injection_rejected(self, gs):
        result = gs.run_command("; rm -rf /")
        assert "caracteres no permitidos" in result

    def test_shell_metachars_rejected(self, gs):
        for cmd in ["`id`", "$(whoami)", "foo && bar", "foo | bar"]:
            result = gs.run_command(cmd)
            assert "caracteres no permitidos" in result, f"Fallo con: {cmd}"
