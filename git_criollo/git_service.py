import os
import tempfile
import logging
import shlex
from git import Repo, GitCommandError, BadName, InvalidGitRepositoryError

from git_criollo.models import (
    BranchInfo, CommitInfo, CommitDetail, DiffHunk, ConflictRegion, StatusInfo,
)


os.makedirs(os.path.expanduser("~/.gitcriollo"), exist_ok=True)
logging.basicConfig(
    filename=os.path.expanduser("~/.gitcriollo/debug.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class GitService:
    def __init__(self, path: str) -> None:
        self.repo = Repo(path, search_parent_directories=True)

    def get_branches(self) -> BranchInfo:
        is_detached = self.repo.head.is_detached
        try:
            active = self.repo.active_branch.name
        except TypeError:
            active = self.repo.head.commit.hexsha[:7]

        branches = [b.name for b in self.repo.branches]

        remotes = []
        try:
            for r in self.repo.remotes:
                for ref in r.refs:
                    remotes.append(f"{r.name}/{ref.remote_head}")
        except Exception as e:
            logging.warning(f"Error obteniendo remotes: {e}")

        tags = [t.name for t in self.repo.tags]

        ahead: dict[str, int] = {}
        behind: dict[str, int] = {}
        try:
            for head in self.repo.branches:
                tracking = head.tracking_branch()
                if tracking:
                    a = sum(1 for _ in self.repo.iter_commits(f"{tracking.name}..{head.name}"))
                    b = sum(1 for _ in self.repo.iter_commits(f"{head.name}..{tracking.name}"))
                    if a or b:
                        ahead[head.name] = a
                        behind[head.name] = b
        except Exception as e:
            logging.warning(f"Error calculando ahead/behind: {e}")

        return BranchInfo(
            active=active,
            branches=branches,
            remotes=remotes,
            tags=tags,
            is_detached=is_detached,
            ahead=ahead,
            behind=behind,
        )

    def get_graph_log(self, skip: int = 0, n: int = 20) -> list[str]:
        try:
            result = self.repo.git.log("--graph", "--oneline", "--all",
                                       "--skip", str(skip), "-n", str(n))
            return [line.rstrip() for line in result.split("\n") if line.strip()]
        except GitCommandError as e:
            logging.warning(f"Error en get_graph_log: {e}")
            return []
        except Exception as e:
            logging.exception(f"Error inesperado en get_graph_log: {e}")
            return []

    def get_commits(self, skip: int = 0, n: int = 20) -> list[CommitInfo]:
        try:
            return [
                CommitInfo(
                    hash=c.hexsha[:7],
                    message=c.message.split("\n")[0],
                    author=c.author.name,
                )
                for c in self.repo.iter_commits(max_count=n, skip=skip)
            ]
        except Exception as e:
            logging.exception(f"Error obteniendo commits: {e}")
            return []

    def get_commit_detail(self, sha: str) -> CommitDetail:
        commit = self.repo.commit(sha)
        diff = self.repo.git.show(sha, "--format=fuller")
        stats = commit.stats.files
        files = sorted(
            (path, s["insertions"], s["deletions"])
            for path, s in stats.items()
        )
        return CommitDetail(
            hash=sha[:7],
            author=f"{commit.author.name} <{commit.author.email}>",
            author_date=commit.authored_datetime.strftime("%Y-%m-%d %H:%M"),
            committer=f"{commit.committer.name} <{commit.committer.email}>",
            committer_date=commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
            message=commit.message.strip(),
            files=files,
            diff=diff,
        )

    def get_status(self) -> StatusInfo:
        info = StatusInfo()
        try:
            try:
                info.staged = [item.a_path for item in self.repo.index.diff("HEAD")]
            except BadName:
                info.is_empty_repo = True
                logging.debug("Repo vacío detectado (BadName en diff HEAD)")
            except InvalidGitRepositoryError as e:
                logging.error(f"Repo inválido: {e}")
                raise
            except Exception as e:
                logging.exception(f"Error inesperado en staged diff: {e}")
            info.unstaged = [item.a_path for item in self.repo.index.diff(None)]
            info.untracked = list(self.repo.untracked_files)
        except Exception as e:
            logging.exception(f"Error crítico en get_status: {e}")
        return info

    def get_diff(self, path: str, staged: bool = False) -> str:
        try:
            if staged:
                return self.repo.git.diff("--cached", "--word-diff", "--", path) or "(sin cambios)"
            result = self.repo.git.diff(None, "--word-diff", "--", path)
            if not result and path in self.repo.untracked_files:
                result = self.repo.git.diff("--no-index", os.devnull, path, "--word-diff")
            return result or "(sin cambios)"
        except Exception as e:
            logging.exception(f"Error obteniendo diff para {path}: {e}")
            return f"Error al obtener diff: {e}"

    def create_branch(self, name: str) -> None:
        self.repo.create_head(name)

    def checkout(self, name: str) -> None:
        self.repo.git.checkout(name)

    def checkout_remote(self, remote_ref: str) -> None:
        local_name = remote_ref.rsplit("/", 1)[1]
        self.repo.git.checkout("-b", local_name, remote_ref)

    def delete_branch(self, name: str, force: bool = True) -> None:
        self.repo.delete_head(name, force=force)

    def stage_file(self, path: str) -> None:
        self.repo.git.add(path)

    def unstage_file(self, path: str) -> None:
        try:
            self.repo.git.reset("HEAD", "--", path)
        except Exception:
            self.repo.git.rm("--cached", path)

    def stage_all(self) -> None:
        self.repo.git.add(all=True)

    def commit(self, message: str) -> None:
        self.repo.index.commit(message)

    def amend_commit(self, message: str) -> None:
        self.repo.git.commit("--amend", "-m", message)

    def pull(self) -> None:
        try:
            remote = self.repo.remote()
            remote.pull()
        except ValueError as e:
            logging.error(f"No hay remote por defecto configurado: {e}")
            raise RuntimeError("No hay remote por defecto configurado. Usá 'git remote add' primero.") from e
        except GitCommandError as e:
            logging.exception(f"Error en pull: {e}")
            raise

    def push(self, branch: str) -> None:
        try:
            remote = self.repo.remote()
            remote.push(branch)
        except ValueError as e:
            logging.error(f"No hay remote por defecto configurado: {e}")
            raise RuntimeError("No hay remote por defecto configurado.") from e
        except GitCommandError as e:
            logging.exception(f"Error en push: {e}")
            raise

    def fetch(self) -> None:
        try:
            remote = self.repo.remote()
            remote.fetch()
        except ValueError as e:
            logging.error(f"No hay remote por defecto: {e}")
            raise RuntimeError("No hay remote por defecto configurado.") from e
        except GitCommandError as e:
            logging.exception(f"Error en fetch: {e}")
            raise

    def merge(self, branch: str) -> None:
        self.repo.git.merge(branch)

    def cherry_pick(self, sha: str) -> None:
        self.repo.git.cherry_pick(sha)

    def stash_push(self, message: str = "") -> None:
        if message:
            self.repo.git.stash("push", "-m", message)
        else:
            self.repo.git.stash("push")

    def stash_pop(self) -> None:
        self.repo.git.stash("pop")

    def stash_list(self) -> list[str]:
        try:
            result = self.repo.git.stash("list")
            return [line for line in result.split("\n") if line.strip()]
        except Exception as e:
            logging.exception(f"Error listando stashes: {e}")
            return []

    def get_tags(self) -> list[str]:
        return [t.name for t in self.repo.tags]

    def create_tag(self, name: str) -> None:
        self.repo.create_tag(name)

    def delete_tag(self, name: str) -> None:
        self.repo.delete_tag(name)

    def run_command(self, cmd: str) -> str:
        cmd = cmd.strip()
        if not cmd.startswith("git "):
            cmd = "git " + cmd

        try:
            args = shlex.split(cmd)
        except ValueError as e:
            return f"Error: comando inválido - {e}"

        dangerous = {";", "&&", "||", "|", "`", "$", "(", ")"}
        for arg in args:
            for char in dangerous:
                if char in arg:
                    return f"Error: caracteres no permitidos en el comando: {char}"

        try:
            result = self.repo.git.execute(args)
            return result
        except Exception as e:
            logging.exception(f"Error ejecutando comando: {cmd}")
            return f"Error: {e}"

    def get_working_diff(self) -> str:
        try:
            return self.repo.git.diff(None, "--word-diff") or "(sin cambios)"
        except Exception as e:
            logging.exception(f"Error en working diff: {e}")
            return "(sin cambios)"

    def get_staged_diff(self) -> str:
        try:
            return self.repo.git.diff("--cached", "--word-diff") or "(sin cambios)"
        except Exception as e:
            logging.exception(f"Error en staged diff: {e}")
            return "(sin cambios)"

    def parse_diff_hunks(self, path: str) -> list[DiffHunk]:
        raw = self.repo.git.diff(None, "--unified=3", "--", path)
        if not raw:
            return []
        lines = raw.split("\n")
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith("+++"):
                header_end = i + 1
                break
        header_lines = lines[:header_end]
        hunks = []
        current_header = ""
        current_lines: list[str] = []
        in_hunk = False
        for line in lines[header_end:]:
            if line.startswith("@@"):
                if in_hunk and current_lines:
                    hunks.append(DiffHunk(
                        header=current_header,
                        lines=current_lines,
                        raw=current_header + "\n" + "\n".join(current_lines)
                    ))
                current_header = line
                current_lines = []
                in_hunk = True
            elif in_hunk:
                current_lines.append(line)
        if in_hunk and current_lines:
            hunks.append(DiffHunk(
                header=current_header,
                lines=current_lines,
                raw=current_header + "\n" + "\n".join(current_lines)
            ))
        return hunks

    def stage_hunk(self, path: str, hunk: DiffHunk) -> None:
        raw_diff = self.repo.git.diff(None, "--unified=3", "--", path)
        header_part = raw_diff.split("\n@@")[0] + "\n"
        patch = header_part + hunk.raw + "\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(patch)
            f.flush()
            patch_path = f.name
        try:
            self.repo.git.apply("--cached", patch_path)
        except GitCommandError as e:
            logging.exception(f"Error aplicando hunk en {path}: {e}")
            os.unlink(patch_path)
            raise RuntimeError(
                f"No se pudo aplicar el hunk. Probablemente las líneas de contexto no coinciden. "
                f"Error: {e.stderr or str(e)}"
            ) from e
        except Exception as e:
            logging.exception(f"Error inesperado aplicando hunk: {e}")
            os.unlink(patch_path)
            raise
        finally:
            if os.path.exists(patch_path):
                os.unlink(patch_path)

    def get_gitignore_content(self) -> str:
        gitignore_path = os.path.join(self.repo.working_tree_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path) as f:
                return f.read()
        return "(el archivo .gitignore no existe)"

    def get_commits_for_rebase(self, sha: str) -> list[CommitInfo]:
        base = f"{sha}~1"
        commits = []
        try:
            for c in self.repo.iter_commits(f"{base}..HEAD", reverse=True):
                commits.append(CommitInfo(
                    hash=c.hexsha[:7],
                    message=c.message.split("\n")[0],
                    author=c.author.name,
                ))
        except Exception as e:
            logging.exception(f"Error obteniendo commits para rebase: {e}")
        return commits

    def get_parent_sha(self, sha: str) -> str | None:
        try:
            commit = self.repo.commit(sha)
            if commit.parents:
                return commit.parents[0].hexsha
        except Exception as e:
            logging.exception(f"Error obteniendo parent de {sha}: {e}")
        return None

    def run_rebase(self, base_sha: str, todos: list[tuple[str, str]]) -> None:
        todo_lines = [f"{action} {sha}" for sha, action in todos]
        todo_content = "\n".join(todo_lines) + "\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.todo', delete=False) as f:
            f.write(todo_content)
            todo_path = f.name
        try:
            #self.repo.git.execute(
                #["git", "rebase", "-i", base_sha],
                #env={**os.environ, "GIT_SEQUENCE_EDITOR": f"cp {todo_path}"},
            self.repo.git.execute(
                ["git", "rebase", "-i", base_sha],
                env={**os.environ, "GIT_SEQUENCE_EDITOR": f'cp "{todo_path}"'},
            )
        except Exception as e:
            logging.exception(f"Error en rebase interactivo: {e}")
            raise
        finally:
            os.unlink(todo_path)

    def is_merge_in_progress(self) -> bool:
        try:
            return os.path.exists(os.path.join(self.repo.working_tree_dir, ".git", "MERGE_HEAD"))
        except Exception as e:
            logging.warning(f"Error verificando merge: {e}")
            return False

    def get_conflicted_files(self) -> list[str]:
        try:
            result = self.repo.git.diff("--name-only", "--diff-filter=U")
            return [f for f in result.split("\n") if f.strip()]
        except Exception as e:
            logging.exception(f"Error obteniendo archivos en conflicto: {e}")
            return []

    def get_conflict_regions(self, path: str) -> list[ConflictRegion]:
        full_path = os.path.join(self.repo.working_tree_dir, path)
        try:
            with open(full_path) as f:
                content = f.read()
        except Exception as e:
            logging.warning(f"Error leyendo {path} para conflictos: {e}")
            return []
        lines = content.split("\n")
        regions = []
        i = 0
        while i < len(lines):
            if lines[i].startswith("<<<<<<<"):
                start = i
                i += 1
                ours_lines = []
                while i < len(lines) and not lines[i].startswith("======="):
                    ours_lines.append(lines[i])
                    i += 1
                if i < len(lines) and lines[i].startswith("======="):
                    i += 1
                theirs_lines = []
                while i < len(lines) and not lines[i].startswith(">>>>>>>"):
                    theirs_lines.append(lines[i])
                    i += 1
                end = i
                if i < len(lines):
                    i += 1
                regions.append(ConflictRegion(
                    start=start,
                    end=end,
                    ours="\n".join(ours_lines),
                    theirs="\n".join(theirs_lines),
                ))
            else:
                i += 1
        return regions

    def resolve_conflict_region(self, path: str, region: ConflictRegion, choice: str) -> None:
        full_path = os.path.join(self.repo.working_tree_dir, path)
        with open(full_path) as f:
            lines = f.read().split("\n")
        if choice == "ours":
            replacement = region.ours.split("\n")
        elif choice == "theirs":
            replacement = region.theirs.split("\n")
        elif choice == "both":
            replacement = (region.ours + "\n" + region.theirs).split("\n")
        else:
            raise ValueError(f"Opción de resolución inválida: {choice}")
        new_lines = lines[:region.start] + replacement + lines[region.end + 1:]
        with open(full_path, "w") as f:
            f.write("\n".join(new_lines))

    def add_to_gitignore(self, pattern: str) -> None:
        gitignore_path = os.path.join(self.repo.working_tree_dir, ".gitignore")
        content = ""
        if os.path.exists(gitignore_path):
            with open(gitignore_path) as f:
                content = f.read()
            if pattern in content.split("\n"):
                return
        with open(gitignore_path, "a") as f:
            if content and not content.endswith("\n"):
                f.write("\n")
            f.write(pattern + "\n")

    def discard_changes(self, path: str) -> None:
        """Descarta cambios locales en el working directory."""
        if path in self.repo.untracked_files:
            full_path = os.path.join(self.repo.working_tree_dir, path)
            if os.path.isfile(full_path):
                os.remove(full_path)
        else:
            self.repo.git.checkout("--", path)