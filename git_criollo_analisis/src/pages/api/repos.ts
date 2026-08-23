// src/pages/api/repos.ts
// POST /api/repos — agrega un repositorio local a repos.json y dispara la
// generación de sus stats con script/extract_stats.py
// DELETE /api/repos — quita un repositorio de repos.json y borra sus stats
import fs from "node:fs";
import path from "node:path";
import { execSync, spawn } from "node:child_process";
import { findProjectRoot } from "../../lib/paths";

export const prerender = false;

const PROJECT_ROOT = findProjectRoot();
const CONFIG_FILE = path.join(PROJECT_ROOT, "repos.json");
const EXTRACTOR_FILE = path.join(PROJECT_ROOT, "script", "extract_stats.py");
const STATS_DIR = path.join(PROJECT_ROOT, "src", "data", "stats");

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

function writeConfig(repos: Repo[]) {
  const payload = JSON.stringify({ repos }, null, 2) + "\n";
  fs.writeFileSync(CONFIG_FILE, payload, "utf-8");
}

function sanitizeName(base: string): string {
  const clean = base
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
  return clean || "repo";
}

function uniqueName(base: string, existing: Repo[]): string {
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

function gitTopLevel(dir: string): string | null {
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

function generateStats(repoPath: string, outputPath: string, branch?: string) {
  const venvPython = path.join(PROJECT_ROOT, "..", ".venv", "bin", "python");
  const python = fs.existsSync(venvPython) ? venvPython : "python3";
  const args = [EXTRACTOR_FILE, repoPath, "-o", outputPath];
  if (branch) args.push("--branch", branch);
  const child = spawn(python, args, {
    cwd: PROJECT_ROOT,
    stdio: "ignore",
  });
  child.on("error", (err) => {
    console.error("[api/repos] no se pudo generar stats:", err.message);
  });
}

export async function POST({ request }: { request: Request }) {
  let body: { path?: string };
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Body JSON inválido" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const rawPath = body.path?.trim() ?? "";
  if (!rawPath) {
    return jsonError("Ingresá la ruta de una carpeta", 400);
  }

  const resolved = path.resolve(rawPath);
  let stat: fs.Stats;
  try {
    stat = fs.statSync(resolved);
  } catch {
    return jsonError(`No existe: ${resolved}`, 400);
  }
  if (!stat.isDirectory()) {
    return jsonError("La ruta no es una carpeta", 400);
  }

  const topLevel = gitTopLevel(resolved);
  if (!topLevel) {
    return jsonError("La carpeta no es un repositorio Git", 400);
  }

  const repos = readConfig();
  const realTop = fs.realpathSync(topLevel);
  for (const r of repos) {
    try {
      if (fs.realpathSync(r.path) === realTop) {
        return jsonError(`El repositorio ya está agregado como "${r.name}"`, 409);
      }
    } catch {
      // ruta existente en config pero ya no disponible: se ignora
    }
  }

  const name = uniqueName(path.basename(realTop), repos);
  repos.push({ name, path: realTop });
  writeConfig(repos);

  const branchDir = path.join(STATS_DIR, name);
  fs.mkdirSync(branchDir, { recursive: true });

  const branches = gitBranches(realTop);
  const branch = branches.length > 0 ? branches[0] : undefined;
  generateStats(realTop, path.join(branchDir, `${branch ?? "HEAD"}.json`), branch);

  return new Response(
    JSON.stringify({ repo: { name, path: realTop }, generating: true }),
    {
      status: 201,
      headers: { "Content-Type": "application/json" },
    }
  );
}

function jsonError(error: string, status: number) {
  return new Response(JSON.stringify({ error }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const NAME_RE = /^[a-z0-9_-]+$/;

export async function DELETE({ request }: { request: Request }) {
  let body: { name?: string };
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Body JSON inválido" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const name = body.name?.trim() ?? "";
  if (!NAME_RE.test(name)) {
    return jsonError("Nombre de repositorio inválido", 400);
  }

  const repos = readConfig();
  const match = repos.find((r) => r.name === name);
  if (!match) {
    return jsonError(`El repositorio "${name}" no está en la lista`, 404);
  }

  writeConfig(repos.filter((r) => r.name !== name));

  const statsDir = path.join(STATS_DIR, name);
  fs.rmSync(statsDir, { recursive: true, force: true });

  return new Response(JSON.stringify({ ok: true, repo: { name } }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
