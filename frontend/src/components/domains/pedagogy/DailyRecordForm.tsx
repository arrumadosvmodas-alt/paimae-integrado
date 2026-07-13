import React, { useState, useEffect } from "react";
import { Card } from "../../ui/Card";
import { Input, Textarea } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { ClipboardList, Plus, Trash2, X } from "lucide-react";
import type { DailySchoolRecord } from "../../../lib/types";

interface DailyRecordFormProps {
  childId?: string;
  recordToEdit?: DailySchoolRecord | null;
  onCancelEdit?: () => void;
  onSubmit: (payload: any) => Promise<void>;
  notify: (msg: string, type?: "ok" | "error") => void;
}

export function DailyRecordForm({ childId, recordToEdit, onCancelEdit, onSubmit, notify }: DailyRecordFormProps) {
  const [date, setDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [summary, setSummary] = useState("");
  const [observedSkills, setObservedSkills] = useState("");
  const [engagementScore, setEngagementScore] = useState("5");
  const [isLoading, setIsLoading] = useState(false);

  // Sugestões de interação com a família
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [newSuggestion, setNewSuggestion] = useState("");

  useEffect(() => {
    if (recordToEdit) {
      setDate(recordToEdit.date);
      setSummary(recordToEdit.summary);
      setObservedSkills(recordToEdit.observed_skills || "");
      setEngagementScore(String(recordToEdit.engagement_score || 5));
      setSuggestions(recordToEdit.suggestions?.map(s => s.suggestion_text) || []);
    } else {
      setDate(new Date().toISOString().split("T")[0]);
      setSummary("");
      setObservedSkills("");
      setEngagementScore("5");
      setSuggestions([]);
    }
  }, [recordToEdit]);

  const handleAddSuggestion = () => {
    if (!newSuggestion.trim()) return;
    setSuggestions([...suggestions, newSuggestion.trim()]);
    setNewSuggestion("");
  };

  const handleRemoveSuggestion = (index: number) => {
    setSuggestions(suggestions.filter((_, i) => i !== index));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!summary.trim() || !date) {
      notify("Preencha a data e o resumo do dia escolar.", "error");
      return;
    }

    setIsLoading(true);
    try {
      if (recordToEdit) {
        await onSubmit({
          id: recordToEdit.id,
          date: date,
          summary: summary.trim(),
          observed_skills: observedSkills.trim() || null,
          engagement_score: Number(engagementScore),
          suggestions: suggestions.map(text => ({ suggestion_text: text }))
        });
      } else {
        if (!childId) {
          notify("Selecione uma criança para cadastrar.", "error");
          return;
        }
        await onSubmit({
          child_id: childId,
          date: date,
          summary: summary.trim(),
          observed_skills: observedSkills.trim() || null,
          engagement_score: Number(engagementScore),
          suggestions: suggestions.map(text => ({ suggestion_text: text }))
        });
        setSummary("");
        setObservedSkills("");
        setEngagementScore("5");
        setSuggestions([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card 
      title={recordToEdit ? "Editar Relatório Diário" : "Relatório Pedagógico Diário"} 
      icon={<ClipboardList className="w-5 h-5 text-primary" />}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Data *"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            disabled={isLoading || (!childId && !recordToEdit)}
          />
          <div>
            <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-1.5">
              Engajamento Geral (1-5) *
            </label>
            <select
              value={engagementScore}
              onChange={(e) => setEngagementScore(e.target.value)}
              disabled={isLoading || (!childId && !recordToEdit)}
              className="w-full h-10 px-3 border border-border rounded-lg bg-surface text-text-primary focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none transition-all duration-200 text-sm"
            >
              <option value="5">5 - Excelente</option>
              <option value="4">4 - Muito Bom</option>
              <option value="3">3 - Regular</option>
              <option value="2">2 - Baixo</option>
              <option value="1">1 - Muito Baixo</option>
            </select>
          </div>
        </div>

        <Textarea
          label="Resumo das Atividades Escolares *"
          placeholder="Ex: Hoje trabalhamos caligrafia da letra B e aprendemos a conta até 30..."
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          required
          disabled={isLoading || (!childId && !recordToEdit)}
        />

        <Input
          label="Habilidades Observadas (Separadas por vírgula)"
          placeholder="Ex: Coordenação Motora, Foco, Escuta Atenta"
          value={observedSkills}
          onChange={(e) => setObservedSkills(e.target.value)}
          disabled={isLoading || (!childId && !recordToEdit)}
        />

        {/* Sugestões de interação com os pais */}
        <div className="border border-border p-4 rounded-xl bg-background/30 flex flex-col gap-3">
          <span className="block text-xs font-bold text-text-primary uppercase tracking-wider">
            Sugestão de Interação (Para a Família)
          </span>

          <div className="flex gap-2">
            <div className="flex-1">
              <Input
                placeholder="Ex: Perguntar qual historinha foi contada hoje..."
                value={newSuggestion}
                onChange={(e) => setNewSuggestion(e.target.value)}
                disabled={!childId && !recordToEdit}
              />
            </div>
            <Button
              type="button"
              onClick={handleAddSuggestion}
              disabled={!newSuggestion.trim() || (!childId && !recordToEdit)}
              variant="outline"
              className="h-10 flex items-center justify-center gap-1"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>

          {suggestions.length > 0 && (
            <ul className="mt-2 flex flex-col gap-1.5 max-h-32 overflow-y-auto">
              {suggestions.map((sug, idx) => (
                <li key={idx} className="flex justify-between items-center text-xs p-2 bg-surface border border-border rounded-lg">
                  <span className="text-text-primary">{sug}</span>
                  <button type="button" onClick={() => handleRemoveSuggestion(idx)} className="text-error hover:text-red-700">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="flex gap-2 mt-2">
          {recordToEdit && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancelEdit}
              disabled={isLoading}
              className="w-1/3 flex items-center justify-center gap-1"
            >
              <X className="w-4 h-4" /> Cancelar
            </Button>
          )}
          <Button
            type="submit"
            isLoading={isLoading}
            disabled={!childId && !recordToEdit}
            className="flex-1"
          >
            {recordToEdit ? "Salvar Alterações" : childId ? "Registrar Relatório Diário" : "Selecione uma criança primeiro"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
