import React, { useState, useEffect } from "react";
import { Card } from "../../ui/Card";
import { Input } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { Bookmark, Plus, Edit2, Trash2, X, Check } from "lucide-react";
import type { PedagogicalMaterial, MaterialItem } from "../../../lib/types";

interface PedagogicalMaterialItemFormProps {
  materials: PedagogicalMaterial[];
  onSubmit: (materialId: string, payload: any) => Promise<void>;
  onDeleteItem: (itemId: string) => Promise<void>;
  onUpdateItem: (itemId: string, payload: any) => Promise<void>;
  notify: (msg: string, type?: "ok" | "error") => void;
}

export function PedagogicalMaterialItemForm({
  materials = [],
  onSubmit,
  onDeleteItem,
  onUpdateItem,
  notify,
}: PedagogicalMaterialItemFormProps) {
  const activeMaterials = materials.filter((m) => m.is_active !== false);

  const [selectedMaterialId, setSelectedMaterialId] = useState("");
  const [theme, setTheme] = useState("");
  const [chapter, setChapter] = useState("");
  const [page, setPage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Estado de Edição de Capítulo
  const [editingItem, setEditingItem] = useState<MaterialItem | null>(null);

  // Seleciona automaticamente o primeiro livro disponível na lista
  useEffect(() => {
    if (activeMaterials.length > 0 && !selectedMaterialId) {
      setSelectedMaterialId(activeMaterials[0].id);
    }
  }, [activeMaterials, selectedMaterialId]);

  // Busca o livro selecionado para listar seus capítulos atuais
  const selectedMaterial = activeMaterials.find((m) => m.id === selectedMaterialId);
  const currentItems = selectedMaterial?.items || [];

  const handleEditClick = (item: MaterialItem) => {
    setEditingItem(item);
    setTheme(item.theme);
    setChapter(item.chapter || "");
    setPage(item.page || "");
  };

  const handleCancelEdit = () => {
    setEditingItem(null);
    setTheme("");
    setChapter("");
    setPage("");
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedMaterialId) {
      notify("Selecione um livro primeiro.", "error");
      return;
    }
    if (!theme.trim()) {
      notify("Preencha o campo Tema / Habilidade.", "error");
      return;
    }

    setIsLoading(true);
    try {
      if (editingItem) {
        // Modo Edição
        await onUpdateItem(editingItem.id, {
          theme: theme.trim(),
          chapter: chapter.trim() || null,
          page: page.trim() || null,
          description: null,
        });
        setEditingItem(null);
        notify("Capítulo atualizado com sucesso!", "ok");
      } else {
        // Modo Criação
        await onSubmit(selectedMaterialId, {
          theme: theme.trim(),
          chapter: chapter.trim() || null,
          page: page.trim() || null,
          description: null,
        });
        notify("Capítulo vinculado com sucesso!", "ok");
      }
      setTheme("");
      setChapter("");
      setPage("");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao processar requisição.", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (itemId: string) => {
    if (window.confirm("Deseja realmente excluir este capítulo?")) {
      setIsLoading(true);
      try {
        await onDeleteItem(itemId);
        notify("Capítulo excluído com sucesso!", "ok");
        if (editingItem?.id === itemId) {
          handleCancelEdit();
        }
      } catch (error) {
        notify(error instanceof Error ? error.message : "Erro ao excluir capítulo.", "error");
      } finally {
        setIsLoading(false);
      }
    }
  };

  if (activeMaterials.length === 0) {
    return (
      <Card title="Vincular Capítulo ao Livro" icon={<Bookmark className="w-5 h-5 text-primary" />}>
        <div className="text-center py-6 text-text-muted text-xs">
          Nenhum livro cadastrado ou ativo para esta escola. Cadastre um livro primeiro.
        </div>
      </Card>
    );
  }

  return (
    <Card title={editingItem ? "Editar Capítulo" : "Vincular Capítulo ao Livro"} icon={<Bookmark className="w-5 h-5 text-primary" />}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-1.5">
            Selecione o Livro *
          </label>
          <select
            value={selectedMaterialId}
            onChange={(e) => {
              setSelectedMaterialId(e.target.value);
              handleCancelEdit();
            }}
            disabled={isLoading || !!editingItem}
            className="w-full h-10 px-3 border border-border rounded-lg bg-surface text-text-primary focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none transition-all duration-200 text-sm"
          >
            {activeMaterials.map((material) => (
              <option key={material.id} value={material.id}>
                {material.title} ({material.subject})
              </option>
            ))}
          </select>
        </div>

        <Input
          label="Tema / Habilidade *"
          placeholder="Ex: Multiplicação Simples"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          required
          disabled={isLoading}
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Capítulo"
            placeholder="Ex: Cap. 2"
            value={chapter}
            onChange={(e) => setChapter(e.target.value)}
            disabled={isLoading}
          />
          <Input
            label="Página"
            placeholder="Ex: p. 45-50"
            value={page}
            onChange={(e) => setPage(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="flex gap-2 mt-2">
          {editingItem && (
            <Button
              type="button"
              variant="outline"
              onClick={handleCancelEdit}
              disabled={isLoading}
              className="w-1/3 flex items-center justify-center gap-1"
            >
              <X className="w-4 h-4" /> Cancelar
            </Button>
          )}
          <Button type="submit" isLoading={isLoading} className="flex-1 flex items-center justify-center gap-1.5">
            {editingItem ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {editingItem ? "Salvar Alterações do Capítulo" : "Vincular Capítulo"}
          </Button>
        </div>
      </form>

      {/* Consulta de Capítulos Vinculados */}
      <div className="mt-6 pt-6 border-t border-border">
        <span className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-3">
          Capítulos Vinculados a este Livro ({currentItems.length})
        </span>

        {currentItems.length === 0 ? (
          <div className="text-center py-4 text-text-muted text-xs">
            Nenhum capítulo cadastrado para este livro ainda.
          </div>
        ) : (
          <div className="flex flex-col gap-2 max-h-48 overflow-y-auto">
            {currentItems.map((item) => (
              <div
                key={item.id}
                className={`flex justify-between items-center p-2.5 border rounded-xl text-xs transition-colors ${
                  editingItem?.id === item.id
                    ? "border-primary bg-primary/5"
                    : "border-border bg-background/25 hover:bg-background/45"
                }`}
              >
                <div>
                  <span className="font-bold text-text-primary">{item.theme}</span>
                  {item.chapter && <span className="text-text-muted"> • {item.chapter}</span>}
                  {item.page && <span className="text-text-muted"> ({item.page})</span>}
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => handleEditClick(item)}
                    disabled={isLoading}
                    className="text-primary hover:text-blue-700 p-1 rounded hover:bg-primary/10 transition-colors"
                    title="Editar capítulo"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(item.id)}
                    disabled={isLoading}
                    className="text-error hover:text-red-700 p-1 rounded hover:bg-error/10 transition-colors"
                    title="Excluir capítulo"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
