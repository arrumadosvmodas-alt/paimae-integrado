import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Badge } from "../../ui/Badge";
import { Button } from "../../ui/Button";
import { BookOpen, Edit2, EyeOff, Eye, Bookmark } from "lucide-react";
import type { PedagogicalMaterial } from "../../../lib/types";

interface PedagogicalMaterialListProps {
  materials: PedagogicalMaterial[];
  onEdit?: (material: PedagogicalMaterial) => void;
  onToggleActive?: (id: string) => Promise<void>;
  onDeleteItem?: (itemId: string) => Promise<void>;
  showActions?: boolean;
}

export function PedagogicalMaterialList({
  materials,
  onEdit,
  onToggleActive,
  onDeleteItem,
  showActions = false,
}: PedagogicalMaterialListProps) {
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

  if (materials.length === 0) {
    return (
      <Card title="Livros & Materiais Didáticos" icon={<BookOpen className="w-5 h-5 text-primary" />}>
        <div className="text-center py-6 text-text-muted text-xs">
          Nenhum material didático cadastrado para esta escola ainda.
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title={`Materiais Cadastrados (${materials.filter(m => m.is_active !== false).length})`} 
      icon={<BookOpen className="w-5 h-5 text-primary" />}
    >
      <div className="flex flex-col gap-4 max-h-[450px] overflow-y-auto pr-1">
        {materials.map((material) => {
          const isActive = material.is_active !== false;
          return (
            <div
              key={material.id}
              className={`border p-4 rounded-xl transition-all duration-200 ${
                isActive
                  ? "border-border bg-background/20 hover:bg-background/40"
                  : "border-border/50 bg-background/5 opacity-60"
              }`}
            >
              <div className="flex justify-between items-start gap-4 mb-2 flex-wrap">
                <div>
                  <h4 className="text-sm font-bold text-text-primary flex items-center gap-1.5 flex-wrap">
                    {material.title}
                    {!isActive && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-error/20 text-error uppercase">
                        Inativo
                      </span>
                    )}
                  </h4>
                  <span className="text-xs text-text-muted">
                    Por {material.author || "Autor Desconhecido"} • {material.subject}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {showActions && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onEdit?.(material)}
                        title="Editar Material"
                        className="p-1 h-7 w-7 flex items-center justify-center"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleToggleActive(material.id)}
                        isLoading={loadingId === material.id}
                        title={isActive ? "Inativar Livro" : "Reativar Livro"}
                        className={`p-1 h-7 w-7 flex items-center justify-center ${
                          isActive ? "text-error hover:bg-error/10" : "text-ok hover:bg-ok/10"
                        }`}
                      >
                        {isActive ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </Button>
                    </>
                  )}
                </div>
              </div>

              {material.isbn && (
                <div className="mb-2">
                  <span className="text-[10px] font-bold text-text-muted bg-surface border border-border px-1.5 py-0.5 rounded">
                    ISBN: {material.isbn}
                  </span>
                </div>
              )}

              {material.objectives && (
                <p className="text-xs text-text-muted line-clamp-2 mt-1">
                  <strong>Objetivos:</strong> {material.objectives}
                </p>
              )}

              {material.items && material.items.length > 0 && (
                <div className="mt-3 pt-2 border-t border-border/80">
                  <span className="block text-[10px] font-bold text-secondary uppercase tracking-wider mb-1.5 flex items-center gap-1">
                    <Bookmark className="w-3 h-3" /> Capítulos/Temas Cadastrados
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {material.items.map((it, idx) => (
                      <Badge key={idx} variant="tertiary" className="text-[9px] flex items-center gap-1">
                        <span>{it.chapter ? `${it.chapter}: ` : ""}{it.theme} {it.page ? `(p. ${it.page})` : ""}</span>
                        {showActions && onDeleteItem && (
                          <button
                            type="button"
                            onClick={() => onDeleteItem(it.id)}
                            className="ml-1 hover:text-error hover:bg-error/10 rounded-full w-3.5 h-3.5 flex items-center justify-center font-bold text-[10px] focus:outline-none transition-all duration-200"
                            title="Excluir capítulo"
                          >
                            ×
                          </button>
                        )}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
