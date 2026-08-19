from git_criollo.git_service import GitService
import json

# TODO: crear un objeto GitService
git = GitService('.')
lista_commits = git.get_commits(skip=0, n=9999)



# Tus objetos CommitInfo o una lista de diccionarios ya armada
json_list = [
    {"hash": commit.hash, "message": commit.message, "author": commit.author}
    for commit in lista_commits
]

# Guardar la estructura en un archivo físico del disco
with open("commits.json", "w", encoding="utf-8") as archivo:
    json.dump(json_list, archivo, indent=2, ensure_ascii=False)