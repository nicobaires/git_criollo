import fs from "node:fs";

export interface Repo {
  name: string;
  path: string;
}

const CONFIG_URL = new URL("../../repos.json", import.meta.url);

export function loadRepos(): Repo[] {
  try {
    const raw = fs.readFileSync(CONFIG_URL, "utf-8");
    const config = JSON.parse(raw) as { repos?: Repo[] };
    return Array.isArray(config?.repos) ? config.repos : [];
  } catch {
    return [];
  }
}