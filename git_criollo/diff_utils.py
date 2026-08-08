import re

from textual.markup import escape


def _diff_coloreado(diff: str) -> str:
    result = []
    for raw in diff.split("\n"):
        line_style = None
        if raw.startswith("diff --git") or raw.startswith("index") or raw.startswith("---") or raw.startswith("+++"):
            line_style = "#888888"
        elif raw.startswith("@@"):
            line_style = "#00afff"
        elif raw.startswith("+"):
            line_style = "#00ff00"
        elif raw.startswith("-"):
            line_style = "#ff5f5f"

        parts = []
        pos = 0
        for m in re.finditer(r"\[-([^\]]*?)-\]|\{\+([^}]*?)\+\}", raw):
            if m.start() > pos:
                parts.append(escape(raw[pos:m.start()]))
            deleted = m.group(1)
            added = m.group(2)
            content = escape(deleted or added)
            if deleted is not None:
                parts.append(f"[#ff5f5f on #330000]{content}[/]")
            else:
                parts.append(f"[#00ff00 on #003300]{content}[/]")
            pos = m.end()
        if pos < len(raw):
            parts.append(escape(raw[pos:]))

        line_str = "".join(parts)
        if line_style:
            result.append(f"[{line_style}]{line_str}[/]")
        else:
            result.append(line_str)

    return "\n".join(result)
