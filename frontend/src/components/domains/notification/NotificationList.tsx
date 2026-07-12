import React, { useState } from "react";
import { Card } from "../../ui/Card";
import { Button } from "../../ui/Button";
import { Badge } from "../../ui/Badge";
import { Bell, CheckCircle2, Clock } from "lucide-react";
import type { Notification } from "../../../lib/types";

interface NotificationListProps {
  notifications: Notification[];
  childId?: string;
  onGenerateToday: () => Promise<void>;
  onCompleteNotification: (id: string) => Promise<void>;
}

export function NotificationList({
  notifications,
  childId,
  onGenerateToday,
  onCompleteNotification,
}: NotificationListProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [completingIds, setCompletingIds] = useState<string[]>([]);

  const handleGenerate = async () => {
    if (!childId) return;
    setIsGenerating(true);
    try {
      await onGenerateToday();
    } finally {
      setIsGenerating(false);
    }
  };

  const handleComplete = async (id: string) => {
    setCompletingIds((prev) => [...prev, id]);
    try {
      await onCompleteNotification(id);
    } finally {
      setCompletingIds((prev) => prev.filter((item) => item !== id));
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case "completed":
      case "concluida":
      case "concluído":
        return <Badge variant="secondary">Concluída</Badge>;
      case "pending":
      case "pendente":
      case "scheduled":
      case "agendada":
        return <Badge variant="tertiary">Agendada</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const formatDateTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  const headerActions = (
    <Button
      size="sm"
      variant="outline"
      onClick={handleGenerate}
      disabled={!childId || isGenerating}
      isLoading={isGenerating}
    >
      Gerar Hoje
    </Button>
  );

  return (
    <Card
      title="Notificações"
      icon={<Bell className="w-5 h-5 text-primary" />}
      headerActions={headerActions}
    >
      {!notifications.length ? (
        <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
          <Bell className="w-12 h-12 text-text-muted/30 mb-3" />
          <p className="text-sm font-semibold text-text-muted">Sem notificações.</p>
          <p className="text-xs text-text-muted/70 mt-1 max-w-[240px]">
            Clique em "Gerar Hoje" para simular a criação automática baseada nas rotinas cadastradas.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {notifications.map((notif) => {
            const isCompleting = completingIds.includes(notif.id);
            const isCompleted = notif.status?.toLowerCase() === "completed" || notif.status?.toLowerCase() === "concluida";

            return (
              <div
                key={notif.id}
                className="p-4 border border-border bg-surface hover:bg-surface-hover/40 rounded-xl transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className="text-sm font-bold text-text-primary truncate">
                      {notif.title}
                    </h4>
                    {getStatusBadge(notif.status)}
                  </div>
                  {notif.message && (
                    <p className="text-xs text-text-muted mt-1">
                      {notif.message}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-2 text-xs text-text-muted">
                    <Clock className="w-3.5 h-3.5 text-primary" />
                    <span>{formatDateTime(notif.scheduled_at)}</span>
                  </div>
                </div>

                {!isCompleted && (
                  <div className="flex-shrink-0">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleComplete(notif.id)}
                      isLoading={isCompleting}
                      className="w-full md:w-auto"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                      Concluir
                    </Button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
