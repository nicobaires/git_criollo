import fs from "node:fs";
import path from "node:path";
import { findProjectRoot } from "./paths";

export interface Stats {
  meta: {
    repo_name: string;
    branch: string;
    generated_at: string;
    since: string | null;
    until: string | null;
    total_commits_analyzed: number;
    repo_age_days: number;
    years: number[];
  };
  kpis: {
    total_commits: number;
    total_authors: number;
    total_added: number;
    total_deleted: number;
    total_changes: number;
  };
  life_metrics: {
    active_days: number;
    total_days: number;
    active_days_percentage: number;
    average_commits_per_day: number;
    top_day: { date: string; commits: number } | null;
    current_streak_days: number;
  };
  timeline: {
    months: string[];
    weeks: string[];
    days: string[];
    commits_by_author: Record<string, number[]>;
    commits_by_author_week: Record<string, number[]>;
    commits_by_author_day: Record<string, number[]>;
    loc_by_month: { months: string[]; added: number[]; deleted: number[] };
    loc_by_week: { weeks: string[]; added: number[]; deleted: number[] };
    loc_by_day: { days: string[]; added: number[]; deleted: number[] };
  };
  hot_files: { path: string; changes: number }[];
  heatmap: { date: string; count: number }[];
  distribution: { author: string; commits: number; percentage: number }[];
}

const STATS_DIR = path.join(findProjectRoot(), "src", "data", "stats");

function sanitizeBranch(branch: string): string {
  return branch.replace(/\//g, "-");
}

export function getStats(repoName: string, branch?: string): Stats | null {
  if (branch) {
    const file = path.join(STATS_DIR, repoName, `${sanitizeBranch(branch)}.json`);
    try {
      return JSON.parse(fs.readFileSync(file, "utf-8")) as Stats;
    } catch {
      return null;
    }
  }
  const dir = path.join(STATS_DIR, repoName);
  try {
    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    if (files.length === 0) return null;
    const first = files.sort()[0];
    return JSON.parse(fs.readFileSync(path.join(dir, first), "utf-8")) as Stats;
  } catch {
    return null;
  }
}

export function listBranches(repoName: string): string[] {
  const dir = path.join(STATS_DIR, repoName);
  try {
    return fs.readdirSync(dir).filter((f) => f.endsWith(".json")).map((f) => path.basename(f, ".json")).sort();
  } catch {
    return [];
  }
}

export function loadStatsMap(): Record<string, Stats> {
  const map: Record<string, Stats> = {};
  let entries: string[];
  try {
    entries = fs.readdirSync(STATS_DIR);
  } catch {
    return map;
  }
  for (const entry of entries) {
    const statPath = path.join(STATS_DIR, entry);
    if (!fs.statSync(statPath).isDirectory()) continue;
    const stats = getStats(entry);
    if (stats) map[entry] = stats;
  }
  return map;
}
