import React, { useState, useEffect } from "react";
import { Card } from "../../ui/Card";
import { Input, Select } from "../../ui/Input";
import { Button } from "../../ui/Button";
import { Users, X } from "lucide-react";
import type { School, User } from "../../../lib/types";

interface UserCreateFormProps {
  schools: School[];
  userToEdit?: User | null;
  onCancelEdit?: () => void;
  onSubmit: (payload: any) => Promise<void>;
}

export function UserCreateForm({ schools, userToEdit, onCancelEdit, onSubmit }: UserCreateFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [document, setDocument] = useState("");
  const [role, setRole] = useState("guardian");
  const [schoolId, setSchoolId] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (userToEdit) {
      setName(userToEdit.name || "");
      setEmail(userToEdit.email || "");
      setPassword(""); // Don't preload hashed password
      setDocument(userToEdit.document || "");
      setRole(userToEdit.role || "guardian");
      setSchoolId(userToEdit.school_id || "");
    } else {
      setName("");
      setEmail("");
      setPassword("");
      setDocument("");
      setRole("guardian");
      setSchoolId("");
    }
  }, [userToEdit]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!name.trim() || !email.trim()) return;
    if (!userToEdit && role === "admin" && !password.trim()) return;

    setIsLoading(true);
    try {
      if (userToEdit) {
        await onSubmit({
          id: userToEdit.id,
          name: name.trim(),
          email: email.trim(),
          password: password.trim() || undefined,
          role: role,
          school_id: role === "guardian" || role === "admin" ? null : schoolId || null,
          document: role === "admin" ? document.trim() : null,
        });
      } else {
        await onSubmit({
          name: name.trim(),
          email: email.trim(),
          password: password.trim() || undefined,
          role: role,
          school_id: role === "guardian" || role === "admin" ? null : schoolId || null,
          document: role === "admin" ? document.trim() : null,
        });
        setName("");
        setEmail("");
        setPassword("");
        setDocument("");
        setRole("guardian");
        setSchoolId("");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card 
      title={userToEdit ? "Editar Usuário" : "Novo Usuário / Responsável"} 
      icon={<Users className="w-5 h-5 text-primary" />}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Nome Completo *"
          placeholder="Ex: João da Silva"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          disabled={isLoading}
        />
        <Input
          label="E-mail *"
          type="email"
          placeholder="Ex: joao@gmail.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={isLoading}
        />
        <Input
          label={userToEdit ? "Nova Senha (deixe em branco para manter)" : role === "admin" ? "Senha *" : "Senha (Opcional - usuário definirá no Primeiro Acesso)"}
          type="password"
          placeholder={userToEdit ? "Mínimo 8 caracteres" : "Mínimo 8 caracteres"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required={!userToEdit && role === "admin"}
          disabled={isLoading}
        />
        
        <Select
          label="Perfil / Nível de Acesso *"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          required
          disabled={isLoading}
        >
          <option value="guardian">Responsável (Pai/Mãe)</option>
          <option value="teacher">Professor</option>
          <option value="school_admin">Escola (Gestor)</option>
          <option value="admin">Administrador Geral</option>
        </Select>

        {role === "admin" && (
          <Input
            label="CPF do Administrador *"
            placeholder="Apenas números ou formatado (ex: 000.000.000-00)"
            value={document}
            onChange={(e) => setDocument(e.target.value)}
            required
            disabled={isLoading}
          />
        )}

        {(role === "teacher" || role === "school_admin") && schools.length > 0 && (
          <Select
            label="Vincular à Escola *"
            value={schoolId}
            onChange={(e) => setSchoolId(e.target.value)}
            required
            disabled={isLoading}
          >
            <option value="">Selecione uma escola</option>
            {schools.map((school) => (
              <option key={school.id} value={school.id}>
                {school.name}
              </option>
            ))}
          </Select>
        )}

        <div className="flex gap-2">
          {userToEdit && (
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
            {userToEdit ? "Salvar Alterações" : "Cadastrar Usuário"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
