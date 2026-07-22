from dataclasses import dataclass, field


@dataclass
class BranchInfo:
    active: str
    branches: list[str]
    remotes: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    is_detached: bool = False
    ahead: dict[str, int] = field(default_factory=dict)
    behind: dict[str, int] = field(default_factory=dict)


@dataclass
class CommitInfo:
    hash: str
    message: str
    author: str


@dataclass
class CommitDetail:
    hash: str
    author: str
    date: str
    message: str
    diff: str


@dataclass
class DiffHunk:
    header: str
    lines: list[str]
    raw: str


@dataclass
class ConflictRegion:
    start: int
    end: int
    ours: str
    theirs: str


@dataclass
class StatusInfo:
    staged: list[str] = field(default_factory=list)
    unstaged: list[str] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)
    is_empty_repo: bool = False
