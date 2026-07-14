import React, { useEffect, useState } from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card } from "../../ui/Card";
import { Loader } from "lucide-react";
import { api } from "../../../lib/api";
import type { LearningMetrics } from "../../../lib/types";

interface ComparisonData {
  metric: string;
  student: number;
  average: number;
}

interface ComparisonChartProps {
  childId: string;
}

export function ComparisonChart({ childId }: ComparisonChartProps) {
  const [data, setData] = useState<ComparisonData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadComparisonData = async () => {
      try {
        const metrics = await api<LearningMetrics>(`/api/v1/learning/metrics?child_id=${childId}`);

        const comparisonData = [
          {
            metric: "Taxa Sucesso",
            student: Math.round(metrics.overall_success_rate * 100),
            average: 70,
          },
          {
            metric: "Engajamento",
            student: metrics.average_engagement * 20,
            average: 60,
          },
          {
            metric: "Temas Dominados",
            student: metrics.themes_mastered.length * 10,
            average: 40,
          },
          {
            metric: "Consistência",
            student: Math.max(0, 100 - (metrics.dropout_risk === "high" ? 70 : metrics.dropout_risk === "medium" ? 40 : 20)),
            average: 65,
          },
          {
            metric: "Progresso",
            student: Math.round(metrics.predicted_next_success_rate * 100),
            average: 60,
          },
        ];

        setData(comparisonData);
      } catch (err) {
        console.error("Erro ao carregar comparação:", err);
      } finally {
        setLoading(false);
      }
    };

    if (childId) loadComparisonData();
  }, [childId]);

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-80">
          <Loader className="w-6 h-6 animate-spin text-gray-400 mr-2" />
          <span className="text-gray-500">Carregando comparação...</span>
        </div>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center h-80 flex items-center justify-center">
          <p className="text-gray-500">Sem dados para comparação</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="font-semibold text-lg mb-2">Comparação com Média da Turma</h3>
      <p className="text-xs text-gray-500 mb-4">Dados anonimizados para fins de benchmark</p>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="metric" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar
            name="Seu Desempenho"
            dataKey="student"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.6}
          />
          <Radar
            name="Média da Turma"
            dataKey="average"
            stroke="#10b981"
            fill="#10b981"
            fillOpacity={0.3}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
        <p className="font-semibold mb-1">📊 Insight</p>
        <p>
          {data[0].student > data[0].average
            ? "Seu desempenho está acima da média! Continue assim."
            : "Há espaço para melhorias. Foque nos temas com mais dificuldade."}
        </p>
      </div>
    </Card>
  );
}
