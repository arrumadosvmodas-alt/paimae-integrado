import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Badge } from "../../ui/Badge";
import { Button } from "../../ui/Button";
import { Calendar, Award, Star, Compass, Edit2, EyeOff, Eye } from "lucide-react";
import type { DailySchoolRecord } from "../../../lib/types";

interface DailyRecordListProps {
  records: DailySchoolRecord[];
  onEdit?: (record: DailySchoolRecord) => void;
  onToggleActive?: (id: string) => Promise<void>;
  showActions?: boolean;
}

export function DailyRecordList({ records, onEdit, onToggleActive, showActions = false }: DailyRecordListProps) {
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const handleToggleActive = async (id: string) => {
    if (!onToggleActive) return;
    setLoadingId(id);
    try {
      await onToggleActive(id);
    } finally {
      setLoadingId(null);
    }
  };

  if (records.length === 0) {
    return (
      <Card title="Diário Escolar" icon={<Calendar className="w-5 h-5 text-primary" />}>
        <div className="text-center py-6 text-text-muted text-xs">
          Nenhum relatório diário registrado para esta criança ainda.
        </div>
      </Card>
    );
  }

  return (
    <Card title="Diário Escolar" icon={<Calendar className="w-5 h-5 text-primary" />}>
      <div className="flex flex-col gap-4 max-h-[450px] overflow-y-auto pr-1">
        {records.map((record) => {
          const isActive = record.is_active !== false;
          return (
            <div 
              key={record.id} 
              className={`border p-4 rounded-xl transition-all duration-200 ${
                isActive 
                  ? "border-border bg-background/20 hover:bg-background/40" 
                  : "border-border/50 bg-background/5 opacity-60"
              }`}
            >
              <div className="flex justify-between items-center mb-2 flex-wrap gap-2">
                <span className="text-xs font-bold text-text-primary flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-primary" />
                  {new Date(record.date).toLocaleDateString("pt-BR")}
                  {!isActive && (
                    <span className="ml-2 text-[9px] font-bold px-1.5 py-0.5 rounded bg-error/20 text-error uppercase">
                      Inativo
                    </span>
                  )}
                </span>
                <div className="flex items-center gap-2">
                  {record.engagement_score && (
                    <div className="flex items-center gap-0.5 text-yellow-500">
                      {Array.from({ length: 5 }).map((_, idx) => (
                        <Star
                          key={idx}
                          className={`w-3.5 h-3.5 ${
                            idx < (record.engagement_score || 0) ? "fill-yellow-500" : "text-border"
                          }`}
                        />
                      ))}
                    </div>
                  )}
                  {showActions && (
                    <div className="flex items-center gap-1.5 ml-2 border-l border-border/80 pl-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onEdit?.(record)}
                        title="Editar Registro"
                        className="p-1 h-7 w-7 flex items-center justify-center"
                      >
                        <Edit2 className="w-3 h-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleToggleActive(record.id)}
                        isLoading={loadingId === record.id}
                        title={isActive ? "Inativar Registro" : "Reativar Registro"}
                        className={`p-1 h-7 w-7 flex items-center justify-center ${isActive ? "text-error hover:bg-error/10" : "text-ok hover:bg-ok/10"}`}
                      >
                        {isActive ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                      </Button>
                    </div>
                  )}
                </div>
              </div>

              <p className="text-sm text-text-primary mb-3 leading-relaxed">
                {record.summary}
              </p>

              {record.observed_skills && (
                <div className="flex flex-wrap gap-1 items-center mb-3">
                  <Award className="w-3.5 h-3.5 text-secondary mr-1" />
                  {record.observed_skills.split(",").map((skill, idx) => (
                    <Badge key={idx} variant="secondary" className="text-[10px]">
                      {skill.trim()}
                    </Badge>
                  ))}
                </div>
              )}

              {record.suggestions && record.suggestions.length > 0 && (
                <div className="border-t border-border/80 pt-2 mt-2">
                  <span className="block text-[10px] font-bold text-secondary uppercase tracking-wider mb-1 flex items-center gap-1">
                    <Compass className="w-3.5 h-3.5" /> Sugestões de Interação Familiar
                  </span>
                  <ul className="list-disc pl-4 text-xs text-text-muted flex flex-col gap-1">
                    {record.suggestions.map((sug) => (
                      <li key={sug.id}>{sug.suggestion_text}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
