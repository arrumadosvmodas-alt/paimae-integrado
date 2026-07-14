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

interface ThemeData {
  theme: string;
  progress: number;
  status: "dominated" | "progressing" | "struggling";
  color: string;
}

interface ThemeProgressChartProps {
  childId: string;
}

export function ThemeProgressChart({ childId }: ThemeProgressChartProps) {
  const [data, setData] = useState<ThemeData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadThemeData = async () => {
      try {
        const metrics = await api<LearningMetrics>(`/api/v1/learning/metrics?child_id=${childId}`);

        const themes: ThemeData[] = [];

        metrics.themes_mastered.forEach((theme) => {
          themes.push({
            theme,
            progress: 85,
            status: "dominated",
            color: "#10b981",
          });
        });

        metrics.themes_in_progress?.forEach((theme) => {
          themes.push({
            theme,
            progress: 55,
            status: "progressing",
            color: "#f59e0b",
          });
        });

        metrics.themes_struggling.forEach((theme) => {
          themes.push({
            theme,
            progress: 30,
            status: "struggling",
            color: "#ef4444",
          });
        });

        setData(themes);
      } catch (err) {
        console.error("Erro ao carregar temas:", err);
      } finally {
        setLoading(false);
      }
    };

    if (childId) loadThemeData();
  }, [childId]);

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <Loader className="w-6 h-6 animate-spin text-gray-400 mr-2" />
          <span className="text-gray-500">Carregando temas...</span>
        </div>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center h-64 flex items-center justify-center">
          <p className="text-gray-500">Sem dados de temas para exibir</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="font-semibold text-lg mb-4">Progresso por Tema</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="theme" angle={-45} textAnchor="end" height={80} />
          <YAxis />
          <Tooltip formatter={(value: number) => `${value}%`} />
          <Bar dataKey="progress" name="Progresso (%)" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-3 mt-6">
        <div className="text-center p-2 bg-green-50 rounded-lg">
          <p className="text-sm font-semibold text-green-900">Dominados</p>
          <p className="text-2xl font-bold text-green-600">{data.filter(d => d.status === "dominated").length}</p>
        </div>
        <div className="text-center p-2 bg-yellow-50 rounded-lg">
          <p className="text-sm font-semibold text-yellow-900">Em Progresso</p>
          <p className="text-2xl font-bold text-yellow-600">{data.filter(d => d.status === "progressing").length}</p>
        </div>
        <div className="text-center p-2 bg-red-50 rounded-lg">
          <p className="text-sm font-semibold text-red-900">Em Dificuldade</p>
          <p className="text-2xl font-bold text-red-600">{data.filter(d => d.status === "struggling").length}</p>
        </div>
      </div>
    </Card>
  );
}
