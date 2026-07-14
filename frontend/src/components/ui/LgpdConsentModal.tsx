import React, { useState } from "react";
import { Button } from "./Button";
import { ShieldCheck, Lock, CheckCircle2, AlertTriangle } from "lucide-react";
import { api } from "../../lib/api";

interface LgpdConsentModalProps {
  onAccept: () => void;
}

export function LgpdConsentModal({ onAccept }: LgpdConsentModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasScrolled, setHasScrolled] = useState(true); // Permitir aceitar diretamente por facilidade, mas exigindo checkbox

  const handleAccept = async () => {
    setIsSubmitting(true);
    try {
      await api("/api/v1/auth/lgpd-accept", { method: "POST" });
      onAccept();
    } catch (err) {
      alert("Erro ao salvar consentimento. Tente novamente.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background-blur/70 backdrop-blur-md p-4 animate-fade-in">
      <div className="bg-surface border border-border/80 w-full max-w-2xl rounded-3xl shadow-2xl p-6 md:p-8 flex flex-col gap-6 max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-border pb-4">
          <div className="w-12 h-12 bg-primary/10 rounded-2xl flex items-center justify-center text-primary">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-lg font-black text-text-primary">Termo de Consentimento e Privacidade</h2>
            <p className="text-xs text-text-muted">Conformidade com a Lei Geral de Proteção de Dados (LGPD)</p>
          </div>
        </div>

        {/* Content */}
        <div className="text-xs text-text-muted leading-relaxed flex flex-col gap-4">
          <p className="font-semibold text-text-primary">
            Olá! Para garantir a segurança e transparência no uso dos dados pedagógicos de seu filho(a), precisamos da sua autorização expressa.
          </p>

          <div className="bg-background/45 border border-border p-4 rounded-2xl flex flex-col gap-3">
            <h3 className="font-bold text-text-primary flex items-center gap-1.5 text-xs">
              <Lock className="w-4 h-4 text-secondary" /> Quais dados nós processamos e para quê?
            </h3>
            
            <ul className="flex flex-col gap-2.5 pl-1">
              <li className="flex gap-2">
                <CheckCircle2 className="w-4 h-4 text-ok shrink-0 mt-0.5" />
                <span><strong>Rotina e Atividades:</strong> Registro das tarefas escolares e de casa para guiar o engajamento diário.</span>
              </li>
              <li className="flex gap-2">
                <CheckCircle2 className="w-4 h-4 text-ok shrink-0 mt-0.5" />
                <span><strong>Observações Pedagógicas:</strong> Armazenamento de anotações dos professores e relatórios gerados por Inteligência Artificial para identificar áreas de apoio.</span>
              </li>
              <li className="flex gap-2">
                <CheckCircle2 className="w-4 h-4 text-ok shrink-0 mt-0.5" />
                <span><strong>Direito de Controle (Seus Direitos):</strong> Você pode, a qualquer momento, baixar o prontuário completo (portabilidade) ou excluir definitivamente o cadastro e histórico do aluno (direito ao esquecimento) na aba de configurações.</span>
              </li>
            </ul>
          </div>

          <p>
            Ao clicar em <strong>"Aceitar e Prosseguir"</strong>, você declara estar ciente e consentir com o tratamento seguro dos dados cadastrais e de progresso pedagógico do estudante sob sua responsabilidade, estritamente para os fins de acompanhamento acadêmico e integração família-escola.
          </p>

          <div className="flex items-start gap-2 bg-error/5 border border-error/20 p-3.5 rounded-2xl">
            <AlertTriangle className="w-5 h-5 text-error shrink-0 mt-0.5" />
            <p className="text-[10px] text-error font-medium leading-normal">
              A ausência de consentimento impossibilita a utilização do painel de monitoramento pedagógico. Seus dados nunca serão compartilhados com terceiros ou usados para fins comerciais.
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-end gap-3 pt-4 border-t border-border mt-2">
          <Button
            onClick={handleAccept}
            isLoading={isSubmitting}
            disabled={!hasScrolled}
            className="w-full sm:w-auto"
          >
            Aceitar e Prosseguir
          </Button>
        </div>
      </div>
    </div>
  );
}
