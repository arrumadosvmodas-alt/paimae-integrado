import React from "react";
import { Card } from "../../ui/Card";
import { Badge } from "../../ui/Badge";
import { ClipboardList, Calendar, CheckSquare, Clock } from "lucide-react";
import type { Task } from "../../../lib/types";

interface TaskListProps {
  tasks: Task[];
}

export function TaskList({ tasks }: TaskListProps) {
  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case "completed":
      case "concluida":
      case "concluído":
        return <Badge variant="secondary">Concluída</Badge>;
      case "pending":
      case "pendente":
        return <Badge variant="tertiary">Pendente</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Sem prazo";
    // Evitar problemas de fuso horário local
    const date = new Date(dateStr + "T00:00:00");
    return date.toLocaleDateString("pt-BR");
  };

  return (
    <Card title="Tarefas Pendentes" icon={<ClipboardList className="w-5 h-5 text-primary" />}>
      {!tasks.length ? (
        <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
          <ClipboardList className="w-12 h-12 text-text-muted/30 mb-3" />
          <p className="text-sm font-semibold text-text-muted">Nenhuma tarefa cadastrada.</p>
          <p className="text-xs text-text-muted/70 mt-1 max-w-[240px]">
            Adicione uma nova tarefa usando o formulário para organizar os compromissos.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="p-4 border border-border bg-surface hover:bg-surface-hover/40 rounded-xl transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h4 className="text-sm font-bold text-text-primary truncate">
                    {task.title}
                  </h4>
                  {getStatusBadge(task.status)}
                </div>
                {task.description && (
                  <p className="text-xs text-text-muted mt-1 line-clamp-2">
                    {task.description}
                  </p>
                )}
                <div className="flex items-center gap-4 mt-2.5 flex-wrap">
                  <div className="flex items-center gap-1 text-xs text-text-muted">
                    <Calendar className="w-3.5 h-3.5 text-primary" />
                    <span>Prazo: {formatDate(task.due_date)}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
