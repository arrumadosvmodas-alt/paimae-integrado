import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Input } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { School } from "lucide-react";

interface SchoolCreateFormProps {
  onSubmit: (payload: { name: string; document: string | null }) => Promise<void>;
}

export function SchoolCreateForm({ onSubmit }: SchoolCreateFormProps) {
  const [name, setName] = useState("");
  const [documentVal, setDocumentVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;

    setIsLoading(true);
    try {
      await onSubmit({
        name: name.trim(),
        document: documentVal.trim() || null,
      });
      setName("");
      setDocumentVal("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card title="Nova Escola" icon={<School className="w-5 h-5 text-primary" />}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Nome da escola"
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
        <Button type="submit" isLoading={isLoading} className="w-full">
          Cadastrar Escola
        </Button>
      </form>
    </Card>
  );
}
