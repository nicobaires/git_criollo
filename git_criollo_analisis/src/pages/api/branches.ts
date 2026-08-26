// src/pages/api/branches.ts
// GET /api/branches?repo=<n> — lista branches con stats disponibles
// POST /api/branches — extrae stats para un branch específico
import fs from "node:fs";
import path from "node:path";
import {
  STATS_DIR,
  readConfig,
  jsonError,
  gitBranches,
  spawnExtractor,
  sanitizeBranch,
} from "../../lib/api-common";
import { listBranches } from "../../lib/stats";

export const prerender = false;

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
    hasStats: statsSet.has(sanitizeBranch(b)),
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

  const safeBranch = sanitizeBranch(branch);
  const branchDir = path.join(STATS_DIR, repoName);
  fs.mkdirSync(branchDir, { recursive: true });
  const outputPath = path.join(branchDir, `${safeBranch}.json`);

  spawnExtractor(repo.path, outputPath, ["--branch", branch]);

  return new Response(JSON.stringify({ ok: true, repo: repoName, branch, generating: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}