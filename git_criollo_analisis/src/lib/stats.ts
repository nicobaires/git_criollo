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
    commits_by_author: Record<string, number[]>;
    loc_by_month: { months: string[]; added: number[]; deleted: number[] };
  };
  hot_files: { path: string; changes: number }[];
  heatmap: { date: string; count: number }[];
  distribution: { author: string; commits: number; percentage: number }[];
}

const STATS_DIR = path.join(findProjectRoot(), "src", "data", "stats");

export function getStats(repoName: string): Stats | null {
  const file = path.join(STATS_DIR, `${repoName}.json`);
  try {
    return JSON.parse(fs.readFileSync(file, "utf-8")) as Stats;
  } catch {
    return null;
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
    if (!entry.endsWith(".json")) continue;
    const name = path.basename(entry, ".json");
    const stats = getStats(name);
    if (stats) map[name] = stats;
  }
  return map;
}