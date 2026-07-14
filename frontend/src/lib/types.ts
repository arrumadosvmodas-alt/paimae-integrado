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
  is_active?: boolean;
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
  is_active?: boolean;
  document?: string | null;
  first_access_completed?: boolean;
  lgpd_accepted?: boolean;
  lgpd_accepted_at?: string | null;
};

export type PedagogicalMethodology = {
  id: string;
  school_id: string;
  name: string;
  description: string | null;
  is_active?: boolean;
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
  is_active?: boolean;
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
  is_active?: boolean;
};

// ===== FASE B: Upload e Processamento =====
export type PedagogicalMaterialWithProcessing = PedagogicalMaterial & {
  file_url?: string;
  extracted_text?: string;
  ai_analysis?: Record<string, any>;
  processing_status: "pending" | "processing" | "completed" | "failed";
  processing_error?: string;
};

// ===== FASE C: Orquestração =====
export type StudyPlan = {
  id: string;
  child_id: string;
  material_id: string;
  start_date: string;
  end_date?: string;
  ai_generated_plan?: string;
  status: "draft" | "active" | "completed" | "paused";
  daily_items: DailyStudyPlanItem[];
  is_active: boolean;
};

export type DailyStudyPlanItem = {
  id: string;
  study_plan_id: string;
  date: string;
  chapter_or_theme: string;
  activity_description?: string;
  difficulty_level: "easy" | "medium" | "hard";
  estimated_duration_minutes?: number;
  status: "pending" | "in_progress" | "completed" | "skipped";
  is_active: boolean;
};

export type Interaction = {
  id: string;
  child_id: string;
  material_id?: string;
  scheduled_at: string;
  sent_at?: string;
  recipient_type: "child" | "parent";
  message: string;
  context_json?: Record<string, any>;
  status: "scheduled" | "sent" | "read" | "not_sent";
  responses: InteractionResponse[];
  is_active: boolean;
};

export type InteractionResponse = {
  id: string;
  interaction_id: string;
  responder_type: "child" | "parent";
  response_text: string;
  response_score?: number;
  attachment_url?: string;
  responded_at: string;
  ai_evaluation?: string;
  is_active: boolean;
};

// ===== FASE D: Aprendizagem Adaptativa =====
export type LearningProfile = {
  id: string;
  child_id: string;
  visual_preference: number;
  auditory_preference: number;
  kinesthetic_preference: number;
  learning_speed: number;
  confidence_level: number;
  retention_rate: number;
  competencies: Record<string, number>;
  identified_challenges: Record<string, any>;
  engagement_level: number;
  use_adaptive_difficulty: boolean;
  is_active: boolean;
};

export type LearningHistory = {
  id: string;
  child_id: string;
  interaction_id?: string;
  response_id?: string;
  theme: string;
  activity_type: string;
  difficulty_presented: "easy" | "medium" | "hard";
  was_successful: boolean;
  score?: number;
  time_spent_seconds?: number;
  feedback?: string;
  effective_styles: string[];
  activity_date: string;
  is_active: boolean;
};

export type AdaptiveRecommendation = {
  id: string;
  child_id: string;
  learning_profile_id: string;
  recommended_theme: string;
  recommended_difficulty: "easy" | "medium" | "hard";
  recommended_style: string;
  confidence: number;
  reason?: string;
  predicted_success_rate: number;
  risk_of_dropout: number;
  status: "pending" | "applied" | "completed";
  is_active: boolean;
};

export type LearningMetrics = {
  child_id: string;
  profile: LearningProfile;
  total_activities: number;
  successful_activities: number;
  overall_success_rate: number;
  average_engagement: number;
  themes_mastered: string[];
  themes_in_progress: string[];
  themes_struggling: string[];
  predicted_next_success_rate: number;
  dropout_risk: "low" | "medium" | "high";
  recommendations: string[];
};

// ===== Extensão de Types Existentes =====
export type ChildExtended = Child & {
  grade?: string;
  shift?: string;
  preferences?: Record<string, any>;
  difficulties?: Record<string, any>;
  observations?: string;
};

