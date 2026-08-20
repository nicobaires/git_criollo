import fs from "node:fs";
import path from "node:path";
import { findProjectRoot } from "./paths";

export interface Repo {
  name: string;
  path: string;
}

const CONFIG_FILE = path.join(findProjectRoot(), "repos.json");

export function loadRepos(): Repo[] {
  try {
    const raw = fs.readFileSync(CONFIG_FILE, "utf-8");
    const config = JSON.parse(raw) as { repos?: Repo[] };
    return Array.isArray(config?.repos) ? config.repos : [];
  } catch {
    return [];
  }
}