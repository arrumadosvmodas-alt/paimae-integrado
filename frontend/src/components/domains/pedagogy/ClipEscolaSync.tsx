import { useEffect, useRef, useState } from "react";
import { QrCode, RefreshCw, Unlink } from "lucide-react";

import { Button } from "../../ui/Button";
import { Card } from "../../ui/Card";
import {
  disconnectClipEscola,
  getClipEscolaPairingStatus,
  getClipEscolaStatus,
  startClipEscolaPairing,
  syncClipEscolaNow,
  type ClipEscolaStatus,
} from "../../../services/apiServices";

type Notify = (msg: string, type?: "ok" | "error" | "info") => void;

interface ClipEscolaSyncProps {
  childId: string;
  notify: Notify;
}

const POLL_INTERVAL_MS = 4000;

export function ClipEscolaSync({ childId, notify }: ClipEscolaSyncProps) {
  const [status, setStatus] = useState<ClipEscolaStatus | null>(null);
  const [qrImage, setQrImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  function stopPolling() {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  async function loadStatus() {
    if (!childId) return;
    setLoading(true);
    try {
      const data = await getClipEscolaStatus(childId);
      setStatus(data);
      if (data.status === "active") {
        setQrImage(null);
        stopPolling();
      }
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao consultar status do ClipEscola.", "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setQrImage(null);
    stopPolling();
    loadStatus();
    return () => stopPolling();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [childId]);

  async function handleStartPairing() {
    if (!childId) return;
    setLoading(true);
    try {
      const result = await startClipEscolaPairing(childId);
      setQrImage(result.qr_image_base64);
      setStatus((current) => ({ ...(current as ClipEscolaStatus), account_id: result.account_id, status: "pending_pairing" }));

      stopPolling();
      pollRef.current = setInterval(async () => {
        try {
          const polled = await getClipEscolaPairingStatus(childId);
          setStatus(polled);
          if (polled.status === "active") {
            setQrImage(null);
            stopPolling();
            notify("ClipEscola conectado! A agenda será sincronizada automaticamente.");
          }
        } catch (error) {
          // erro pontual de rede durante o polling nao deve interromper a tentativa
        }
      }, POLL_INTERVAL_MS);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao iniciar pareamento com o ClipEscola.", "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleSyncNow() {
    if (!childId) return;
    setSyncing(true);
    try {
      const result = await syncClipEscolaNow(childId);
      if (result.status === "needs_reauth") {
        notify("Sessão do ClipEscola expirou. Escaneie o QR Code novamente.", "error");
        await loadStatus();
      } else {
        notify(`Sincronizado: ${result.schedules_created} novo(s) conteúdo(s) de estudo identificado(s).`);
      }
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao sincronizar agenda do ClipEscola.", "error");
    } finally {
      setSyncing(false);
    }
  }

  async function handleDisconnect() {
    if (!childId) return;
    setLoading(true);
    try {
      await disconnectClipEscola(childId);
      notify("ClipEscola desconectado.");
      setQrImage(null);
      stopPolling();
      await loadStatus();
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao desconectar ClipEscola.", "error");
    } finally {
      setLoading(false);
    }
  }

  const currentStatus = status?.status ?? "not_configured";

  return (
    <Card
      title="Agenda ClipEscola"
      subtitle="Conecta com seu login pessoal do ClipEscola e alimenta a rotina de estudos automaticamente"
      icon={<QrCode className="w-5 h-5 text-primary" />}
      headerActions={
        <Button variant="ghost" size="sm" onClick={loadStatus} disabled={!childId || loading} title="Atualizar">
          <RefreshCw className="w-4 h-4" />
        </Button>
      }
    >
      {currentStatus === "not_configured" && !qrImage && (
        <div className="flex flex-col gap-3">
          <p className="text-sm text-text-muted">
            Ainda nao conectado. Ao conectar, o app ira ler os recados da Agenda da escola e criar
            automaticamente os conteudos de estudo do dia.
          </p>
          <Button onClick={handleStartPairing} isLoading={loading} disabled={!childId}>
            Conectar com QR Code
          </Button>
        </div>
      )}

      {(currentStatus === "pending_pairing" || qrImage) && (
        <div className="flex flex-col items-center gap-3 text-center">
          <p className="text-sm text-text-muted">
            Abra o app ClipEscola no celular do responsavel → Menu → <strong>Autorizar outros Aparelhos</strong> →{" "}
            <strong>Conectar um Aparelho</strong> → aponte para este QR Code.
          </p>
          {qrImage ? (
            <img
              src={`data:image/png;base64,${qrImage}`}
              alt="QR Code de pareamento do ClipEscola"
              className="w-48 h-48 rounded-lg border border-border"
            />
          ) : (
            <div className="flex flex-col items-center gap-2">
              <p className="text-xs text-text-muted">
                Nenhum QR Code ativo no momento (a tentativa anterior pode ter expirado).
              </p>
              <Button onClick={handleStartPairing} isLoading={loading} disabled={!childId}>
                Gerar novo QR Code
              </Button>
            </div>
          )}
        </div>
      )}

      {currentStatus === "needs_reauth" && (
        <div className="flex flex-col gap-3">
          <p className="text-sm text-warning font-bold">
            A sessão do ClipEscola expirou. Reconecte para continuar recebendo a agenda automaticamente.
          </p>
          <Button onClick={handleStartPairing} isLoading={loading} disabled={!childId}>
            Reconectar com QR Code
          </Button>
        </div>
      )}

      {currentStatus === "active" && (
        <div className="flex flex-col gap-3">
          <p className="text-sm text-text-primary">
            Conectado. {status?.last_synced_at ? `Última sincronização: ${new Date(status.last_synced_at).toLocaleString("pt-BR")}` : "Ainda não sincronizado."}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={handleSyncNow} isLoading={syncing} disabled={!childId}>
              Sincronizar agora
            </Button>
            <Button variant="outline" onClick={handleDisconnect} disabled={!childId || loading}>
              <Unlink className="w-4 h-4" /> Desconectar
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
