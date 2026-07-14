import React, { useEffect, useState } from "react";
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Eye,
  Ear,
  Zap,
  Target,
  Loader,
} from "lucide-react";
import { Card } from "../../ui/Card";
import { Button } from "../../ui/Button";
import {
  getLearningMetrics,
  predictDropoutRisk,
  generateAdaptiveRecommendation,
} from "../../../services/apiServices";
import type { LearningMetrics, AdaptiveRecommendation } from "../../../lib/types";

interface LearningAnalyticsProps {
  childId: string;
  availableThemes?: string[];
}

export function LearningAnalytics({
  childId,
  availableThemes = ["Português", "Matemática", "Ciências", "Artes"],
}: LearningAnalyticsProps) {
  const [metrics, setMetrics] = useState<LearningMetrics | null>(null);
  const [recommendation, setRecommendation] = useState<AdaptiveRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generatingRec, setGeneratingRec] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const metricsData = await getLearningMetrics(childId);
        setMetrics(metricsData);

        // Try to load existing recommendation
        const recData = await generateAdaptiveRecommendation(childId, availableThemes);
        setRecommendation(recData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar análise");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [childId, availableThemes]);

  const handleNewRecommendation = async () => {
    setGeneratingRec(true);
    try {
      const recData = await generateAdaptiveRecommendation(childId, availableThemes);
      setRecommendation(recData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar recomendação");
    } finally {
      setGeneratingRec(false);
    }
  };

  if (loading) {
    return <div className="text-center text-gray-500">Carregando análise...</div>;
  }

  if (error) {
    return (
      <Card className="p-4 border-red-200 bg-red-50">
        <p className="text-red-700">{error}</p>
      </Card>
    );
  }

  if (!metrics) {
    return <div className="text-center text-gray-500">Sem dados de aprendizagem</div>;
  }

  const riskLevel = metrics.dropout_risk;
  const successRate = Math.round(metrics.overall_success_rate * 100);

  return (
    <div className="space-y-4">
      {/* Métricas Principais */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Taxa de Sucesso</span>
            <BarChart3 className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-3xl font-bold text-blue-600">{successRate}%</div>
          <p className="text-xs text-gray-500 mt-1">
            {metrics.successful_activities}/{metrics.total_activities} atividades
          </p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Engajamento</span>
            <Zap className="w-4 h-4 text-yellow-600" />
          </div>
          <div className="text-3xl font-bold text-yellow-600">{metrics.average_engagement}/5</div>
          <p className="text-xs text-gray-500 mt-1">Nível de interesse</p>
        </Card>

        <Card
          className={`p-4 ${
            riskLevel === "high" ? "border-red-200 bg-red-50" : "border-green-200 bg-green-50"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Risco de Dropout</span>
            {riskLevel === "high" ? (
              <AlertTriangle className="w-4 h-4 text-red-600" />
            ) : (
              <CheckCircle className="w-4 h-4 text-green-600" />
            )}
          </div>
          <div className={`text-2xl font-bold ${riskLevel === "high" ? "text-red-600" : "text-green-600"}`}>
            {riskLevel === "high" ? "Alto" : riskLevel === "medium" ? "Médio" : "Baixo"}
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Próximo Sucesso</span>
            <Target className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-3xl font-bold text-purple-600">
            {Math.round(metrics.predicted_next_success_rate * 100)}%
          </div>
          <p className="text-xs text-gray-500 mt-1">Predição IA</p>
        </Card>
      </div>

      {/* Estilos de Aprendizagem */}
      {metrics.profile && (
        <Card className="p-4">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Eye className="w-4 h-4" />
            Estilos de Aprendizagem
          </h3>
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  <Eye className="w-3 h-3" />
                  Visual
                </span>
                <span className="text-sm font-semibold">
                  {Math.round(metrics.profile.visual_preference * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${metrics.profile.visual_preference * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  <Ear className="w-3 h-3" />
                  Auditivo
                </span>
                <span className="text-sm font-semibold">
                  {Math.round(metrics.profile.auditory_preference * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${metrics.profile.auditory_preference * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  <Zap className="w-3 h-3" />
                  Cinestésico
                </span>
                <span className="text-sm font-semibold">
                  {Math.round(metrics.profile.kinesthetic_preference * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-500 h-2 rounded-full"
                  style={{ width: `${metrics.profile.kinesthetic_preference * 100}%` }}
                />
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Temas */}
      <div className="grid grid-cols-2 gap-4">
        {metrics.themes_mastered.length > 0 && (
          <Card className="p-4 border-green-200 bg-green-50">
            <h3 className="font-semibold text-sm text-green-900 mb-2">Dominou</h3>
            <div className="space-y-1">
              {metrics.themes_mastered.map((theme) => (
                <p key={theme} className="text-xs text-green-800">
                  ✓ {theme}
                </p>
              ))}
            </div>
          </Card>
        )}

        {metrics.themes_struggling.length > 0 && (
          <Card className="p-4 border-red-200 bg-red-50">
            <h3 className="font-semibold text-sm text-red-900 mb-2">Em Dificuldade</h3>
            <div className="space-y-1">
              {metrics.themes_struggling.map((theme) => (
                <p key={theme} className="text-xs text-red-800">
                  ⚠ {theme}
                </p>
              ))}
            </div>
          </Card>
        )}
      </div>

      {/* Recomendação Adaptativa */}
      {recommendation && (
        <Card className="p-4 border-blue-200 bg-blue-50">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
            <Target className="w-4 h-4" />
            Recomendação Inteligente
          </h3>
          <div className="space-y-2 text-sm">
            <p>
              <span className="font-semibold">Próximo tema:</span> {recommendation.recommended_theme}
            </p>
            <p>
              <span className="font-semibold">Dificuldade:</span>{" "}
              {recommendation.recommended_difficulty === "easy"
                ? "Fácil (reforço)"
                : recommendation.recommended_difficulty === "medium"
                  ? "Médio (normal)"
                  : "Difícil (desafio)"}
            </p>
            <p>
              <span className="font-semibold">Estilo:</span> {recommendation.recommended_style}
            </p>
            <p>
              <span className="font-semibold">Chance de sucesso:</span>{" "}
              {Math.round(recommendation.predicted_success_rate * 100)}%
            </p>
            {recommendation.reason && (
              <p className="text-xs text-blue-800 italic mt-2">"{recommendation.reason}"</p>
            )}
          </div>
        </Card>
      )}

      {/* Recomendações */}
      {metrics.recommendations.length > 0 && (
        <Card className="p-4">
          <h3 className="font-semibold mb-2">Sugestões do Sistema</h3>
          <ul className="space-y-1">
            {metrics.recommendations.map((rec, i) => (
              <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-yellow-600 mt-1">💡</span>
                {rec}
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Button
        onClick={handleNewRecommendation}
        disabled={generatingRec}
        variant="primary"
        className="w-full"
      >
        {generatingRec ? (
          <>
            <Loader className="w-4 h-4 animate-spin" />
            Gerando recomendação...
          </>
        ) : (
          "Gerar Nova Recomendação"
        )}
      </Button>
    </div>
  );
}
