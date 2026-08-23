// src/pages/api/repos.ts
// POST /api/repos — agrega un repositorio local a repos.json y dispara la
// generación de sus stats con script/extract_stats.py
// DELETE /api/repos — quita un repositorio de repos.json y borra sus stats
import fs from "node:fs";
import path from "node:path";
import {
  STATS_DIR,
  readConfig,
  writeConfig,
  jsonError,
  gitTopLevel,
  gitBranches,
  uniqueName,
  spawnExtractor,
} from "../../lib/api-common";

export const prerender = false;

export async function POST({ request }: { request: Request }) {
  let body: { path?: string };
  try {
    body = await request.json();
  } catch {
    return jsonError("Body JSON inválido", 400);
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
      // ruta existente en config pero ya no disponible
    }
  }

  const name = uniqueName(path.basename(realTop), repos);
  repos.push({ name, path: realTop });
  writeConfig(repos);

  const branchDir = path.join(STATS_DIR, name);
  fs.mkdirSync(branchDir, { recursive: true });

  const branches = gitBranches(realTop);
  const branch = branches.length > 0 ? branches[0] : undefined;
  const args = branch ? ["--branch", branch] : [];
  spawnExtractor(realTop, path.join(branchDir, `${branch ?? "HEAD"}.json`), args);

  return new Response(
    JSON.stringify({ repo: { name, path: realTop }, generating: true }),
    { status: 201, headers: { "Content-Type": "application/json" } }
  );
}

const NAME_RE = /^[a-z0-9_-]+$/;

export async function DELETE({ request }: { request: Request }) {
  let body: { name?: string };
  try {
    body = await request.json();
  } catch {
    return jsonError("Body JSON inválido", 400);
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
