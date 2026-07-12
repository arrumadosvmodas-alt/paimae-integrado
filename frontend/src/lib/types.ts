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

