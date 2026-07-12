import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Input, Select } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { UserPlus } from "lucide-react";
import type { School } from "../../../lib/types";

interface ChildCreateFormProps {
  schools: School[];
  onSubmit: (payload: {
    full_name: string;
    birth_date: string | null;
    school_id: string;
    class_name: string | null;
  }) => Promise<void>;
}

export function ChildCreateForm({ schools, onSubmit }: ChildCreateFormProps) {
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [schoolId, setSchoolId] = useState("");
  const [classNameVal, setClassNameVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!fullName.trim() || !schoolId) return;

    setIsLoading(true);
    try {
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
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card title="Nova Criança" icon={<UserPlus className="w-5 h-5 text-primary" />}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Nome Completo"
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
          label="Escola"
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
        <Button type="submit" isLoading={isLoading} className="w-full">
          Cadastrar Criança
        </Button>
      </form>
    </Card>
  );
}
