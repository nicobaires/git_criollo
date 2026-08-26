import re
from rich.text import Text


def _diff_coloreado(diff: str) -> Text:
    result = Text()
    lineas = diff.split("\n")
    for i, raw in enumerate(lineas):
        if i > 0:
            result.append("\n")

        line_style = None
        if raw.startswith(("diff --git", "index", "---", "+++")):
            line_style = "#888888"
        elif raw.startswith("@@"):
            line_style = "#00afff"
        elif raw.startswith("+"):
            line_style = "#00ff00"
        elif raw.startswith("-"):
            line_style = "#ff5f5f"

        pos = 0
        for m in re.finditer(r"\[-([^\]]*?)-\]|\{\+([^}]*?)\+\}", raw):
            if m.start() > pos:
                result.append(raw[pos:m.start()], style=line_style)
            deleted, added = m.group(1), m.group(2)
            content = deleted if deleted is not None else added
            style = "#ff5f5f on #330000" if deleted is not None else "#00ff00 on #003300"
            result.append(content, style=style)
            pos = m.end()

        if pos < len(raw):
            result.append(raw[pos:], style=line_style)

    return result