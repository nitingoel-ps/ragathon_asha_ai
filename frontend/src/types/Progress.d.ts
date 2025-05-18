export interface Progress {
  overallProgress: number;
  categoryProgress: Record<string, CategoryProgress>;
}

export interface CategoryProgress {
  progress: number;
  totalActivities: number;
}
