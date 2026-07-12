import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Input, Textarea } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { Sparkles } from "lucide-react";

interface EvolutionEventCreateFormProps {
  childId?: string;
  onSubmit: (payload: {
    child_id: string;
    event_type: string;
    occurred_at: string;
    score: number | null;
    notes: string | null;
    event_metadata: null;
  }) => Promise<void>;
}

export function EvolutionEventCreateForm({ childId, onSubmit }: EvolutionEventCreateFormProps) {
  const [eventType, setEventType] = useState("");
  const [score, setScore] = useState("");
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!childId || !eventType.trim()) return;

    setIsLoading(true);
    try {
      await onSubmit({
        child_id: childId,
        event_type: eventType.trim(),
        occurred_at: new Date().toISOString(),
        score: score ? Number(score) : null,
        notes: notes.trim() || null,
        event_metadata: null,
      });
      setEventType("");
      setScore("");
      setNotes("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card title="Registrar Evolução" icon={<Sparkles className="w-5 h-5 text-primary" />}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Tipo de Evento"
          placeholder="Ex: Leitura, Comportamento, Prova"
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
          required
          disabled={isLoading || !childId}
        />
        <Input
          label="Pontuação / Nota (0-100, opcional)"
          type="number"
          min="0"
          max="100"
          placeholder="Ex: 85"
          value={score}
          onChange={(e) => setScore(e.target.value)}
          disabled={isLoading || !childId}
        />
        <Textarea
          label="Observações"
          placeholder="Ex: Demonstrou bom foco durante a leitura e respondeu às perguntas corretamente."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={isLoading || !childId}
        />
        <Button
          type="submit"
          isLoading={isLoading}
          disabled={!childId}
          className="w-full mt-2"
        >
          {childId ? "Registrar Evento" : "Selecione uma criança primeiro"}
        </Button>
      </form>
    </Card>
  );
}
