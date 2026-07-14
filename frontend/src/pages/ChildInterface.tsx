import React, { useState, useEffect } from "react";
import { MessageSquare, TrendingUp, Trophy, Zap, Loader, Star } from "lucide-react";
import { Card } from "../components/ui/Card";
import { LearningAnalytics } from "../components/domains/adaptive/LearningAnalytics";
import { InteractionCard } from "../components/domains/adaptive/InteractionCard";
import type { Interaction } from "../lib/types";
import { api } from "../lib/api";

export function ChildInterface() {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [gamificationData, setGamificationData] = useState({
    badges: ["🌟", "💡", "🔥"],
    streak: 5,
    points: 150,
    nextChallenge: "Dominar Frações",
  });
  const [loading, setLoading] = useState(true);
  const childId = localStorage.getItem("child_id") || "";

  useEffect(() => {
    const loadData = async () => {
      try {
        if (!childId) {
          console.warn("child_id not found");
          return;
        }

        const data = await api<Interaction[]>(`/api/v1/interactions?child_id=${childId}&limit=5`);
        const pending = data.filter((i) => i.status === "scheduled");
        setInteractions(pending);
      } catch (err) {
        console.error("Erro ao carregar interações:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [childId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Star className="w-8 h-8 text-purple-600" />
              <h1 className="text-2xl font-bold text-gray-900">Meu Aprendizado</h1>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-purple-600">{gamificationData.points}</p>
              <p className="text-xs text-gray-500">Pontos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader className="w-6 h-6 animate-spin text-gray-400 mr-2" />
            <span className="text-gray-500">Carregando...</span>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Gamificação */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card className="p-4 text-center border-purple-200 bg-purple-50">
                <Trophy className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <p className="text-sm text-gray-600">Troféus</p>
                <div className="flex justify-center gap-1 mt-2">
                  {gamificationData.badges.map((badge, i) => (
                    <span key={i} className="text-xl">{badge}</span>
                  ))}
                </div>
              </Card>

              <Card className="p-4 text-center border-orange-200 bg-orange-50">
                <Zap className="w-8 h-8 mx-auto mb-2 text-orange-600" />
                <p className="text-sm text-gray-600">Sequência</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">{gamificationData.streak} dias</p>
              </Card>

              <Card className="p-4 text-center border-blue-200 bg-blue-50">
                <Star className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <p className="text-sm text-gray-600">Próximo Desafio</p>
                <p className="text-sm font-semibold text-blue-600 mt-1">{gamificationData.nextChallenge}</p>
              </Card>
            </div>

            {/* Interações Agendadas */}
            {interactions.length > 0 && (
              <div>
                <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  Atividades Agendadas ({interactions.length})
                </h2>
                <div className="space-y-4">
                  {interactions.map((interaction) => (
                    <InteractionCard
                      key={interaction.id}
                      interaction={interaction}
                      onResponseSubmitted={() => {
                        setInteractions(interactions.filter((i) => i.id !== interaction.id));
                      }}
                      showFeedback={true}
                    />
                  ))}
                </div>
              </div>
            )}

            {interactions.length === 0 && !loading && (
              <Card className="p-8 text-center">
                <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">Nenhuma atividade agendada no momento</p>
                <p className="text-sm text-gray-400 mt-2">Volte em breve para novas atividades!</p>
              </Card>
            )}

            {/* Análise de Progresso */}
            <div>
              <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Seu Progresso
              </h2>
              {childId && <LearningAnalytics childId={childId} />}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
