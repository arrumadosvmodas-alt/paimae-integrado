import React, { useEffect, useState } from "react";
import { Card } from "../../ui/Card";
import { Badge } from "../../ui/Badge";
import { Button } from "../../ui/Button";
import { api } from "../../../lib/api";
import {
  TrendingUp,
  Award,
  BookOpen,
  Calendar,
  CheckCircle,
  Clock,
  Printer,
  Sparkles,
} from "lucide-react";

interface MetricsDashboardProps {
  childId: string;
}

interface TaskStats {
  total: number;
  completed: number;
  pending: number;
  completion_rate: number;
}

interface EngagementEntry {
  date: string;
  score: number;
  type: string;
}

interface SubjectEntry {
  subject: string;
  count: number;
}

interface MetricsData {
  task_stats: TaskStats;
  engagement_history: EngagementEntry[];
  subject_distribution: SubjectEntry[];
}

export function MetricsDashboard({ childId }: MetricsDashboardProps) {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!childId) return;

    async function fetchMetrics() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api<MetricsData>(`/api/v1/reports/metrics?child_id=${childId}`);
        setMetrics(data);
      } catch (err) {
        setError("Não foi possível carregar as métricas deste aluno.");
      } finally {
        setIsLoading(false);
      }
    }

    fetchMetrics();
  }, [childId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-semibold text-text-muted">Calculando métricas pedagógicas...</p>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <Card title="Relatório e Métricas" icon={<TrendingUp className="w-5 h-5 text-primary" />}>
        <div className="text-center py-10 text-error text-xs font-semibold">
          {error || "Selecione um aluno para visualizar as métricas."}
        </div>
      </Card>
    );
  }

  const { task_stats, engagement_history, subject_distribution } = metrics;

  // Calcula engajamento médio
  const avgEngagement =
    engagement_history.length > 0
      ? (
          engagement_history.reduce((acc, entry) => acc + entry.score, 0) /
          engagement_history.length
        ).toFixed(1)
      : "N/A";

  // Gera o gráfico de evolução do engajamento usando SVG
  const renderSVGChart = () => {
    if (engagement_history.length === 0) {
      return (
        <div className="text-center py-10 text-xs text-text-muted">
          Histórico comportamental insuficiente para gerar o gráfico.
        </div>
      );
    }

    const width = 600;
    const height = 150;
    const padding = 20;

    // Mapeamento dos pontos
    const xStep =
      engagement_history.length > 1
        ? (width - padding * 2) / (engagement_history.length - 1)
        : width - padding * 2;

    const points = engagement_history.map((entry, idx) => {
      const x = padding + idx * xStep;
      // Inverte o eixo Y pois no SVG o topo é Y=0. O score vai de 1 a 5.
      const y = height - padding - ((entry.score - 1) / 4) * (height - padding * 2);
      return { x, y, ...entry };
    });

    let pathD = "";
    if (points.length > 0) {
      pathD = `M ${points[0].x} ${points[0].y}`;
      for (let i = 1; i < points.length; i++) {
        pathD += ` L ${points[i].x} ${points[i].y}`;
      }
    }

    return (
      <div className="w-full overflow-x-auto mt-4 bg-background/25 p-4 border border-border rounded-2xl">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full min-w-[500px] h-[150px] overflow-visible">
          {/* Linhas de Grade Verticais / Horizontais */}
          {[1, 2, 3, 4, 5].map((lvl) => {
            const y = height - padding - ((lvl - 1) / 4) * (height - padding * 2);
            return (
              <g key={lvl}>
                <line
                  x1={padding}
                  y1={y}
                  x2={width - padding}
                  y2={y}
                  stroke="var(--color-border)"
                  strokeWidth="0.5"
                  strokeDasharray="4,4"
                />
                <text x="5" y={y + 3} className="text-[8px] fill-text-muted font-bold">
                  {lvl}★
                </text>
              </g>
            );
          })}

          {/* Linha do Gráfico */}
          {points.length > 1 && (
            <path
              d={pathD}
              fill="none"
              stroke="var(--color-primary)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Pontos Individuais */}
          {points.map((pt, idx) => (
            <g key={idx} className="group cursor-pointer">
              <circle
                cx={pt.x}
                cy={pt.y}
                r="4.5"
                className="fill-primary stroke-surface"
                strokeWidth="1.5"
              />
              <circle
                cx={pt.x}
                cy={pt.y}
                r="8"
                className="fill-primary/20 opacity-0 group-hover:opacity-100 transition-opacity"
              />
              <title>
                {new Date(pt.date + "T00:00:00").toLocaleDateString("pt-BR")} - Nota: {pt.score}
              </title>
            </g>
          ))}
        </svg>
      </div>
    );
  };

  const handlePrint = () => {
    // Abre a rota do backend configurada para exportar o relatório imprimível
    window.open(`/api/v1/reports/export-html?child_id=${childId}`, "_blank");
  };

  return (
    <div className="flex flex-col gap-6">
      {/* KPIs Principais */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* KPI 1: Taxa de Conclusão */}
        <div className="bg-surface border border-border p-4 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-[10px] font-bold text-text-muted uppercase tracking-wider">
              Conclusão de Tarefas
            </span>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-2xl font-black text-text-primary">
                {task_stats.completion_rate}%
              </span>
              <span className="text-xs text-text-muted font-medium">
                ({task_stats.completed}/{task_stats.total})
              </span>
            </div>
          </div>
        </div>

        {/* KPI 2: Engajamento Médio */}
        <div className="bg-surface border border-border p-4 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center text-secondary">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-[10px] font-bold text-text-muted uppercase tracking-wider">
              Média de Engajamento
            </span>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-2xl font-black text-text-primary">
                {avgEngagement}
              </span>
              <span className="text-xs text-text-muted font-medium">
                / 5.0
              </span>
            </div>
          </div>
        </div>

        {/* KPI 3: Total de Pendentes */}
        <div className="bg-surface border border-border p-4 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-tertiary/10 flex items-center justify-center text-tertiary">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-[10px] font-bold text-text-muted uppercase tracking-wider">
              Tarefas Pendentes
            </span>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-2xl font-black text-text-primary">
                {task_stats.pending}
              </span>
              <span className="text-xs text-text-muted font-medium">
                atividades
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Gráfico de Evolução e Grade de Áreas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Histórico do Engajamento */}
        <Card title="Evolução do Engajamento" icon={<TrendingUp className="w-5 h-5 text-primary" />}>
          <p className="text-xs text-text-muted">
            Histórico contínuo do índice comportamental e de atenção da criança em sala de aula e nas tarefas em casa.
          </p>
          {renderSVGChart()}
          {engagement_history.length > 0 && (
            <div className="mt-4 flex gap-4 text-[10px] font-semibold text-text-muted justify-center">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-primary inline-block"></span> Evolução Comportamental
              </span>
            </div>
          )}
        </Card>

        {/* Mapa Curricular / Disciplinas */}
        <Card title="Habilidades Trabalhadas" icon={<BookOpen className="w-5 h-5 text-secondary" />}>
          <p className="text-xs text-text-muted mb-4">
            Componentes curriculares e competências cognitivas mais trabalhados nas dinâmicas diárias escolares.
          </p>

          {subject_distribution.length === 0 ? (
            <div className="text-center py-10 text-xs text-text-muted">
              Nenhuma habilidade identificada no período.
            </div>
          ) : (
            <div className="flex flex-col gap-3.5">
              {subject_distribution.slice(0, 5).map((entry, idx) => {
                const maxVal = subject_distribution[0].count;
                const percentage = maxVal > 0 ? (entry.count / maxVal) * 100 : 0;
                return (
                  <div key={idx} className="flex flex-col gap-1">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-text-primary">{entry.subject}</span>
                      <span className="font-semibold text-text-muted">{entry.count} registros</span>
                    </div>
                    {/* Barra de Progresso */}
                    <div className="w-full h-2.5 bg-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-secondary transition-all duration-500 rounded-full"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      </div>

      {/* Ações de Impressão e Exportação */}
      <Card title="Exportação e Relatório Oficial" icon={<Sparkles className="w-5 h-5 text-primary" />}>
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex-1">
            <h4 className="text-sm font-bold text-text-primary">Ficha Pedagógica de Progresso</h4>
            <p className="text-xs text-text-muted mt-1">
              Gere um relatório formatado e limpo para reuniões de pais e mestres ou arquivo pedagógico da coordenação.
            </p>
          </div>
          <Button onClick={handlePrint} className="flex items-center gap-1.5 w-full sm:w-auto">
            <Printer className="w-4 h-4" />
            Imprimir Ficha Completa
          </Button>
        </div>
      </Card>
    </div>
  );
}
