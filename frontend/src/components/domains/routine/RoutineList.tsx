import React from "react";
import { Card } from "../../ui/Card";
import { Badge } from "../../ui/Badge";
import { BookOpen, Calendar, Clock, Users } from "lucide-react";
import type { Routine } from "../../../lib/types";

const weekdayLabels = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"];

interface RoutineListProps {
  routines: Routine[];
}

export function RoutineList({ routines }: RoutineListProps) {
  const getAudienceBadge = (audience: string) => {
    switch (audience) {
      case "child":
        return <Badge variant="primary">Criança</Badge>;
      case "guardian":
        return <Badge variant="secondary">Responsável</Badge>;
      case "both":
        return <Badge variant="tertiary">Ambos</Badge>;
      default:
        return <Badge variant="neutral">{audience}</Badge>;
    }
  };

  const getWeekdaysString = (days: number[]) => {
    if (!days || days.length === 0) return "Nenhum dia selecionado";
    if (days.length === 7) return "Todos os dias";
    return days.map((d) => weekdayLabels[d]).join(", ");
  };

  return (
    <Card title="Rotinas Cadastradas" icon={<BookOpen className="w-5 h-5 text-primary" />}>
      {!routines.length ? (
        <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
          <BookOpen className="w-12 h-12 text-text-muted/30 mb-3" />
          <p className="text-sm font-semibold text-text-muted">Nenhuma rotina cadastrada.</p>
          <p className="text-xs text-text-muted/70 mt-1 max-w-[240px]">
            Crie uma rotina usando o formulário para acompanhar as atividades.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {routines.map((routine) => (
            <div
              key={routine.id}
              className="p-4 border border-border bg-surface hover:bg-surface-hover/40 rounded-xl transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h4 className="text-sm font-bold text-text-primary truncate">
                    {routine.title}
                  </h4>
                  {getAudienceBadge(routine.target_audience)}
                </div>
                {routine.description && (
                  <p className="text-xs text-text-muted mt-1 line-clamp-2">
                    {routine.description}
                  </p>
                )}
                <div className="flex items-center gap-4 mt-2.5 flex-wrap">
                  <div className="flex items-center gap-1 text-xs text-text-muted">
                    <Clock className="w-3.5 h-3.5 text-primary" />
                    <span>{routine.scheduled_time}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-text-muted">
                    <Calendar className="w-3.5 h-3.5 text-primary" />
                    <span className="truncate max-w-[180px]">
                      {getWeekdaysString(routine.weekdays)}
                    </span>
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
