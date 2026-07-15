import React, { useEffect, useMemo, useState } from "react";
import { Bell, CalendarDays, CheckCircle2, ClipboardCheck, GraduationCap, Loader, Plus, UserCheck } from "lucide-react";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { ChildSelector } from "../components/domains/child/ChildSelector";
import type { AcademicGrade, Child, DailyJourney } from "../lib/types";
import { api } from "../lib/api";

const today = new Date().toISOString().slice(0, 10);

export function ParentDashboard() {
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChildId, setSelectedChildId] = useState("");
  const [journey, setJourney] = useState<DailyJourney | null>(null);
  const [loading, setLoading] = useState(true);
  const [attendanceStatus, setAttendanceStatus] = useState("present");
  const [attendanceReason, setAttendanceReason] = useState("");
  const [grade, setGrade] = useState({ subject: "", assessment_name: "", score: "", max_score: "10", notes: "" });

  const selectedChild = useMemo(() => children.find((item) => item.id === selectedChildId), [children, selectedChildId]);

  async function loadChildren() {
    setLoading(true);
    try {
      const kids = await api<Child[]>("/api/v1/children");
      setChildren(kids);
      const nextChildId = selectedChildId || kids[0]?.id || "";
      setSelectedChildId(nextChildId);
      if (nextChildId) await loadJourney(nextChildId);
    } finally {
      setLoading(false);
    }
  }

  async function loadJourney(childId = selectedChildId) {
    if (!childId) return;
    const data = await api<DailyJourney>(`/api/v1/daily-journey?child_id=${childId}&target_date=${today}`);
    setJourney(data);
    setAttendanceStatus(data.attendance?.status || "present");
    setAttendanceReason(data.attendance?.reason || "");
  }

  useEffect(() => {
    loadChildren().catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedChildId) loadJourney(selectedChildId).catch(console.error);
  }, [selectedChildId]);

  async function saveAttendance() {
    if (!selectedChildId) return;
    await api("/api/v1/daily-journey/attendance", {
      method: "POST",
      body: JSON.stringify({ child_id: selectedChildId, date: today, status: attendanceStatus, reason: attendanceReason || null, notes: null }),
    });
    await loadJourney();
  }

  async function saveGrade(event: React.FormEvent) {
    event.preventDefault();
    if (!selectedChild) return;
    await api<AcademicGrade>("/api/v1/daily-journey/grades", {
      method: "POST",
      body: JSON.stringify({
        child_id: selectedChild.id,
        school_id: selectedChild.school_id,
        subject: grade.subject,
        assessment_name: grade.assessment_name,
        assessment_date: today,
        score: grade.score ? Number(grade.score) : null,
        max_score: grade.max_score ? Number(grade.max_score) : null,
        notes: grade.notes || null,
      }),
    });
    setGrade({ subject: "", assessment_name: "", score: "", max_score: "10", notes: "" });
    await loadJourney();
  }

  async function acknowledge() {
    if (!selectedChildId) return;
    await api(`/api/v1/daily-journey/acknowledge?child_id=${selectedChildId}&target_date=${today}`, {
      method: "POST",
      body: JSON.stringify({ acknowledged: true }),
    });
    await loadJourney();
  }

  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="border-b border-border bg-surface sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <UserCheck className="w-6 h-6 text-primary shrink-0" />
            <div className="min-w-0">
              <h1 className="text-xl font-black truncate">App do Responsavel</h1>
              <p className="text-xs text-text-muted">Jornada diaria, frequencia, notas e ciencia</p>
            </div>
          </div>
          <span className="text-xs font-bold text-text-muted">{new Date(today).toLocaleDateString("pt-BR")}</span>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-6 space-y-5">
        {loading ? (
          <Card className="p-6 flex items-center gap-2"><Loader className="w-4 h-4 animate-spin" /> Carregando...</Card>
        ) : children.length === 0 ? (
          <Card className="p-6 text-center text-text-muted">Nenhuma crianca vinculada.</Card>
        ) : (
          <>
            <Card className="p-4">
              <ChildSelector childrenList={children} selectedChildId={selectedChildId} onSelectChild={setSelectedChildId} />
            </Card>

            {journey?.requires_manual_schedule && (
              <Card className="p-4 border-warning/40 bg-warning/10">
                <div className="flex items-start gap-3">
                  <Bell className="w-5 h-5 text-warning shrink-0 mt-0.5" />
                  <div>
                    <h2 className="font-bold">Cronograma necessario</h2>
                    <p className="text-sm text-text-muted">Nao existe atividade registrada para hoje. Inclua no painel central ou no modulo pedagogico para gerar as interacoes automaticamente.</p>
                  </div>
                </div>
              </Card>
            )}

            <section className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <Card className="p-5 lg:col-span-2">
                <div className="flex items-center gap-2 mb-3"><CalendarDays className="w-5 h-5 text-primary" /><h2 className="font-black">Atividades e orientacoes de hoje</h2></div>
                <p className="text-sm text-text-muted mb-4">{journey?.session.summary}</p>
                <div className="space-y-3">
                  {journey?.parent_interactions.map((interaction) => (
                    <div key={interaction.id} className="rounded-lg border border-border p-3 text-sm whitespace-pre-wrap">{interaction.message}</div>
                  ))}
                  {!journey?.parent_interactions.length && <p className="text-sm text-text-muted">{journey?.session.parent_guidance}</p>}
                </div>
                <Button onClick={acknowledge} className="mt-4 w-full sm:w-auto" disabled={Boolean(journey?.session.acknowledged_at)}>
                  <CheckCircle2 className="w-4 h-4" /> {journey?.session.acknowledged_at ? "Ciencia confirmada" : "Confirmar ciencia"}
                </Button>
              </Card>

              <Card className="p-5">
                <div className="flex items-center gap-2 mb-3"><ClipboardCheck className="w-5 h-5 text-primary" /><h2 className="font-black">Frequencia</h2></div>
                <select className="w-full h-11 rounded-lg border border-border bg-surface px-3 text-sm" value={attendanceStatus} onChange={(e) => setAttendanceStatus(e.target.value)}>
                  <option value="present">Foi a escola</option>
                  <option value="absent">Nao foi</option>
                  <option value="sick">Doente</option>
                  <option value="holiday">Feriado/recesso</option>
                  <option value="remote">Atividade remota</option>
                  <option value="excused">Falta justificada</option>
                </select>
                <Input className="mt-3" placeholder="Motivo ou observacao" value={attendanceReason} onChange={(e) => setAttendanceReason(e.target.value)} />
                <Button onClick={saveAttendance} className="mt-3 w-full">Salvar frequencia</Button>
              </Card>
            </section>

            <Card className="p-5">
              <div className="flex items-center gap-2 mb-4"><GraduationCap className="w-5 h-5 text-primary" /><h2 className="font-black">Notas escolares</h2></div>
              <form onSubmit={saveGrade} className="grid grid-cols-1 md:grid-cols-5 gap-3">
                <Input required placeholder="Disciplina" value={grade.subject} onChange={(e) => setGrade({ ...grade, subject: e.target.value })} />
                <Input required placeholder="Avaliacao" value={grade.assessment_name} onChange={(e) => setGrade({ ...grade, assessment_name: e.target.value })} />
                <Input placeholder="Nota" value={grade.score} onChange={(e) => setGrade({ ...grade, score: e.target.value })} />
                <Input placeholder="Maximo" value={grade.max_score} onChange={(e) => setGrade({ ...grade, max_score: e.target.value })} />
                <Button type="submit"><Plus className="w-4 h-4" /> Adicionar</Button>
              </form>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {journey?.grades.map((item) => (
                  <div key={item.id} className="rounded-lg border border-border p-3 text-sm flex justify-between gap-3">
                    <span className="font-semibold">{item.subject} - {item.assessment_name}</span>
                    <span>{item.score ?? "-"}/{item.max_score ?? "-"}</span>
                  </div>
                ))}
              </div>
            </Card>
          </>
        )}
      </div>
    </main>
  );
}
