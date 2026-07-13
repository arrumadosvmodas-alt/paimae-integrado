import React, { useState, useEffect } from "react";
import { Card } from "../../ui/Card";
import { Input } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { School, X } from "lucide-react";

interface SchoolCreateFormProps {
  onSubmit: (payload: { id?: string; name: string; document: string | null }) => Promise<void>;
  schoolToEdit?: any | null;
  onCancelEdit?: () => void;
}

export function SchoolCreateForm({ onSubmit, schoolToEdit, onCancelEdit }: SchoolCreateFormProps) {
  const [name, setName] = useState("");
  const [documentVal, setDocumentVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (schoolToEdit) {
      setName(schoolToEdit.name || "");
      setDocumentVal(schoolToEdit.document || "");
    } else {
      setName("");
      setDocumentVal("");
    }
  }, [schoolToEdit]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;

    setIsLoading(true);
    try {
      if (schoolToEdit) {
        await onSubmit({
          id: schoolToEdit.id,
          name: name.trim(),
          document: documentVal.trim() || null,
        });
      } else {
        await onSubmit({
          name: name.trim(),
          document: documentVal.trim() || null,
        });
        setName("");
        setDocumentVal("");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card 
      title={schoolToEdit ? "Editar Escola" : "Nova Escola"} 
      icon={<School className="w-5 h-5 text-primary" />}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Nome da escola *"
          placeholder="Ex: Colégio Primário"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          disabled={isLoading}
        />
        <Input
          label="CNPJ/Documento (opcional)"
          placeholder="Ex: 00.000.000/0001-00"
          value={documentVal}
          onChange={(e) => setDocumentVal(e.target.value)}
          disabled={isLoading}
        />
        
        <div className="flex gap-2">
          {schoolToEdit && (
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
            {schoolToEdit ? "Salvar Alterações" : "Cadastrar Escola"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
