import React, { useState, useEffect } from "react";
import { Users, AlertTriangle, TrendingUp, MessageSquare, Loader } from "lucide-react";
import { Card } from "../components/ui/Card";
import { ChildSelector } from "../components/domains/child/ChildSelector";
import { LearningAnalytics } from "../components/domains/adaptive/LearningAnalytics";
import { InteractionCard } from "../components/domains/adaptive/InteractionCard";
import type { Child, Interaction } from "../lib/types";
import { api } from "../lib/api";

export function ParentDashboard() {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChildId, setSelectedChildId] = useState<string>("");
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadChildren = async () => {
      try {
        const kids = await api<Child[]>("/api/v1/children");
        setChildren(kids);
        if (kids.length > 0) {
          setSelectedChildId(kids[0].id);
        }
      } catch (err) {
        console.error("Erro ao carregar crianças:", err);
      } finally {
        setLoading(false);
      }
    };

    loadChildren();
  }, []);

  useEffect(() => {
    if (selectedChildId) {
      const loadInteractions = async () => {
        try {
          const data = await api<Interaction[]>(
            `/api/v1/interactions?child_id=${selectedChildId}&limit=10`
          );
          setInteractions(data);
        } catch (err) {
          console.error("Erro ao carregar interações:", err);
        }
      };

      loadInteractions();
    }
  }, [selectedChildId]);

  const selectedChild = children.find((c) => c.id === selectedChildId);
  const pendingInteractions = interactions.filter((i) => i.status === "scheduled");
  const respondedInteractions = interactions.filter((i) => i.status === "sent" || i.status === "read");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Acompanhamento de Progresso</h1>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader className="w-6 h-6 animate-spin text-gray-400 mr-2" />
            <span className="text-gray-500">Carregando...</span>
          </div>
        ) : children.length === 0 ? (
          <Card className="p-8 text-center">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">Nenhuma criança cadastrada</p>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Seletor de Criança */}
            <Card className="p-6">
              <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Users className="w-5 h-5" />
                Selecione uma Criança
              </h2>
              <ChildSelector
                childrenList={children}
                selectedChildId={selectedChildId}
                onSelectChild={setSelectedChildId}
              />
            </Card>

            {selectedChild && (
              <div className="space-y-6">
                {/* Análise de Progresso */}
                <div>
                  <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Análise de Aprendizagem
                  </h2>
                  <LearningAnalytics childId={selectedChildId} />
                </div>

                {/* Interações */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Pendentes */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                      <MessageSquare className="w-5 h-5" />
                      Respostas Pendentes ({pendingInteractions.length})
                    </h3>
                    {pendingInteractions.length > 0 ? (
                      <div className="space-y-4">
                        {pendingInteractions.map((interaction) => (
                          <InteractionCard
                            key={interaction.id}
                            interaction={interaction}
                            showFeedback={false}
                          />
                        ))}
                      </div>
                    ) : (
                      <Card className="p-6 text-center">
                        <p className="text-gray-500">Nenhuma interação pendente</p>
                      </Card>
                    )}
                  </div>

                  {/* Respondidas */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                      <MessageSquare className="w-5 h-5" />
                      Respondidas ({respondedInteractions.length})
                    </h3>
                    {respondedInteractions.length > 0 ? (
                      <div className="space-y-4">
                        {respondedInteractions.map((interaction) => (
                          <Card key={interaction.id} className="p-4">
                            <p className="text-sm text-gray-600 mb-2">{interaction.message}</p>
                            <p className="text-xs text-green-600 flex items-center gap-1">
                              ✓ Respondida em{" "}
                              {interaction.sent_at
                                ? new Date(interaction.sent_at).toLocaleDateString("pt-BR")
                                : "data desconhecida"}
                            </p>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <Card className="p-6 text-center">
                        <p className="text-gray-500">Nenhuma resposta registrada ainda</p>
                      </Card>
                    )}
                  </div>
                </div>

                {/* Alertas */}
                <Card className="p-4 border-yellow-200 bg-yellow-50">
                  <h3 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    Alertas Importantes
                  </h3>
                  <ul className="space-y-2 text-sm text-yellow-800">
                    <li>• Acompanhe regularmente o progresso</li>
                    <li>• Incentive respostas nas interações</li>
                    <li>• Converse com o professor sobre dificuldades</li>
                  </ul>
                </Card>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
