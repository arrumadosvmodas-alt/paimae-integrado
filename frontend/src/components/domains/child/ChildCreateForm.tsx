import React, { useState, useEffect } from "react";
import { Card } from "../../ui/Card";
import { Input, Select } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { UserPlus, X } from "lucide-react";
import type { School } from "../../../lib/types";

interface ChildCreateFormProps {
  schools: School[];
  onSubmit: (payload: {
    id?: string;
    full_name: string;
    birth_date: string | null;
    school_id: string;
    class_name: string | null;
  }) => Promise<void>;
  childToEdit?: any | null;
  onCancelEdit?: () => void;
}

export function ChildCreateForm({ schools, onSubmit, childToEdit, onCancelEdit }: ChildCreateFormProps) {
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [schoolId, setSchoolId] = useState("");
  const [classNameVal, setClassNameVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (childToEdit) {
      setFullName(childToEdit.full_name || "");
      setBirthDate(childToEdit.birth_date || "");
      setSchoolId(childToEdit.school_id || "");
      setClassNameVal(childToEdit.class_name || "");
    } else {
      setFullName("");
      setBirthDate("");
      setSchoolId(schools.length > 0 ? schools[0].id : "");
      setClassNameVal("");
    }
  }, [childToEdit, schools]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!fullName.trim() || !schoolId) return;

    setIsLoading(true);
    try {
      if (childToEdit) {
        await onSubmit({
          id: childToEdit.id,
          full_name: fullName.trim(),
          birth_date: birthDate || null,
          school_id: schoolId,
          class_name: classNameVal.trim() || null,
        });
      } else {
        await onSubmit({
          full_name: fullName.trim(),
          birth_date: birthDate || null,
          school_id: schoolId,
          class_name: classNameVal.trim() || null,
        });
        setFullName("");
        setBirthDate("");
        setSchoolId("");
        setClassNameVal("");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card 
      title={childToEdit ? "Editar Criança" : "Nova Criança"} 
      icon={<UserPlus className="w-5 h-5 text-primary" />}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Nome Completo *"
          placeholder="Ex: João Silva Santos"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
          disabled={isLoading}
        />
        <Input
          label="Data de Nascimento"
          type="date"
          value={birthDate}
          onChange={(e) => setBirthDate(e.target.value)}
          disabled={isLoading}
        />
        <Select
          label="Escola *"
          value={schoolId}
          onChange={(e) => setSchoolId(e.target.value)}
          placeholder="Selecione a escola"
          required
          disabled={isLoading}
        >
          {schools.map((school) => (
            <option key={school.id} value={school.id}>
              {school.name}
            </option>
          ))}
        </Select>
        <Input
          label="Turma (opcional)"
          placeholder="Ex: Maternal II - B"
          value={classNameVal}
          onChange={(e) => setClassNameVal(e.target.value)}
          disabled={isLoading}
        />
        
        <div className="flex gap-2">
          {childToEdit && (
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
            {childToEdit ? "Salvar Alterações" : "Cadastrar Criança"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
