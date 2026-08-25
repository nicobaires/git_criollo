import type { Stats } from './stats';

export type Granularity = 'day' | 'week' | 'month';

export function getGranularity(repoAgeDays: number): Granularity {
  if (repoAgeDays <= 30) return 'day';
  if (repoAgeDays <= 180) return 'week';
  return 'month';
}

export function getTimelineKeys(stats: Stats, g: Granularity) {
  return {
    day:   { keys: stats.timeline.days,   commits: stats.timeline.commits_by_author_day,   loc: stats.timeline.loc_by_day },
    week:  { keys: stats.timeline.weeks,  commits: stats.timeline.commits_by_author_week,  loc: stats.timeline.loc_by_week },
    month: { keys: stats.timeline.months, commits: stats.timeline.commits_by_author,       loc: stats.timeline.loc_by_month },
  }[g];
}

export function filterByYear<T extends string>(keys: T[], year: number | null): T[] {
  if (!year) return keys;
  return keys.filter(k => parseInt(k.slice(0, 4)) === year);
}

export function filterValues<T>(allKeys: string[], filteredKeys: string[], values: T[]): T[] {
  if (filteredKeys.length === allKeys.length) return values;
  const set = new Set(filteredKeys);
  return allKeys.reduce<T[]>((acc, k, i) => {
    if (set.has(k)) acc.push(values[i]);
    return acc;
  }, []);
}

const PERIOD_NAMES: Record<Granularity, string> = {
  day: 'día',
  week: 'semana',
  month: 'mes',
};

export function getChartTitles(g: Granularity) {
  return {
    chartTitle: `Commits por autor y ${PERIOD_NAMES[g]}`,
    locTitle: `Líneas por ${PERIOD_NAMES[g]}`,
  };
}

export function getTimeRangeLabel(filterYear: number | null, hasMultipleYears: boolean): string {
  if (filterYear) return ` (${filterYear})`;
  if (hasMultipleYears) return ' (todos los años)';
  return '';
}

export interface TimelineData {
  labels: string[];
  commitsSeries: Record<string, number[]>;
  locLabels: string[];
  locAdded: number[];
  locDeleted: number[];
}

export function getTimelineData(stats: Stats, g: Granularity, filterYear: number | null): TimelineData {
  const t = getTimelineKeys(stats, g);
  const fKeys = filterByYear(t.keys, filterYear);

  return {
    labels: fKeys,
    commitsSeries: t.commits,
    locLabels: fKeys,
    locAdded: filterValues(t.keys, fKeys, t.loc.added),
    locDeleted: filterValues(t.keys, fKeys, t.loc.deleted),
  };
}

export function computeYearKpis(stats: Stats, year: number | null, g: Granularity) {
  if (!year) return stats.kpis;

  const t = getTimelineKeys(stats, g);
  let yCommits = 0, yAdded = 0, yDeleted = 0;

  const fKeys = filterByYear(t.keys, year);

  for (const [author, values] of Object.entries(t.commits)) {
    const filtered = filterValues(t.keys, fKeys, values);
    yCommits += filtered.reduce((s, v) => s + v, 0);
  }

  for (let i = 0; i < t.keys.length; i++) {
    if (parseInt(t.keys[i].slice(0, 4)) === year) {
      yAdded += t.loc.added[i];
      yDeleted += t.loc.deleted[i];
    }
  }

  return {
    total_commits: yCommits,
    total_authors: stats.kpis.total_authors,
    total_added: yAdded,
    total_deleted: yDeleted,
    total_changes: yAdded + yDeleted,
  };
}
