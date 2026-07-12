import React from "react";
import { Card } from "../../ui/Card";
import { Select } from "../../ui/Input";
import { User, Calendar, BookOpen } from "lucide-react";
import type { Child } from "../../../lib/types";

interface ChildSelectorProps {
  childrenList: Child[];
  selectedChildId: string;
  onSelectChild: (id: string) => void;
}

export function ChildSelector({
  childrenList,
  selectedChildId,
  onSelectChild,
}: ChildSelectorProps) {
  const selectedChild = childrenList.find((child) => child.id === selectedChildId);

  return (
    <Card title="Criança em foco" icon={<User className="w-5 h-5 text-primary" />}>
      <div className="flex flex-col gap-4">
        <Select
          value={selectedChildId}
          onChange={(e) => onSelectChild(e.target.value)}
          placeholder="Selecione uma criança"
        >
          {childrenList.map((child) => (
            <option key={child.id} value={child.id}>
              {child.full_name}
            </option>
          ))}
        </Select>

        {selectedChild ? (
          <div className="mt-2 p-3 bg-background/50 border border-border rounded-xl flex flex-col gap-2">
            <div className="flex items-center gap-2 text-xs text-text-muted">
              <BookOpen className="w-3.5 h-3.5 flex-shrink-0 text-primary" />
              <span className="font-semibold text-text-primary">Turma:</span>
              <span className="truncate">{selectedChild.class_name ?? "Sem turma cadastrada"}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-text-muted">
              <Calendar className="w-3.5 h-3.5 flex-shrink-0 text-primary" />
              <span className="font-semibold text-text-primary">Nascimento:</span>
              <span>
                {selectedChild.birth_date
                  ? new Date(selectedChild.birth_date + "T00:00:00").toLocaleDateString("pt-BR")
                  : "Não cadastrado"}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-text-muted text-center py-2">
            Nenhuma criança selecionada para visualização.
          </p>
        )}
      </div>
    </Card>
  );
}
