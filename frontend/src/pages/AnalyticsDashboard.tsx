import React, { useState, useEffect } from "react";
import { BarChart3, Users, TrendingUp, Filter } from "lucide-react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { ChildSelector } from "../components/domains/child/ChildSelector";
import { ProgressChart } from "../components/domains/analytics/ProgressChart";
import { LearningStyleChart } from "../components/domains/analytics/LearningStyleChart";
import { ThemeProgressChart } from "../components/domains/analytics/ThemeProgressChart";
import { ComparisonChart } from "../components/domains/analytics/ComparisonChart";
import { ReportGenerator } from "../components/domains/analytics/ReportGenerator";
import type { Child } from "../lib/types";
import { api } from "../lib/api";

export function AnalyticsDashboard() {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChildId, setSelectedChildId] = useState<string>("");
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);
  const [timeRange, setTimeRange] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadChildren = async () => {
      try {
        const kids = await api<Child[]>("/api/v1/children");
        setChildren(kids);
        if (kids.length > 0) {
          setSelectedChildId(kids[0].id);
          setSelectedChild(kids[0]);
        }
      } catch (err) {
        console.error("Erro ao carregar crianças:", err);
      } finally {
        setLoading(false);
      }
    };

    loadChildren();
  }, []);

  const handleSelectChild = (childId: string) => {
    setSelectedChildId(childId);
    const child = children.find((c) => c.id === childId);
    setSelectedChild(child || null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Analytics & Relatórios</h1>
          </div>
          <p className="text-sm text-gray-600">Análise detalhada de progresso, estilos e comparativas</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <Card className="p-8 text-center">
            <p className="text-gray-500">Carregando...</p>
          </Card>
        ) : children.length === 0 ? (
          <Card className="p-8 text-center">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">Nenhuma criança cadastrada</p>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Seletor de Criança e Filtros */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card className="p-6">
                  <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Selecione uma Criança
                  </h2>
                  <ChildSelector
                    childrenList={children}
                    selectedChildId={selectedChildId}
                    onSelectChild={handleSelectChild}
                  />
                </Card>
              </div>

              <Card className="p-6">
                <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                  <Filter className="w-5 h-5" />
                  Filtros
                </h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Período (dias)
                  </label>
                  <select
                    value={timeRange}
                    onChange={(e) => setTimeRange(parseInt(e.target.value))}
                    className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value={7}>Última Semana</option>
                    <option value={30}>Último Mês</option>
                    <option value={90}>Último Trimestre</option>
                    <option value={365}>Último Ano</option>
                  </select>
                </div>
              </Card>
            </div>

            {selectedChildId && (
              <div className="space-y-6">
                {/* Gráfico de Progresso */}
                <ProgressChart childId={selectedChildId} days={timeRange} />

                {/* Grid de Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <LearningStyleChart childId={selectedChildId} />
                  <ComparisonChart childId={selectedChildId} />
                </div>

                {/* Progresso por Tema */}
                <ThemeProgressChart childId={selectedChildId} />

                {/* Relatório e Exportações */}
                <ReportGenerator childId={selectedChildId} childData={selectedChild || undefined} />

                {/* Recomendações e Insights */}
                <Card className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                  <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    Insights & Recomendações
                  </h2>
                  <div className="space-y-3 text-sm">
                    <div className="p-3 bg-white rounded-lg border border-blue-100">
                      <p className="font-semibold text-blue-900">📊 Análise de Desempenho</p>
                      <p className="text-gray-700 mt-1">
                        Acompanhe a evolução do aluno ao longo do tempo. Os gráficos acima mostram progresso,
                        estilos de aprendizagem e comparação com a média da turma.
                      </p>
                    </div>

                    <div className="p-3 bg-white rounded-lg border border-green-100">
                      <p className="font-semibold text-green-900">✅ Próximos Passos</p>
                      <p className="text-gray-700 mt-1">
                        Baseado nos dados, considere aumentar atividades nos temas em dificuldade
                        e reforçar o estilo de aprendizagem preferido do aluno.
                      </p>
                    </div>

                    <div className="p-3 bg-white rounded-lg border border-purple-100">
                      <p className="font-semibold text-purple-900">📥 Exportar Dados</p>
                      <p className="text-gray-700 mt-1">
                        Use o gerador de relatórios para criar documentos PDF, exportar em JSON ou CSV
                        para análises mais profundas.
                      </p>
                    </div>
                  </div>
                </Card>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
