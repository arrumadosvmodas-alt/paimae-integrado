import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Input, Select, Textarea, Checkbox } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { BookOpen } from "lucide-react";

const weekdays = [
  { value: 0, label: "Seg" },
  { value: 1, label: "Ter" },
  { value: 2, label: "Qua" },
  { value: 3, label: "Qui" },
  { value: 4, label: "Sex" },
  { value: 5, label: "Sab" },
  { value: 6, label: "Dom" },
];

interface RoutineCreateFormProps {
  childId?: string;
  onSubmit: (payload: {
    child_id: string;
    title: string;
    description: string | null;
    scheduled_time: string;
    weekdays: number[];
    target_audience: string;
  }) => Promise<void>;
}

export function RoutineCreateForm({ childId, onSubmit }: RoutineCreateFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [scheduledTime, setScheduledTime] = useState("");
  const [selectedWeekdays, setSelectedWeekdays] = useState<number[]>([]);
  const [targetAudience, setTargetAudience] = useState("child");
  const [isLoading, setIsLoading] = useState(false);

  const handleWeekdayChange = (value: number, checked: boolean) => {
    if (checked) {
      setSelectedWeekdays((prev) => [...prev, value].sort());
    } else {
      setSelectedWeekdays((prev) => prev.filter((d) => d !== value));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!childId || !title.trim() || !scheduledTime) return;

    setIsLoading(true);
    try {
      await onSubmit({
        child_id: childId,
        title: title.trim(),
        description: description.trim() || null,
        scheduled_time: scheduledTime,
        weekdays: selectedWeekdays,
        target_audience: targetAudience,
      });
      setTitle("");
      setDescription("");
      setScheduledTime("");
      setSelectedWeekdays([]);
      setTargetAudience("child");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card title="Nova Rotina" icon={<BookOpen className="w-5 h-5 text-primary" />}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Título da Rotina"
          placeholder="Ex: Leitura de Histórias ou Higiene Bucal"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          disabled={isLoading || !childId}
        />
        
        <Textarea
          label="Descrição (opcional)"
          placeholder="Ex: Ler um livro infantil de 10 páginas antes de dormir."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={isLoading || !childId}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Horário Agendado"
            type="time"
            value={scheduledTime}
            onChange={(e) => setScheduledTime(e.target.value)}
            required
            disabled={isLoading || !childId}
          />

          <Select
            label="Público-Alvo"
            value={targetAudience}
            onChange={(e) => setTargetAudience(e.target.value)}
            disabled={isLoading || !childId}
          >
            <option value="child">Criança</option>
            <option value="guardian">Responsável</option>
            <option value="both">Ambos</option>
          </Select>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold font-display uppercase tracking-wider text-text-muted">
            Dias da Semana
          </span>
          <div className="flex flex-wrap gap-2">
            {weekdays.map((day) => (
              <Checkbox
                key={day.value}
                label={day.label}
                checked={selectedWeekdays.includes(day.value)}
                onChange={(e) => handleWeekdayChange(day.value, e.target.checked)}
                disabled={isLoading || !childId}
              />
            ))}
          </div>
        </div>

        <Button
          type="submit"
          isLoading={isLoading}
          disabled={!childId}
          className="w-full mt-2"
        >
          {childId ? "Criar Rotina" : "Selecione uma criança primeiro"}
        </Button>
      </form>
    </Card>
  );
}
