// src/pages/api/branches.ts
// GET /api/branches?repo=<name> — lista branches con stats disponibles
// POST /api/branches — extrae stats para un branch específico
import fs from "node:fs";
import path from "node:path";
import { execSync, spawn } from "node:child_process";
import { findProjectRoot } from "../../lib/paths";
import { listBranches } from "../../lib/stats";

export const prerender = false;

const PROJECT_ROOT = findProjectRoot();
const EXTRACTOR_FILE = path.join(PROJECT_ROOT, "script", "extract_stats.py");
const STATS_DIR = path.join(PROJECT_ROOT, "src", "data", "stats");
const CONFIG_FILE = path.join(PROJECT_ROOT, "repos.json");

interface Repo {
  name: string;
  path: string;
}

function readConfig(): Repo[] {
  try {
    const raw = fs.readFileSync(CONFIG_FILE, "utf-8");
    const config = JSON.parse(raw) as { repos?: Repo[] };
    return Array.isArray(config?.repos) ? config.repos : [];
  } catch {
    return [];
  }
}

function gitBranches(dir: string): string[] {
  try {
    const out = execSync("git branch --format=%(refname:short)", {
      cwd: dir,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    return out.trim().split("\n").filter(Boolean);
  } catch {
    return [];
  }
}

export async function GET({ url }: { url: URL }) {
  const repoName = url.searchParams.get("repo");
  if (!repoName) {
    return jsonError("Falta el parámetro repo", 400);
  }

  const repos = readConfig();
  const repo = repos.find((r) => r.name === repoName);
  if (!repo) {
    return jsonError(`Repo "${repoName}" no encontrado`, 404);
  }

  const gitBranchesList = gitBranches(repo.path);
  const statsBranches = listBranches(repoName);
  const statsSet = new Set(statsBranches);

  const branches = gitBranchesList.map((b) => ({
    name: b,
    hasStats: statsSet.has(b),
  }));

  return new Response(JSON.stringify({ branches }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

export async function POST({ request }: { request: Request }) {
  let body: { repo?: string; branch?: string };
  try {
    body = await request.json();
  } catch {
    return jsonError("Body JSON inválido", 400);
  }

  const repoName = body.repo?.trim();
  const branch = body.branch?.trim();
  if (!repoName || !branch) {
    return jsonError("Faltan repo y branch", 400);
  }

  const repos = readConfig();
  const repo = repos.find((r) => r.name === repoName);
  if (!repo) {
    return jsonError(`Repo "${repoName}" no encontrado`, 404);
  }

  const branchDir = path.join(STATS_DIR, repoName);
  fs.mkdirSync(branchDir, { recursive: true });
  const outputPath = path.join(branchDir, `${branch}.json`);

  const venvPython = path.join(PROJECT_ROOT, "..", ".venv", "bin", "python");
  const python = fs.existsSync(venvPython) ? venvPython : "python3";
  const child = spawn(python, [EXTRACTOR_FILE, repo.path, "-o", outputPath, "--branch", branch], {
    cwd: PROJECT_ROOT,
    stdio: "ignore",
  });
  child.on("error", (err) => {
    console.error("[api/branches] no se pudo generar stats:", err.message);
  });

  return new Response(JSON.stringify({ ok: true, repo: repoName, branch, generating: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

function jsonError(error: string, status: number) {
  return new Response(JSON.stringify({ error }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
