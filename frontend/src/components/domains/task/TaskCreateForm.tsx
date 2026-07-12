import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Input, Textarea } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { ClipboardList } from "lucide-react";

interface TaskCreateFormProps {
  childId?: string;
  onSubmit: (payload: {
    child_id: string;
    title: string;
    description: string | null;
    due_date: string | null;
  }) => Promise<void>;
}

export function TaskCreateForm({ childId, onSubmit }: TaskCreateFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!childId || !title.trim()) return;

    setIsLoading(true);
    try {
      await onSubmit({
        child_id: childId,
        title: title.trim(),
        description: description.trim() || null,
        due_date: dueDate || null,
      });
      setTitle("");
      setDescription("");
      setDueDate("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card title="Nova Tarefa" icon={<ClipboardList className="w-5 h-5 text-primary" />}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Título da Tarefa"
          placeholder="Ex: Trazer cartolina para trabalho de ciências"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          disabled={isLoading || !childId}
        />
        <Textarea
          label="Descrição (opcional)"
          placeholder="Ex: Cartolina azul de tamanho A2 para apresentação na sexta-feira."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={isLoading || !childId}
        />
        <Input
          label="Data de Entrega / Prazo"
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          disabled={isLoading || !childId}
        />
        <Button
          type="submit"
          isLoading={isLoading}
          disabled={!childId}
          className="w-full mt-2"
        >
          {childId ? "Criar Tarefa" : "Selecione uma criança primeiro"}
        </Button>
      </form>
    </Card>
  );
}
