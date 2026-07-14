import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card } from "../../ui/Card";
import { Loader } from "lucide-react";
import { api } from "../../../lib/api";

interface ProgressDataPoint {
  date: string;
  successRate: number;
  engagement: number;
  dropoutRisk: number;
}

interface ProgressChartProps {
  childId: string;
  days?: number;
}

export function ProgressChart({ childId, days = 30 }: ProgressChartProps) {
  const [data, setData] = useState<ProgressDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProgressData = async () => {
      try {
        const history = await api<any[]>(`/api/v1/learning/history?child_id=${childId}&limit=${days}`);

        const progressData = history
          .sort((a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime())
          .map((item) => ({
            date: new Date(item.recorded_at).toLocaleDateString("pt-BR"),
            successRate: (item.success_score || 0) * 100,
            engagement: (item.engagement_score || 0) * 5,
            dropoutRisk: item.dropout_risk_score ? (item.dropout_risk_score * 100) : 0,
          }));

        setData(progressData);
      } catch (err) {
        console.error("Erro ao carregar progresso:", err);
      } finally {
        setLoading(false);
      }
    };

    if (childId) loadProgressData();
  }, [childId, days]);

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-80">
          <Loader className="w-6 h-6 animate-spin text-gray-400 mr-2" />
          <span className="text-gray-500">Carregando gráfico...</span>
        </div>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center h-80 flex items-center justify-center">
          <p className="text-gray-500">Sem dados de progresso para exibir</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="font-semibold text-lg mb-4">Progresso ao Longo do Tempo</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip
            formatter={(value: number) => value.toFixed(1)}
            labelFormatter={(label) => `Data: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="successRate"
            stroke="#3b82f6"
            name="Taxa de Sucesso (%)"
            isAnimationActive
          />
          <Line
            type="monotone"
            dataKey="engagement"
            stroke="#10b981"
            name="Engajamento (1-5)"
            isAnimationActive
          />
          <Line
            type="monotone"
            dataKey="dropoutRisk"
            stroke="#ef4444"
            name="Risco de Dropout (%)"
            isAnimationActive
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
