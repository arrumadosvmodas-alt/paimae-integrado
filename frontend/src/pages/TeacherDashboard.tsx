import React, { useState, useEffect } from "react";
import { LayoutDashboard, BookOpen, Zap, Users, Plus, Loader } from "lucide-react";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { BookUpload } from "../components/domains/book/BookUpload";
import { StudyPlanView } from "../components/domains/adaptive/StudyPlanView";
import { LearningAnalytics } from "../components/domains/adaptive/LearningAnalytics";
import { ChildSelector } from "../components/domains/child/ChildSelector";
import type { Child, PedagogicalMaterial, StudyPlan } from "../lib/types";
import { api } from "../lib/api";

export function TeacherDashboard() {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChildId, setSelectedChildId] = useState<string>("");
  const [materials, setMaterials] = useState<PedagogicalMaterial[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<PedagogicalMaterial | null>(null);
  const [studyPlans, setStudyPlans] = useState<StudyPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<StudyPlan | null>(null);
  const [activeTab, setActiveTab] = useState<"upload" | "plans" | "analytics">("upload");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const kids = await api<Child[]>("/api/v1/children");
        setChildren(kids);
        if (kids.length > 0) {
          setSelectedChildId(kids[0].id);
        }

        const mats = await api<PedagogicalMaterial[]>("/api/v1/pedagogy/materials");
        setMaterials(mats);
      } catch (err) {
        console.error("Erro ao carregar dados:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  useEffect(() => {
    if (selectedChildId) {
      const loadPlans = async () => {
        try {
          const plans = await api<StudyPlan[]>(
            `/api/v1/study-plans?child_id=${selectedChildId}`
          );
          setStudyPlans(plans);
        } catch (err) {
          console.error("Erro ao carregar planos:", err);
        }
      };

      loadPlans();
    }
  }, [selectedChildId]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <LayoutDashboard className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Dashboard do Professor</h1>
            </div>
            <Button variant="primary" className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Novo Plano
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Seletor de Criança */}
        {children.length > 0 && (
          <Card className="mb-6 p-6">
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
        )}

        {selectedChildId ? (
          <div className="space-y-6">
            {/* Abas */}
            <div className="bg-white rounded-lg shadow-sm p-1 flex gap-1 w-fit">
              {(["upload", "plans", "analytics"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
                    activeTab === tab
                      ? "bg-blue-600 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  {tab === "upload" && "📚 Upload"}
                  {tab === "plans" && "📋 Planos"}
                  {tab === "analytics" && "📊 Análise"}
                </button>
              ))}
            </div>

            {/* Conteúdo por Aba */}
            {activeTab === "upload" && (
              <div className="space-y-4">
                <h2 className="font-semibold text-lg flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Fazer Upload de Livro
                </h2>

                {/* Seletor de Material */}
                {materials.length > 0 && (
                  <Card className="p-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Escolha um livro já cadastrado:
                    </label>
                    <select
                      value={selectedMaterial?.id || ""}
                      onChange={(e) => {
                        const mat = materials.find((m) => m.id === e.target.value);
                        setSelectedMaterial(mat || null);
                      }}
                      className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                    >
                      <option value="">-- Selecionar --</option>
                      {materials.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.title} ({m.subject})
                        </option>
                      ))}
                    </select>
                  </Card>
                )}

                {selectedMaterial && (
                  <BookUpload
                    materialId={selectedMaterial.id}
                    onUploadComplete={() => {
                      console.log("Upload completo!");
                    }}
                  />
                )}
              </div>
            )}

            {activeTab === "plans" && (
              <div className="space-y-4">
                <h2 className="font-semibold text-lg flex items-center gap-2">
                  <Zap className="w-5 h-5" />
                  Planos de Estudo
                </h2>

                {loading ? (
                  <div className="flex items-center justify-center p-8">
                    <Loader className="w-6 h-6 animate-spin text-gray-400" />
                  </div>
                ) : studyPlans.length > 0 ? (
                  <div className="space-y-4">
                    {studyPlans.map((plan) => (
                      <Card key={plan.id} className="p-4">
                        <div className="mb-4">
                          <button
                            onClick={() =>
                              setSelectedPlan(selectedPlan?.id === plan.id ? null : plan)
                            }
                            className="font-semibold text-blue-600 hover:underline text-left"
                          >
                            {new Date(plan.start_date).toLocaleDateString("pt-BR")} -{" "}
                            {plan.daily_items?.length || 0} atividades
                          </button>
                        </div>
                        {selectedPlan?.id === plan.id && (
                          <StudyPlanView planId={plan.id} />
                        )}
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card className="p-6 text-center">
                    <p className="text-gray-500">Nenhum plano de estudo criado ainda</p>
                  </Card>
                )}
              </div>
            )}

            {activeTab === "analytics" && (
              <div>
                <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5" />
                  Análise de Aprendizagem
                </h2>
                <LearningAnalytics childId={selectedChildId} />
              </div>
            )}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">Selecione uma criança para começar</p>
          </Card>
        )}
      </div>
    </div>
  );
}
