import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Input, Textarea } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { api } from "../../../lib/api";
import { BookOpen, Search, Plus, Trash2 } from "lucide-react";
import type { MaterialItem } from "../../../lib/types";

interface PedagogicalMaterialFormProps {
  schoolId?: string;
  onSubmit: (payload: any) => Promise<void>;
  notify: (msg: string, type?: "ok" | "error") => void;
}

export function PedagogicalMaterialForm({ schoolId, onSubmit, notify }: PedagogicalMaterialFormProps) {
  const [isbn, setIsbn] = useState("");
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [subject, setSubject] = useState("");
  const [pedagogicalLine, setPedagogicalLine] = useState("");
  const [objectives, setObjectives] = useState("");
  const [familyOrientation, setFamilyOrientation] = useState("");
  const [isLoadingISBN, setIsLoadingISBN] = useState(false);
  const [isLoadingSubmit, setIsLoadingSubmit] = useState(false);

  // Itens do livro (Capítulos, páginas)
  const [items, setItems] = useState<Array<{ chapter: string; page: string; theme: string; description: string }>>([]);
  const [newItemTheme, setNewItemTheme] = useState("");
  const [newItemChapter, setNewItemChapter] = useState("");
  const [newItemPage, setNewItemPage] = useState("");

  const handleLookupISBN = async () => {
    if (!isbn.trim()) return;
    setIsLoadingISBN(true);
    try {
      const res = await api<{ resolved: boolean; isbn: string; data: any }>(`/api/v1/pedagogy/isbn/${isbn.trim()}`);
      if (res.resolved && res.data) {
        setTitle(res.data.title || "");
        setAuthor(res.data.author || "");
        setSubject(res.data.subject || "");
        setPedagogicalLine(res.data.pedagogical_line || "");
        setObjectives(res.data.objectives || "");
        setFamilyOrientation(res.data.family_orientation || "");
        notify("ISBN resolvido com sucesso! Dados preenchidos.", "ok");
      }
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao buscar ISBN.", "error");
    } finally {
      setIsLoadingISBN(false);
    }
  };

  const handleAddItem = () => {
    if (!newItemTheme.trim()) return;
    setItems([...items, {
      theme: newItemTheme.trim(),
      chapter: newItemChapter.trim(),
      page: newItemPage.trim(),
      description: ""
    }]);
    setNewItemTheme("");
    setNewItemChapter("");
    setNewItemPage("");
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!schoolId || !title.trim() || !subject.trim() || !pedagogicalLine.trim()) {
      notify("Preencha todos os campos obrigatórios: Título, Matéria e Linha Pedagógica.", "error");
      return;
    }

    setIsLoadingSubmit(true);
    try {
      await onSubmit({
        school_id: schoolId,
        title: title.trim(),
        author: author.trim() || null,
        isbn: isbn.trim() || null,
        subject: subject.trim(),
        pedagogical_line: pedagogicalLine.trim(),
        objectives: objectives.trim() || null,
        family_orientation: familyOrientation.trim() || null,
        items: items
      });
      setTitle("");
      setAuthor("");
      setIsbn("");
      setSubject("");
      setPedagogicalLine("");
      setObjectives("");
      setFamilyOrientation("");
      setItems([]);
    } finally {
      setIsLoadingSubmit(false);
    }
  };

  return (
    <Card title="Adicionar Material Didático" icon={<BookOpen className="w-5 h-5 text-primary" />}>
      <div className="flex gap-2 mb-4 items-end">
        <div className="flex-1">
          <Input
            label="Buscar por ISBN (Opcional)"
            placeholder="Ex: 9788532283215"
            value={isbn}
            onChange={(e) => setIsbn(e.target.value)}
            disabled={isLoadingISBN || isLoadingSubmit || !schoolId}
          />
        </div>
        <Button
          onClick={handleLookupISBN}
          disabled={isLoadingISBN || !isbn.trim() || !schoolId}
          className="h-10 px-3 flex items-center gap-1.5"
          variant="outline"
        >
          <Search className="w-4 h-4" />
          {isLoadingISBN ? "Buscando..." : "Buscar"}
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Título do Livro/Material *"
          placeholder="Ex: Coleção Estrelas Vol. 1"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          disabled={isLoadingSubmit || !schoolId}
        />
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Autor"
            placeholder="Ex: Ana Clara"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            disabled={isLoadingSubmit || !schoolId}
          />
          <Input
            label="Componente Curricular / Assunto *"
            placeholder="Ex: Português"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
            disabled={isLoadingSubmit || !schoolId}
          />
        </div>
        <Input
          label="Linha Pedagógica / Metodologia *"
          placeholder="Ex: Construtivista, Tradicional"
          value={pedagogicalLine}
          onChange={(e) => setPedagogicalLine(e.target.value)}
          required
          disabled={isLoadingSubmit || !schoolId}
        />
        <Textarea
          label="Objetivos de Aprendizagem"
          placeholder="Ex: Compreender as quatro operações matemáticas básicas..."
          value={objectives}
          onChange={(e) => setObjectives(e.target.value)}
          disabled={isLoadingSubmit || !schoolId}
        />
        <Textarea
          label="Orientação para a Família"
          placeholder="Ex: Praticar contagem de brinquedos no cotidiano..."
          value={familyOrientation}
          onChange={(e) => setFamilyOrientation(e.target.value)}
          disabled={isLoadingSubmit || !schoolId}
        />

        {/* Adição de itens específicos do livro */}
        <div className="border border-border p-4 rounded-xl bg-background/30 flex flex-col gap-3">
          <span className="block text-xs font-bold text-text-primary uppercase tracking-wider">
            Capítulos e Páginas do Material (Itens Didáticos)
          </span>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 items-end">
            <Input
              label="Tema / Habilidade *"
              placeholder="Ex: Multiplicação Simples"
              value={newItemTheme}
              onChange={(e) => setNewItemTheme(e.target.value)}
              disabled={!schoolId}
            />
            <Input
              label="Capítulo"
              placeholder="Ex: Cap. 2"
              value={newItemChapter}
              onChange={(e) => setNewItemChapter(e.target.value)}
              disabled={!schoolId}
            />
            <Input
              label="Página"
              placeholder="Ex: p. 45-50"
              value={newItemPage}
              onChange={(e) => setNewItemPage(e.target.value)}
              disabled={!schoolId}
            />
          </div>
          <Button
            type="button"
            onClick={handleAddItem}
            disabled={!newItemTheme.trim() || !schoolId}
            variant="outline"
            className="w-full flex items-center justify-center gap-1 mt-1"
          >
            <Plus className="w-4 h-4" /> Adicionar Item ao Livro
          </Button>

          {items.length > 0 && (
            <ul className="mt-2 flex flex-col gap-1.5 max-h-32 overflow-y-auto">
              {items.map((item, idx) => (
                <li key={idx} className="flex justify-between items-center text-xs p-2 bg-surface border border-border rounded-lg">
                  <div>
                    <span className="font-bold">{item.theme}</span>
                    {item.chapter && <span className="text-text-muted"> - {item.chapter}</span>}
                    {item.page && <span className="text-text-muted"> ({item.page})</span>}
                  </div>
                  <button type="button" onClick={() => handleRemoveItem(idx)} className="text-error hover:text-red-700">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <Button
          type="submit"
          isLoading={isLoadingSubmit}
          disabled={!schoolId}
          className="w-full mt-2"
        >
          {schoolId ? "Cadastrar Material Didático" : "Selecione uma escola primeiro"}
        </Button>
      </form>
    </Card>
  );
}
