import React, { useEffect, useState } from "react";
import { CheckCircle2, Loader, MessageSquare, Send, Sparkles, Star } from "lucide-react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import type { Child, DailyJourney, Interaction } from "../lib/types";
import { api } from "../lib/api";

const today = new Date().toISOString().slice(0, 10);

export function ChildInterface() {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChildId, setSelectedChildId] = useState(localStorage.getItem("child_id") || "");
  const [journey, setJourney] = useState<DailyJourney | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const kids = await api<Child[]>("/api/v1/children");
      setChildren(kids);
      const childId = selectedChildId || kids[0]?.id || "";
      if (childId) {
        setSelectedChildId(childId);
        localStorage.setItem("child_id", childId);
        const data = await api<DailyJourney>(`/api/v1/daily-journey?child_id=${childId}&target_date=${today}`);
        setJourney(data);
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load().catch(console.error);
  }, []);

  async function changeChild(childId: string) {
    setSelectedChildId(childId);
    localStorage.setItem("child_id", childId);
    const data = await api<DailyJourney>(`/api/v1/daily-journey?child_id=${childId}&target_date=${today}`);
    setJourney(data);
  }

  async function sendAnswer(interaction: Interaction) {
    const responseText = answers[interaction.id]?.trim();
    if (!responseText) return;
    await api(`/api/v1/study-plans/interactions/${interaction.id}/responses`, {
      method: "POST",
      body: JSON.stringify({ responder_type: "child", response_text: responseText, response_score: 5, responded_at: today }),
    });
    setAnswers({ ...answers, [interaction.id]: "" });
    if (selectedChildId) {
      const data = await api<DailyJourney>(`/api/v1/daily-journey?child_id=${selectedChildId}&target_date=${today}`);
      setJourney(data);
    }
  }

  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="border-b border-border bg-surface sticky top-0 z-20">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <Star className="w-7 h-7 text-primary shrink-0" />
            <div className="min-w-0">
              <h1 className="text-xl font-black truncate">App da Crianca</h1>
              <p className="text-xs text-text-muted">Atividades de hoje</p>
            </div>
          </div>
          <div className="rounded-lg bg-primary/10 px-3 py-2 text-sm font-black text-primary flex items-center gap-1"><Sparkles className="w-4 h-4" /> Hoje</div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-5">
        {loading ? (
          <Card className="p-6 flex items-center gap-2"><Loader className="w-4 h-4 animate-spin" /> Carregando...</Card>
        ) : !selectedChildId ? (
          <Card className="p-6 text-center text-text-muted">Nenhuma crianca disponivel.</Card>
        ) : (
          <>
            {children.length > 1 && (
              <select className="w-full h-11 rounded-lg border border-border bg-surface px-3 text-sm" value={selectedChildId} onChange={(e) => changeChild(e.target.value)}>
                {children.map((child) => <option key={child.id} value={child.id}>{child.full_name}</option>)}
              </select>
            )}

            <Card className="p-5">
              <div className="flex items-center gap-2 mb-3"><MessageSquare className="w-5 h-5 text-primary" /><h2 className="font-black">Minha missao do dia</h2></div>
              <p className="text-sm text-text-muted whitespace-pre-wrap">{journey?.session.child_activity || "Ainda nao existe atividade preparada para hoje."}</p>
            </Card>

            <section className="space-y-4">
              {journey?.child_interactions.map((interaction) => (
                <Card key={interaction.id} className="p-5">
                  <p className="text-sm leading-relaxed whitespace-pre-wrap mb-4">{interaction.message}</p>
                  {interaction.responses?.length ? (
                    <div className="flex items-center gap-2 text-sm font-bold text-ok"><CheckCircle2 className="w-4 h-4" /> Resposta enviada</div>
                  ) : (
                    <div className="flex flex-col sm:flex-row gap-2">
                      <Input placeholder="Digite sua resposta" value={answers[interaction.id] || ""} onChange={(e) => setAnswers({ ...answers, [interaction.id]: e.target.value })} />
                      <Button onClick={() => sendAnswer(interaction)}><Send className="w-4 h-4" /> Enviar</Button>
                    </div>
                  )}
                </Card>
              ))}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
