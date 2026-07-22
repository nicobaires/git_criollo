CSS = """
Horizontal { width: 100%; height: 100%; }
.columna { width: 25%; height: 100%; border-right: solid #333; }
.columna-derecha { width: 75%; height: 100%; }
.panel { padding: 1; background: #121212; border-bottom: solid #222; }
.panel-status { height: auto; }
.panel-history { height: 1fr; }
ListView { background: #1a1a1a; margin: 1; border: tall #444; }
ListView:focus { border: tall #00afff; }
#lista_ramas { height: 1fr; }
#lista_ramas:focus { border: tall #00afd7; }
#lista_staged { height: auto; max-height: 8; margin: 0 0 0 1; border: solid #333; }
#lista_unstaged { height: auto; max-height: 8; margin: 0 0 0 1; border: solid #333; }
#lista_commits { height: 1fr; margin: 1; border: solid #333; }
#lista_commits:focus { border: tall #ffaf00; }
ListItem { padding: 0 1; }
ListItem.--highlight { background: #005f87; }
Label { margin: 1 0 0 2; }
.label-subtitle { margin: 0 0 0 2; text-style: bold; }
#atajos_help { margin: 1 0 1 2; color: #888; height: auto; }
#info_rama { margin: 0 0 0 2; color: #aaa; height: auto; }
"""
