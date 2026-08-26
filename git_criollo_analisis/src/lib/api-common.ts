import fs from "node:fs";
import path from "node:path";
import { execSync, spawn } from "node:child_process";
import { findProjectRoot } from "./paths";

export const PROJECT_ROOT = findProjectRoot();
export const CONFIG_FILE = path.join(PROJECT_ROOT, "repos.json");
export const EXTRACTOR_FILE = path.join(PROJECT_ROOT, "script", "extract_stats.py");
export const STATS_DIR = path.join(PROJECT_ROOT, "src", "data", "stats");

export interface Repo { name: string; path: string; }

export function readConfig(): Repo[] {
  try {
    const raw = fs.readFileSync(CONFIG_FILE, "utf-8");
    const config = JSON.parse(raw) as { repos?: Repo[] };
    return Array.isArray(config?.repos) ? config.repos : [];
  } catch {
    return [];
  }
}

export function writeConfig(repos: Repo[]): void {
  const payload = JSON.stringify({ repos }, null, 2) + "\n";
  fs.writeFileSync(CONFIG_FILE, payload, "utf-8");
}

export function jsonError(error: string, status: number): Response {
  return new Response(JSON.stringify({ error }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function gitTopLevel(dir: string): string | null {
  try {
    const out = execSync("git rev-parse --show-toplevel", {
      cwd: dir,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    return out.trim() || null;
  } catch {
    return null;
  }
}

export function gitBranches(dir: string): string[] {
  try {
    const out = execSync("git branch --format='%(refname:short)'", {
      cwd: dir,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    return out.trim().split("\n").filter(Boolean);
  } catch {
    return [];
  }
}

export function sanitizeName(base: string): string {
  const clean = base
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
  return clean || "repo";
}

export function sanitizeBranch(branch: string): string {
  return branch.replace(/\//g, "-");
}

export function uniqueName(base: string, existing: Repo[]): string {
  const taken = new Set(existing.map((r) => r.name.toLowerCase()));
  let name = sanitizeName(base);
  let candidate = name;
  let i = 2;
  while (taken.has(candidate.toLowerCase())) {
    candidate = `${name}-${i}`;
    i += 1;
  }
  return candidate;
}

export function spawnExtractor(repoPath: string, outputPath: string, args: string[] = []) {
  const venvPython = path.join(PROJECT_ROOT, "..", ".venv", "bin", "python");
  const python = fs.existsSync(venvPython) ? venvPython : "python3";
  const child = spawn(python, [EXTRACTOR_FILE, repoPath, "-o", outputPath, ...args], {
    cwd: PROJECT_ROOT,
    stdio: "ignore",
  });
  child.on("error", (err) => console.error("[extractor]", err.message));
  return child;
}
