export type School = {
  id: string;
  name: string;
  document: string | null;
  is_active: boolean;
};

export type Child = {
  id: string;
  full_name: string;
  birth_date: string | null;
  school_id: string;
  class_name: string | null;
};

export type Routine = {
  id: string;
  child_id: string;
  title: string;
  description: string | null;
  scheduled_time: string;
  weekdays: number[];
  target_audience: string;
};

export type Notification = {
  id: string;
  child_id: string;
  title: string;
  message: string | null;
  scheduled_at: string;
  status: string;
};

export type Task = {
  id: string;
  child_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  status: string;
};

export type EvolutionEvent = {
  id: string;
  child_id: string;
  event_type: string;
  occurred_at: string;
  score: number | null;
  notes: string | null;
};

export type User = {
  id: string;
  name: string;
  email: string;
  role: string;
  school_id: string | null;
};

export type PedagogicalMethodology = {
  id: string;
  school_id: string;
  name: string;
  description: string | null;
};

export type MaterialItem = {
  id: string;
  material_id: string;
  chapter: string | null;
  page: string | null;
  theme: string;
  description: string | null;
};

export type PedagogicalMaterial = {
  id: string;
  school_id: string;
  title: string;
  author: string | null;
  isbn: string | null;
  subject: string;
  pedagogical_line: string;
  objectives: string | null;
  family_orientation: string | null;
  items: MaterialItem[];
};

export type FamilyInteractionSuggestion = {
  id: string;
  daily_record_id: string;
  suggestion_text: string;
};

export type DailySchoolRecord = {
  id: string;
  child_id: string;
  date: string;
  summary: string;
  observed_skills: string | null;
  engagement_score: number | null;
  suggestions: FamilyInteractionSuggestion[];
};


