from git_criollo.diff_utils import _diff_coloreado


class TestDiffColoreado:
    def test_empty_diff(self):
        assert len(_diff_coloreado("")) == 0

    def test_simple_line(self):
        result = _diff_coloreado("hola mundo")
        assert "hola mundo" in result.plain

    def test_added_line(self):
        result = _diff_coloreado("+nueva linea")
        assert "nueva linea" in result.plain
        assert any(span.style == "#00ff00" for span in result.spans)

    def test_removed_line(self):
        result = _diff_coloreado("-linea borrada")
        assert "linea borrada" in result.plain
        assert any(span.style == "#ff5f5f" for span in result.spans)

    def test_hunk_header(self):
        result = _diff_coloreado("@@ -1,3 +1,4 @@")
        assert any(span.style == "#00afff" for span in result.spans)

    def test_diff_header(self):
        result = _diff_coloreado("diff --git a/f.py b/f.py")
        assert any(span.style == "#888888" for span in result.spans)

    def test_word_diff_added(self):
        result = _diff_coloreado('{+palabra+}')
        assert "palabra" in result.plain
        assert any(span.style == "#00ff00 on #003300" for span in result.spans)

    def test_word_diff_deleted(self):
        result = _diff_coloreado('[-palabra-]')
        assert "palabra" in result.plain
        assert any(span.style == "#ff5f5f on #330000" for span in result.spans)

    def test_rich_escape_brackets(self):
        diff = "texto con [corchetes] y {llaves}"
        result = _diff_coloreado(diff)
        assert "[corchetes]" in result.plain or "corchetes" in result.plain
        assert "{llaves}" in result.plain or "llaves" in result.plain

    def test_mixed_content(self):
        raw = 'diff --git a/f.txt b/f.txt\n@@ -1 +1 @@\n-base\n{+nueva+}'
        result = _diff_coloreado(raw)
        styles = [span.style for span in result.spans]
        assert "#888888" in styles
        assert "#00afff" in styles
        assert "#ff5f5f" in styles
        assert "#00ff00 on #003300" in styles

