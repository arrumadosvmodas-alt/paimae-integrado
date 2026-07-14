import React, { useState, useEffect } from "react";
import { Card } from "../../ui/Card";
import { Input, Textarea } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { GraduationCap, X } from "lucide-react";
import type { School, PedagogicalMethodology } from "../../../lib/types";

const METHODOLOGIES = [
  "Aprendizagem Baseada em Projetos (ABP)",
  "Aprendizagem Baseada em Problemas (ABP)",
  "Sala de Aula Invertida (Flipped Classroom)",
  "Ensino Híbrido (Blended Learning)",
  "Ensino Tradicional",
  "Método Montessori",
  "Pedagogia Waldorf",
  "Pedagogia Freinet",
  "Aprendizagem Cooperativa",
  "Outra"
];

interface PedagogicalMethodologyFormProps {
  schoolId?: string;
  schools?: School[];
  methodologyToEdit?: PedagogicalMethodology | null;
  onCancelEdit?: () => void;
  onSubmit: (payload: any) => Promise<void>;
  notify: (msg: string, type?: "ok" | "error") => void;
}

export function PedagogicalMethodologyForm({
  schoolId: propSchoolId,
  schools = [],
  methodologyToEdit,
  onCancelEdit,
  onSubmit,
  notify,
}: PedagogicalMethodologyFormProps) {
  const [selectedSchoolId, setSelectedSchoolId] = useState(propSchoolId || "");
  const [methodologySelect, setMethodologySelect] = useState("Aprendizagem Baseada em Projetos (ABP)");
  const [customMethodology, setCustomMethodology] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (propSchoolId) {
      setSelectedSchoolId(propSchoolId);
    } else if (schools.length > 0 && !selectedSchoolId) {
      setSelectedSchoolId(schools[0].id);
    }
  }, [propSchoolId, schools]);

  useEffect(() => {
    if (methodologyToEdit) {
      setSelectedSchoolId(methodologyToEdit.school_id || "");
      const isPredefined = METHODOLOGIES.includes(methodologyToEdit.name || "");
      if (isPredefined) {
        setMethodologySelect(methodologyToEdit.name || "");
        setCustomMethodology("");
      } else {
        setMethodologySelect("Outra");
        setCustomMethodology(methodologyToEdit.name || "");
      }
      setDescription(methodologyToEdit.description || "");
    } else {
      setMethodologySelect("Aprendizagem Baseada em Projetos (ABP)");
      setCustomMethodology("");
      setDescription("");
    }
  }, [methodologyToEdit]);

  const activeSchoolId = selectedSchoolId || (schools.length > 0 ? schools[0].id : "");

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!activeSchoolId) {
      notify("Selecione ou cadastre uma escola primeiro.", "error");
      return;
    }
    const finalName = methodologySelect === "Outra" ? customMethodology.trim() : methodologySelect;
    if (!finalName) {
      notify("Preencha o nome da metodologia.", "error");
      return;
    }

    setIsLoading(true);
    try {
      if (methodologyToEdit) {
        await onSubmit({
          id: methodologyToEdit.id,
          school_id: activeSchoolId,
          name: finalName,
          description: description.trim() || null,
        });
      } else {
        await onSubmit({
          school_id: activeSchoolId,
          name: finalName,
          description: description.trim() || null,
        });
        setCustomMethodology("");
        setDescription("");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card 
      title={methodologyToEdit ? "Editar Metodologia" : "Nova Metodologia"} 
      icon={<GraduationCap className="w-5 h-5 text-primary" />}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {!propSchoolId && schools.length > 0 && (
          <div>
            <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-1.5">
              Escola *
            </label>
            <select
              value={activeSchoolId}
              onChange={(e) => setSelectedSchoolId(e.target.value)}
              disabled={isLoading}
              className="w-full h-10 px-3 border border-border rounded-lg bg-surface text-text-primary focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none transition-all duration-200 text-sm"
            >
              {schools.map((school) => (
                <option key={school.id} value={school.id}>
                  {school.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <div>
          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-1.5">
            Metodologia Pedagógica (Reconhecida MEC) *
          </label>
          <select
            value={methodologySelect}
            onChange={(e) => setMethodologySelect(e.target.value)}
            disabled={isLoading}
            className="w-full h-10 px-3 border border-border rounded-lg bg-surface text-text-primary focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none transition-all duration-200 text-sm"
          >
            {METHODOLOGIES.map((met) => (
              <option key={met} value={met}>
                {met}
              </option>
            ))}
          </select>
        </div>

        {methodologySelect === "Outra" && (
          <Input
            label="Especifique a Metodologia *"
            placeholder="Ex: Metodologia Ativa Personalizada"
            value={customMethodology}
            onChange={(e) => setCustomMethodology(e.target.value)}
            required
            disabled={isLoading}
          />
        )}

        <Textarea
          label="Descrição"
          placeholder="Ex: Foco na autonomia e liberdade com limites..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={isLoading}
        />

        <div className="flex gap-2">
          {methodologyToEdit && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancelEdit}
              disabled={isLoading}
              className="w-1/3 flex items-center justify-center gap-1"
            >
              <X className="w-4 h-4" /> Cancelar
            </Button>
          )}
          <Button type="submit" isLoading={isLoading} className="flex-1">
            {methodologyToEdit ? "Salvar Alterações" : "Cadastrar Metodologia"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
