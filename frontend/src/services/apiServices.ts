import { api } from "../lib/api";
import type {
  StudyPlan,
  DailyStudyPlanItem,
  Interaction,
  InteractionResponse,
  LearningProfile,
  LearningHistory,
  AdaptiveRecommendation,
  LearningMetrics,
  PedagogicalMaterialWithProcessing,
  SchoolSchedule,
  ScheduleGenerationResult,
} from "../lib/types";

// ===== FASE B: Material Processing =====

export async function uploadBookFile(
  materialId: string,
  file: File
): Promise<{ status: string; message: string; material_id: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/materials/${materialId}/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("paimae.token")}`,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Erro ao fazer upload do arquivo");
  }

  return response.json();
}

export async function getMaterialProcessingStatus(
  materialId: string
): Promise<PedagogicalMaterialWithProcessing> {
  return api(`/api/v1/materials/${materialId}/processing-status`);
}

export async function generateStudyPlan(
  materialId: string,
  childId: string
): Promise<{ status: string; message: string; study_plan: string }> {
  return api(`/api/v1/materials/${materialId}/generate-study-plan?child_id=${childId}`, {
    method: "POST",
  });
}

export async function generateInteraction(
  materialId: string,
  childId: string,
  chapter: string,
  theme: string,
  recipientType: "child" | "parent"
): Promise<{ status: string; message: string; interaction: string }> {
  return api(
    `/api/v1/materials/${materialId}/generate-interaction?child_id=${childId}&chapter=${encodeURIComponent(chapter)}&theme=${encodeURIComponent(theme)}&recipient_type=${recipientType}`,
    {
      method: "POST",
    }
  );
}


// ===== CRONOGRAMA PEDAGOGICO =====

export async function getSchoolSchedules(childId: string): Promise<SchoolSchedule[]> {
  return api(`/api/v1/pedagogy/school-schedules?child_id=${childId}`);
}

export async function createSchoolSchedule(data: {
  child_id: string;
  school_id: string;
  date: string;
  subject: string;
  topic?: string | null;
  material_id?: string | null;
  chapter?: string | null;
  page_start?: number | null;
  page_end?: number | null;
  source?: "manual" | "pdf" | "image" | "ocr" | "fallback";
  source_file_url?: string | null;
  confidence_score?: number | null;
  fallback_used?: boolean;
  status?: "planned" | "confirmed" | "completed" | "skipped";
}): Promise<SchoolSchedule> {
  return api("/api/v1/pedagogy/school-schedules", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateSchoolSchedule(
  scheduleId: string,
  data: {
    date: string;
    subject: string;
    topic?: string | null;
    material_id?: string | null;
    chapter?: string | null;
    page_start?: number | null;
    page_end?: number | null;
    source?: "manual" | "pdf" | "image" | "ocr" | "fallback";
    source_file_url?: string | null;
    confidence_score?: number | null;
    fallback_used?: boolean;
    status?: "planned" | "confirmed" | "completed" | "skipped";
  }
): Promise<SchoolSchedule> {
  return api(`/api/v1/pedagogy/school-schedules/${scheduleId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function generateScheduleActivities(scheduleId: string): Promise<ScheduleGenerationResult> {
  return api(`/api/v1/orchestration/school-schedules/${scheduleId}/generate-daily-activities`, {
    method: "POST",
  });
}

// ===== CLIPESCOLA (integracao pessoal do responsavel) =====

export type ClipEscolaStatus = {
  account_id: string | null;
  status: "not_configured" | "pending_pairing" | "active" | "needs_reauth";
  last_synced_at: string | null;
  qr_image_base64?: string | null;
};

export async function getClipEscolaStatus(childId: string): Promise<ClipEscolaStatus> {
  return api(`/api/v1/clip-escola/${childId}`);
}

export async function startClipEscolaPairing(childId: string): Promise<{ account_id: string; qr_image_base64: string }> {
  return api(`/api/v1/clip-escola/${childId}/pair/start`, { method: "POST" });
}

export async function getClipEscolaPairingStatus(childId: string): Promise<ClipEscolaStatus> {
  return api(`/api/v1/clip-escola/${childId}/pair/status`);
}

export async function syncClipEscolaNow(childId: string): Promise<{ status: string; schedules_created: number; clips_read: number; message?: string }> {
  return api(`/api/v1/clip-escola/${childId}/sync`, { method: "POST" });
}

export type ClipEscolaDateLookupEntry = {
  subject: string;
  topic?: string | null;
  book?: string | null;
  page_start?: number | null;
  page_end?: number | null;
  date: string;
  confidence?: number;
};

export async function lookupClipEscolaDate(
  childId: string,
  date: string
): Promise<{
  status: "success" | "not_found" | "needs_reauth";
  date?: string;
  schedules_created: number;
  raw_text?: string | null;
  entries?: ClipEscolaDateLookupEntry[] | null;
  message?: string;
}> {
  return api(`/api/v1/clip-escola/${childId}/lookup-date`, {
    method: "POST",
    body: JSON.stringify({ date }),
  });
}

export async function disconnectClipEscola(childId: string): Promise<{ message: string }> {
  return api(`/api/v1/clip-escola/${childId}`, { method: "DELETE" });
}

// ===== FASE C: Orquestração =====

export async function createStudyPlan(data: {
  child_id: string;
  material_id: string;
  start_date: string;
  end_date?: string;
  ai_generated_plan?: string;
  daily_items?: DailyStudyPlanItem[];
}): Promise<StudyPlan> {
  return api("/api/v1/study-plans", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getStudyPlans(childId?: string): Promise<StudyPlan[]> {
  const query = childId ? `?child_id=${childId}` : "";
  return api(`/api/v1/study-plans${query}`);
}

export async function getStudyPlan(planId: string): Promise<StudyPlan> {
  return api(`/api/v1/study-plans/${planId}`);
}

export async function updateStudyPlan(
  planId: string,
  data: Partial<StudyPlan>
): Promise<StudyPlan> {
  return api(`/api/v1/study-plans/${planId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteStudyPlan(planId: string): Promise<void> {
  return api(`/api/v1/study-plans/${planId}`, {
    method: "DELETE",
  });
}

export async function activateStudyPlan(
  planId: string,
  activate: boolean = true
): Promise<{ status: string; message: string; study_plan_id: string }> {
  return api(`/api/v1/orchestration/study-plans/${planId}/activate?activate=${activate}`, {
    method: "POST",
  });
}

export async function createInteraction(data: {
  child_id: string;
  material_id?: string;
  scheduled_at: string;
  recipient_type: "child" | "parent";
  message: string;
  context_json?: Record<string, any>;
}): Promise<Interaction> {
  return api("/api/v1/study-plans/interactions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getInteractions(childId?: string): Promise<Interaction[]> {
  const query = childId ? `?child_id=${childId}` : "";
  return api(`/api/v1/study-plans/interactions${query}`);
}

export async function getPendingInteractions(limit: number = 10): Promise<Interaction[]> {
  return api(`/api/v1/orchestration/interactions/pending?limit=${limit}`);
}

export async function dispatchInteraction(interactionId: string): Promise<{
  status: string;
  message: string;
  interaction_id: string;
}> {
  return api(`/api/v1/orchestration/interactions/${interactionId}/dispatch`, {
    method: "POST",
  });
}

export async function createInteractionResponse(
  interactionId: string,
  data: {
    responder_type: "child" | "parent";
    response_text: string;
    response_score?: number;
    attachment_url?: string;
    responded_at: string;
  }
): Promise<InteractionResponse> {
  return api(`/api/v1/study-plans/interactions/${interactionId}/responses`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getInteractionResponses(interactionId: string): Promise<InteractionResponse[]> {
  return api(`/api/v1/study-plans/interactions/${interactionId}/responses`);
}

export async function evaluateResponse(
  interactionId: string,
  responseId: string,
  autoEvaluate: boolean = true
): Promise<{ status: string; message: string; ai_evaluation?: string; score?: number }> {
  return api(
    `/api/v1/orchestration/interactions/${interactionId}/responses/${responseId}/evaluate?auto_evaluate=${autoEvaluate}`,
    {
      method: "POST",
    }
  );
}

// ===== FASE D: Aprendizagem Adaptativa =====

export async function getLearningProfile(childId: string): Promise<LearningProfile> {
  return api(`/api/v1/learning/children/${childId}/learning-profile`);
}

export async function updateLearningProfile(
  childId: string,
  data: Partial<LearningProfile>
): Promise<LearningProfile> {
  return api(`/api/v1/learning/children/${childId}/learning-profile`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function recordLearningAttempt(
  childId: string,
  data: {
    theme: string;
    activity_type: string;
    difficulty_presented: "easy" | "medium" | "hard";
    was_successful: boolean;
    score?: number;
    time_spent_seconds?: number;
    feedback?: string;
    effective_styles?: string[];
    activity_date: string;
  }
): Promise<LearningHistory> {
  return api(`/api/v1/learning/children/${childId}/learning-history`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getLearningHistory(childId: string, limit: number = 50): Promise<LearningHistory[]> {
  return api(`/api/v1/learning/children/${childId}/learning-history?limit=${limit}`);
}

export async function getLearningMetrics(childId: string): Promise<LearningMetrics> {
  return api(`/api/v1/learning/children/${childId}/metrics`);
}

export async function generateAdaptiveRecommendation(
  childId: string,
  availableThemes?: string[]
): Promise<AdaptiveRecommendation> {
  const query = availableThemes ? `?available_themes=${availableThemes.join(",")}` : "";
  return api(`/api/v1/learning/children/${childId}/adaptive-recommendation${query}`, {
    method: "POST",
  });
}

export async function getAdaptiveRecommendations(
  childId: string,
  status: string = "pending"
): Promise<AdaptiveRecommendation[]> {
  return api(`/api/v1/learning/children/${childId}/adaptive-recommendations?status=${status}`);
}

export async function predictSuccess(
  childId: string,
  theme: string,
  difficulty: "easy" | "medium" | "hard" = "medium"
): Promise<{
  child_id: string;
  theme: string;
  difficulty: string;
  predicted_success_rate: number;
  confidence: string;
  recommendation: string;
}> {
  return api(
    `/api/v1/learning/children/${childId}/success-prediction?theme=${encodeURIComponent(theme)}&difficulty=${difficulty}`
  );
}

export async function predictDropoutRisk(childId: string): Promise<{
  child_id: string;
  dropout_risk_score: number;
  risk_level: "low" | "medium" | "high";
  interventions: string[];
}> {
  return api(`/api/v1/learning/children/${childId}/dropout-risk`);
}

export async function getPersonalizedFeedback(
  childId: string,
  responseScore: number,
  theme: string
): Promise<{
  child_id: string;
  theme: string;
  score: number;
  feedback: string;
}> {
  return api(
    `/api/v1/learning/children/${childId}/personalized-feedback?response_score=${responseScore}&theme=${encodeURIComponent(theme)}`
  );
}

export async function getSchedulerStatus(): Promise<{
  status: string;
  message: string;
  jobs_count: number;
  jobs: Array<{
    id: string;
    name: string;
    next_run_time: string;
    trigger: string;
  }>;
}> {
  return api("/api/v1/orchestration/scheduler/status");
}
