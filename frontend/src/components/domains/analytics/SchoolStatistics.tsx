import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Card } from "../../ui/Card";
import { Loader, School } from "lucide-react";
import { api } from "../../../lib/api";

interface SchoolStats {
  totalStudents: number;
  averageSuccessRate: number;
  averageEngagement: number;
  dropoutRiskDistribution: { level: string; count: number; color: string }[];
  topThemes: { name: string; mastered: number }[];
  weeklyProgress: { week: string; successRate: number }[];
}

interface SchoolStatisticsProps {
  schoolId?: string;
}

export function SchoolStatistics({ schoolId }: SchoolStatisticsProps) {
  const [stats, setStats] = useState<SchoolStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        // Simular dados agregados (em produção, viria de um endpoint específico)
        const children = await api<any[]>("/api/v1/children");

        if (children.length === 0) {
          setStats(null);
          return;
        }

        // Simular estatísticas agregadas
        const aggregatedStats: SchoolStats = {
          totalStudents: children.length,
          averageSuccessRate: 0.72,
          averageEngagement: 4.2,
          dropoutRiskDistribution: [
            { level: "Baixo", count: Math.floor(children.length * 0.6), color: "#10b981" },
            { level: "Médio", count: Math.floor(children.length * 0.25), color: "#f59e0b" },
            { level: "Alto", count: Math.floor(children.length * 0.15), color: "#ef4444" },
          ],
          topThemes: [
            { name: "Português", mastered: children.length * 0.8 },
            { name: "Matemática", mastered: children.length * 0.65 },
            { name: "Ciências", mastered: children.length * 0.55 },
            { name: "Artes", mastered: children.length * 0.45 },
          ],
          weeklyProgress: [
            { week: "Sem. 1", successRate: 68 },
            { week: "Sem. 2", successRate: 70 },
            { week: "Sem. 3", successRate: 71 },
            { week: "Sem. 4", successRate: 72 },
          ],
        };

        setStats(aggregatedStats);
      } catch (err) {
        console.error("Erro ao carregar estatísticas:", err);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, [schoolId]);

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <Loader className="w-6 h-6 animate-spin text-gray-400 mr-2" />
          <span className="text-gray-500">Carregando estatísticas...</span>
        </div>
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card className="p-6">
        <div className="text-center h-64 flex items-center justify-center">
          <p className="text-gray-500">Sem dados para exibir</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Métricas Principais */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Total de Alunos</span>
            <School className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-600">{stats.totalStudents}</p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Taxa Média Sucesso</span>
          </div>
          <p className="text-3xl font-bold text-green-600">
            {Math.round(stats.averageSuccessRate * 100)}%
          </p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Engajamento Médio</span>
          </div>
          <p className="text-3xl font-bold text-yellow-600">{stats.averageEngagement.toFixed(1)}/5</p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Risco Baixo</span>
          </div>
          <p className="text-3xl font-bold text-purple-600">
            {Math.round(
              (stats.dropoutRiskDistribution[0].count / stats.totalStudents) * 100
            )}%
          </p>
        </Card>
      </div>

      {/* Progresso Semanal */}
      <Card className="p-6">
        <h3 className="font-semibold text-lg mb-4">Evolução Semanal da Taxa de Sucesso</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={stats.weeklyProgress}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis domain={[0, 100]} />
            <Tooltip formatter={(value: number) => `${value}%`} />
            <Line
              type="monotone"
              dataKey="successRate"
              stroke="#3b82f6"
              name="Taxa de Sucesso (%)"
              isAnimationActive
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Grid de Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribuição de Risco */}
        <Card className="p-6">
          <h3 className="font-semibold text-lg mb-4">Distribuição de Risco de Dropout</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={stats.dropoutRiskDistribution}
                dataKey="count"
                nameKey="level"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {stats.dropoutRiskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Temas Dominados */}
        <Card className="p-6">
          <h3 className="font-semibold text-lg mb-4">Temas Mais Dominados</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={stats.topThemes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="mastered" name="Alunos" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Resumo */}
      <Card className="p-4 bg-blue-50 border-blue-200">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">📊 Insight:</span> A turma está com bom desempenho geral,
          com taxa de sucesso em torno de {Math.round(stats.averageSuccessRate * 100)}%. Foque em alunos com risco alto
          de dropout.
        </p>
      </Card>
    </div>
  );
}
