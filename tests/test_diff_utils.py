from git_criollo.diff_utils import _diff_coloreado


class TestDiffColoreado:
    def test_empty_diff(self):
        assert _diff_coloreado("") == ""

    def test_simple_line(self):
        result = _diff_coloreado("hola mundo")
        assert "hola mundo" in result

    def test_added_line(self):
        result = _diff_coloreado("+nueva linea")
        assert "nueva linea" in result
        assert "#00ff00" in result

    def test_removed_line(self):
        result = _diff_coloreado("-linea borrada")
        assert "linea borrada" in result
        assert "#ff5f5f" in result

    def test_hunk_header(self):
        result = _diff_coloreado("@@ -1,3 +1,4 @@")
        assert "#00afff" in result

    def test_diff_header(self):
        result = _diff_coloreado("diff --git a/f.py b/f.py")
        assert "#888888" in result

    def test_word_diff_added(self):
        result = _diff_coloreado('{+palabra+}')
        assert "palabra" in result
        assert "#00ff00 on #003300" in result

    def test_word_diff_deleted(self):
        result = _diff_coloreado('[-palabra-]')
        assert "palabra" in result
        assert "#ff5f5f on #330000" in result

    def test_rich_escape_brackets(self):
        diff = "texto con [corchetes] y {llaves}"
        result = _diff_coloreado(diff)
        assert "[corchetes]" in result or "corchetes" in result
        assert "{llaves}" in result or "llaves" in result

    def test_mixed_content(self):
        raw = 'diff --git a/f.txt b/f.txt\n@@ -1 +1 @@\n-base\n{+nueva+}'
        result = _diff_coloreado(raw)
        assert "#888888" in result
        assert "#00afff" in result
        assert "#ff5f5f" in result
        assert "#00ff00 on #003300" in result
