import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export function findProjectRoot(): string {
  let dir = path.dirname(fileURLToPath(import.meta.url));
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, "astro.config.mjs"))) return dir;
    dir = path.dirname(dir);
  }
  throw new Error("No se encontró la raíz del proyecto (astro.config.mjs)");
}