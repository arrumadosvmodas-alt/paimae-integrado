import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Button } from "../../ui/Button";
import { Badge } from "../../ui/Badge";
import { MessageSquare, HelpCircle, Sparkles, AlertCircle } from "lucide-react";
import { api } from "../../../lib/api";

interface FamilyInteractionsProps {
  childId?: string;
  notify: (msg: string, type?: "ok" | "error") => void;
}

export function FamilyInteractions({ childId, notify }: FamilyInteractionsProps) {
  const [activeTab, setActiveTab] = useState<"conversation" | "question" | "guidance" | null>(null);
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerateInteraction = async (type: "conversation" | "question" | "guidance") => {
    if (!childId) return;
    setIsLoading(true);
    setActiveTab(type);
    setContent("");
    setStatus("");

    try {
      const res = await api<{ status: string; content: string }>("/api/v1/ai/interactions", {
        method: "POST",
        body: JSON.stringify({
          child_id: childId,
          interaction_type: type
        })
      });
      setStatus(res.status);
      setContent(res.content);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao gerar interação.", "error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card
      title="Interações da Família (IA)"
      subtitle="Sugestões sob demanda baseadas no dia escolar da criança"
      icon={<Sparkles className="w-5 h-5 text-primary" />}
    >
      <div className="flex flex-col gap-4">
        {/* Grade de botões rápidos */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
          <Button
            onClick={() => handleGenerateInteraction("conversation")}
            disabled={isLoading || !childId}
            variant={activeTab === "conversation" ? "primary" : "outline"}
            className="flex items-center justify-center gap-1.5 py-3 text-xs"
          >
            <MessageSquare className="w-4 h-4" />
            Gerar Conversa
          </Button>

          <Button
            onClick={() => handleGenerateInteraction("question")}
            disabled={isLoading || !childId}
            variant={activeTab === "question" ? "primary" : "outline"}
            className="flex items-center justify-center gap-1.5 py-3 text-xs"
          >
            <HelpCircle className="w-4 h-4" />
            Gerar Pergunta
          </Button>

          <Button
            onClick={() => handleGenerateInteraction("guidance")}
            disabled={isLoading || !childId}
            variant={activeTab === "guidance" ? "primary" : "outline"}
            className="flex items-center justify-center gap-1.5 py-3 text-xs"
          >
            <Sparkles className="w-4 h-4" />
            Gerar Reforço
          </Button>
        </div>

        {/* Painel de exibição do resultado */}
        {activeTab && (
          <div className="mt-2 border border-border p-4 rounded-xl bg-background/20 min-h-24 flex flex-col justify-center">
            {isLoading ? (
              <div className="flex flex-col items-center gap-2 text-text-muted py-4 text-xs">
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                Analisando dados e estruturando interação...
              </div>
            ) : status === "insufficient_data" ? (
              <div className="flex items-start gap-2.5 text-error text-xs bg-error/5 p-3 rounded-lg border border-error/15">
                <AlertCircle className="w-4.5 h-4.5 shrink-0 mt-0.5" />
                <span className="leading-relaxed">{content}</span>
              </div>
            ) : content ? (
              <div className="text-sm text-text-primary leading-relaxed whitespace-pre-line prose max-w-none">
                {content}
              </div>
            ) : (
              <div className="text-center text-text-muted text-xs py-4">
                Selecione uma opção acima para iniciar.
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
