from dataclasses import dataclass, field
from git import Repo


@dataclass
class BranchInfo:
    active: str
    branches: list[str]


@dataclass
class CommitInfo:
    hash: str
    message: str
    author: str


@dataclass
class StatusInfo:
    staged: list[str] = field(default_factory=list)
    unstaged: list[str] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)
    is_empty_repo: bool = False


class GitService:
    def __init__(self, path: str) -> None:
        self.repo = Repo(path, search_parent_directories=True)

    def get_branches(self) -> BranchInfo:
        try:
            active = self.repo.active_branch.name
        except TypeError:
            active = "master"
        branches = [b.name for b in self.repo.branches]
        return BranchInfo(active=active, branches=branches)

    def get_commits(self, n: int = 6) -> list[CommitInfo]:
        try:
            return [
                CommitInfo(
                    hash=c.hexsha[:7],
                    message=c.message.split("\n")[0],
                    author=c.author.name,
                )
                for c in self.repo.iter_commits(max_count=n)
            ]
        except Exception:
            return []

    def get_status(self) -> StatusInfo:
        info = StatusInfo()
        try:
            try:
                info.staged = [item.a_path for item in self.repo.index.diff("HEAD")]
            except Exception:
                info.is_empty_repo = True
            info.unstaged = [item.a_path for item in self.repo.index.diff(None)]
            info.untracked = list(self.repo.untracked_files)
        except Exception:
            pass
        return info

    def create_branch(self, name: str) -> None:
        self.repo.create_head(name)

    def checkout(self, name: str) -> None:
        self.repo.git.checkout(name)

    def delete_branch(self, name: str, force: bool = True) -> None:
        self.repo.delete_head(name, force=force)

    def pull(self) -> None:
        self.repo.remotes.origin.pull()

    def push(self, branch: str) -> None:
        self.repo.remotes.origin.push(branch)

    def stage_all(self) -> None:
        self.repo.git.add(all=True)

    def commit(self, message: str) -> None:
        self.repo.index.commit(message)
