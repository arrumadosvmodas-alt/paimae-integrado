import React, { useState } from "react";
import { Send, Loader, CheckCircle, MessageSquare } from "lucide-react";
import { Card } from "../../ui/Card";
import { Button } from "../../ui/Button";
import { Input } from "../../ui/Input";
import { Toast } from "../../ui/Toast";
import {
  createInteractionResponse,
  evaluateResponse,
  getPersonalizedFeedback,
} from "../../../services/apiServices";
import type { Interaction } from "../../../lib/types";

interface InteractionCardProps {
  interaction: Interaction;
  onResponseSubmitted?: () => void;
  showFeedback?: boolean;
}

export function InteractionCard({
  interaction,
  onResponseSubmitted,
  showFeedback = false,
}: InteractionCardProps) {
  const [responseText, setResponseText] = useState("");
  const [responseScore, setResponseScore] = useState(3);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleSubmitResponse = async () => {
    if (!responseText.trim()) {
      setToastMessage("⚠️ Digite uma resposta");
      return;
    }

    setSubmitting(true);

    try {
      // Registrar resposta
      const response = await createInteractionResponse(interaction.id, {
        responder_type: interaction.recipient_type,
        response_text: responseText,
        response_score: responseScore,
        responded_at: new Date().toISOString().split("T")[0],
      });

      // Se showFeedback, avaliar com IA
      if (showFeedback && response.id) {
        setEvaluating(true);
        try {
          const feedbackData = await getPersonalizedFeedback(
            interaction.child_id,
            responseScore,
            interaction.context_json?.theme || "Desconhecido"
          );
          setFeedback(feedbackData.feedback);
        } catch (err) {
          console.error("Erro ao gerar feedback:", err);
        }
      }

      setSubmitted(true);
      setToastMessage("✅ Resposta registrada com sucesso!");
      onResponseSubmitted?.();
    } catch (err) {
      setToastMessage("❌ Erro ao registrar resposta");
      console.error(err);
    } finally {
      setSubmitting(false);
      setEvaluating(false);
    }
  };

  const recipientLabel =
    interaction.recipient_type === "child" ? "👧 Para a Criança" : "👨‍👩‍👧 Para os Pais";

  return (
    <div className="space-y-4">
      <Card
        className={`p-4 ${interaction.status === "sent" ? "border-blue-200 bg-blue-50" : "border-gray-200"}`}
      >
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-gray-600 flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            {recipientLabel}
          </span>
          <span
            className={`text-xs px-2 py-1 rounded ${
              interaction.status === "sent"
                ? "bg-green-100 text-green-700"
                : interaction.status === "read"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-700"
            }`}
          >
            {interaction.status === "sent"
              ? "Enviada"
              : interaction.status === "read"
                ? "Lida"
                : "Pendente"}
          </span>
        </div>

        <div className="bg-white p-3 rounded-lg mb-3 border">
          <p className="text-gray-800 whitespace-pre-wrap">{interaction.message}</p>
        </div>

        {submitted ? (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2 text-green-700 text-sm">
              <CheckCircle className="w-4 h-4" />
              Resposta registrada!
            </div>
            {feedback && (
              <div className="mt-2 text-sm text-gray-700 bg-white p-2 rounded border border-green-100">
                <p className="font-semibold text-green-700 mb-1">💭 Feedback Personalizado:</p>
                <p>{feedback}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sua Resposta:
              </label>
              <textarea
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                placeholder="Escreva sua resposta aqui..."
                className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                disabled={submitting}
              />
            </div>

            {interaction.recipient_type === "child" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Como você se avalia? (1-5)
                </label>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((score) => (
                    <button
                      key={score}
                      onClick={() => setResponseScore(score)}
                      disabled={submitting}
                      className={`flex-1 py-2 px-1 rounded text-sm font-semibold transition ${
                        responseScore === score
                          ? "bg-blue-500 text-white"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      }`}
                    >
                      {score === 1
                        ? "😞"
                        : score === 2
                          ? "😐"
                          : score === 3
                            ? "🙂"
                            : score === 4
                              ? "😊"
                              : "🎉"}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <Button
              onClick={handleSubmitResponse}
              disabled={submitting || evaluating || !responseText.trim()}
              variant="primary"
              className="w-full flex items-center justify-center gap-2"
            >
              {submitting || evaluating ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  {evaluating ? "Gerando feedback..." : "Enviando..."}
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Enviar Resposta
                </>
              )}
            </Button>
          </div>
        )}
      </Card>

      {toastMessage && (
        <Toast
          message={toastMessage}
          type={toastMessage.includes("❌") ? "error" : "success"}
        />
      )}
    </div>
  );
}
