// types.ts
export interface Activity {
  recommendation: string;
  importance: string;
  recommendation_reason: string;
  benefit: string;
  impact_of_not_doing: string;
  frequency: string;
  source: string;
  recommendation_short_str: string;
  frequency_short_str: string;
}

export interface ActivityItem {
  activity: Activity;
  status: Status;
  next_step_recommendation: string | null;
  supporting_evidence: string;
  user_input_questions: string[] | null;
}

export interface Category {
  category_name: string;
  activities: ActivityItem[];
}

export interface HealthRecommendations {
  categories: Category[];
  assessment_date: string;
}

export type Status =
  | 'Completed'
  | 'Needs user confirmation'
  | 'Partially completed'
  | 'Not started';
