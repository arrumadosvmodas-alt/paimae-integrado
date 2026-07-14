import React, { useEffect, useState } from "react";
import { BookOpen, Calendar, Clock, TrendingUp, Zap } from "lucide-react";
import { Card } from "../../ui/Card";
import { Button } from "../../ui/Button";
import { getStudyPlan, activateStudyPlan } from "../../../services/apiServices";
import type { StudyPlan } from "../../../lib/types";

interface StudyPlanViewProps {
  planId: string;
  onStatusChange?: (status: string) => void;
}

export function StudyPlanView({ planId, onStatusChange }: StudyPlanViewProps) {
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isActivating, setIsActivating] = useState(false);

  useEffect(() => {
    const loadPlan = async () => {
      try {
        const data = await getStudyPlan(planId);
        setPlan(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar plano");
      } finally {
        setLoading(false);
      }
    };

    loadPlan();
  }, [planId]);

  const handleActivate = async () => {
    if (!plan) return;

    setIsActivating(true);
    try {
      await activateStudyPlan(planId, true);
      setPlan({ ...plan, status: "active" });
      onStatusChange?.("active");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao ativar plano");
    } finally {
      setIsActivating(false);
    }
  };

  if (loading) {
    return <div className="text-center text-gray-500">Carregando plano...</div>;
  }

  if (error) {
    return (
      <Card className="p-4 border-red-200 bg-red-50">
        <p className="text-red-700">{error}</p>
      </Card>
    );
  }

  if (!plan) {
    return <div className="text-center text-gray-500">Plano não encontrado</div>;
  }

  const statusColors = {
    draft: "bg-gray-100 text-gray-700",
    active: "bg-green-100 text-green-700",
    completed: "bg-blue-100 text-blue-700",
    paused: "bg-yellow-100 text-yellow-700",
  };

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <BookOpen className="w-6 h-6 text-blue-600" />
              Plano de Estudos
            </h2>
            <p className="text-gray-600 text-sm mt-1">{plan.daily_items?.length || 0} atividades planejadas</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[plan.status]}`}>
            {plan.status.charAt(0).toUpperCase() + plan.status.slice(1)}
          </span>
        </div>

        {plan.ai_generated_plan && (
          <div className="bg-blue-50 p-4 rounded-lg mb-4">
            <p className="text-sm text-blue-900 whitespace-pre-wrap">{plan.ai_generated_plan}</p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="w-4 h-4 text-gray-500" />
            <span className="text-gray-700">
              Início: {new Date(plan.start_date).toLocaleDateString("pt-BR")}
            </span>
          </div>
          {plan.end_date && (
            <div className="flex items-center gap-2 text-sm">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">
                Fim: {new Date(plan.end_date).toLocaleDateString("pt-BR")}
              </span>
            </div>
          )}
        </div>

        {plan.status === "draft" && (
          <Button onClick={handleActivate} disabled={isActivating} variant="primary" className="w-full">
            {isActivating ? "Ativando..." : "Ativar Plano (Iniciar Interações Automáticas)"}
          </Button>
        )}
      </Card>

      <div className="space-y-2">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          <Zap className="w-5 h-5 text-yellow-600" />
          Atividades Planejadas
        </h3>
        {plan.daily_items && plan.daily_items.length > 0 ? (
          <div className="grid gap-2">
            {plan.daily_items.map((item) => (
              <Card key={item.id} className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-gray-800">{item.chapter_or_theme}</h4>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      item.difficulty_level === "easy"
                        ? "bg-green-100 text-green-700"
                        : item.difficulty_level === "medium"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-700"
                    }`}
                  >
                    {item.difficulty_level === "easy"
                      ? "Fácil"
                      : item.difficulty_level === "medium"
                        ? "Médio"
                        : "Difícil"}
                  </span>
                </div>

                {item.activity_description && (
                  <p className="text-sm text-gray-600 mb-2">{item.activity_description}</p>
                )}

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(item.date).toLocaleDateString("pt-BR")}
                  </div>
                  {item.estimated_duration_minutes && (
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.estimated_duration_minutes} min
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {item.status === "completed"
                      ? "Concluído"
                      : item.status === "in_progress"
                        ? "Em progresso"
                        : "Pendente"}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">Nenhuma atividade planejada ainda</p>
        )}
      </div>
    </div>
  );
}
