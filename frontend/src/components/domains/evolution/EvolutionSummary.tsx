import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Button } from "../../ui/Button";
import { Sparkles, BrainCircuit } from "lucide-react";

interface EvolutionSummaryProps {
  childId?: string;
  summaryText: string;
  onGenerateSummary: () => Promise<void>;
}

export function EvolutionSummary({
  childId,
  summaryText,
  onGenerateSummary,
}: EvolutionSummaryProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerate = async () => {
    if (!childId) return;
    setIsLoading(true);
    try {
      await onGenerateSummary();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card title="Evolução & IA" icon={<BrainCircuit className="w-5 h-5 text-primary" />}>
      <div className="flex flex-col gap-4">
        <p className="text-xs text-text-muted">
          Gere um resumo inteligente baseado nos eventos de evolução registrados para esta criança. A IA consolidará o histórico em uma análise comportamental e pedagógica.
        </p>

        <Button
          variant="secondary"
          onClick={handleGenerate}
          disabled={!childId || isLoading}
          isLoading={isLoading}
          className="w-full flex items-center justify-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          Gerar Resumo da Criança
        </Button>

        {summaryText && (
          <div className="mt-2 p-4 bg-primary/5 dark:bg-primary/10 border border-primary/20 rounded-xl relative overflow-hidden flex flex-col gap-2">
            <div className="flex items-center gap-1.5 text-xs text-primary font-bold">
              <Sparkles className="w-4 h-4 text-primary animate-pulse" />
              <span>Análise Consolidada por IA</span>
            </div>
            <p className="text-sm text-text-primary leading-relaxed whitespace-pre-wrap">
              {summaryText}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
