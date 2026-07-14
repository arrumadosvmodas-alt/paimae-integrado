import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card } from "../../ui/Card";
import { Loader } from "lucide-react";
import { api } from "../../../lib/api";
import type { LearningMetrics } from "../../../lib/types";

interface LearningStyleChartProps {
  childId: string;
}

export function LearningStyleChart({ childId }: LearningStyleChartProps) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStyleData = async () => {
      try {
        const metrics = await api<LearningMetrics>(`/api/v1/learning/metrics?child_id=${childId}`);

        if (metrics.profile) {
          const styleData = [
            {
              name: "Visual",
              percentage: Math.round(metrics.profile.visual_preference * 100),
              color: "#3b82f6",
            },
            {
              name: "Auditivo",
              percentage: Math.round(metrics.profile.auditory_preference * 100),
              color: "#10b981",
            },
            {
              name: "Cinestésico",
              percentage: Math.round(metrics.profile.kinesthetic_preference * 100),
              color: "#f59e0b",
            },
          ];
          setData(styleData);
        }
      } catch (err) {
        console.error("Erro ao carregar estilos:", err);
      } finally {
        setLoading(false);
      }
    };

    if (childId) loadStyleData();
  }, [childId]);

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <Loader className="w-6 h-6 animate-spin text-gray-400 mr-2" />
          <span className="text-gray-500">Carregando estilos...</span>
        </div>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center h-64 flex items-center justify-center">
          <p className="text-gray-500">Sem dados de estilos para exibir</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="font-semibold text-lg mb-4">Estilos de Aprendizagem</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip formatter={(value: number) => `${value}%`} />
          <Legend />
          <Bar dataKey="percentage" name="Preferência (%)" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
