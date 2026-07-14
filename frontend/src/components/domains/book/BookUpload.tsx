import React, { useState, useRef } from "react";
import { Upload, FileText, Loader, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "../../ui/Button";
import { Card } from "../../ui/Card";
import { Toast } from "../../ui/Toast";
import { uploadBookFile, getMaterialProcessingStatus } from "../../../services/apiServices";

interface BookUploadProps {
  materialId: string;
  onUploadComplete?: (status: string) => void;
}

export function BookUpload({ materialId, onUploadComplete }: BookUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState<"idle" | "uploading" | "processing" | "complete" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError("Arquivo muito grande (máximo 50MB)");
        setToastMessage("Arquivo muito grande");
        return;
      }

      if (!["application/pdf", "image/jpeg", "image/png", "image/webp"].includes(selectedFile.type)) {
        setError("Tipo de arquivo não suportado. Use: PDF, JPEG, PNG ou WEBP");
        setToastMessage("Tipo de arquivo inválido");
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setStatus("uploading");
    setError(null);

    try {
      await uploadBookFile(materialId, file);
      setStatus("processing");
      setToastMessage("Arquivo enviado! Processando...");

      // Poll para verificar status
      let pollingAttempts = 0;
      const maxAttempts = 60; // 5 minutos com polling a cada 5s

      while (pollingAttempts < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 5000)); // Wait 5s

        try {
          const materialStatus = await getMaterialProcessingStatus(materialId);

          if (materialStatus.processing_status === "completed") {
            setStatus("complete");
            setToastMessage("✅ Livro processado com sucesso!");
            onUploadComplete?.("completed");
            break;
          } else if (materialStatus.processing_status === "failed") {
            setStatus("error");
            setError(materialStatus.processing_error || "Erro ao processar o arquivo");
            setToastMessage("❌ Erro ao processar");
            break;
          }

          pollingAttempts++;
        } catch (err) {
          pollingAttempts++;
        }
      }

      if (status === "processing") {
        setStatus("error");
        setError("Processamento demorou muito");
        setToastMessage("⏱️ Processamento demorou muito");
      }
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Erro ao fazer upload");
      setToastMessage("❌ Erro ao fazer upload");
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-lg">Upload do Livro</h3>
          </div>

          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="w-10 h-10 mx-auto mb-2 text-gray-400" />
            <p className="text-sm text-gray-600">
              Clique ou arraste um arquivo (PDF, JPEG, PNG, WEBP)
            </p>
            <p className="text-xs text-gray-500 mt-1">Máximo 50MB</p>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.jpg,.jpeg,.png,.webp"
              onChange={handleFileChange}
            />
          </div>

          {file && (
            <div className="bg-blue-50 p-3 rounded flex items-center justify-between">
              <span className="text-sm text-gray-700">{file.name}</span>
              <button
                onClick={() => {
                  setFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
                className="text-red-500 hover:text-red-700"
              >
                ✕
              </button>
            </div>
          )}

          {error && (
            <div className="bg-red-50 p-3 rounded flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {status === "complete" && (
            <div className="bg-green-50 p-3 rounded flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-700">Livro processado com sucesso! OCR e IA já analisaram o conteúdo.</p>
            </div>
          )}

          {status === "processing" && (
            <div className="bg-blue-50 p-3 rounded flex items-start gap-2">
              <Loader className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5 animate-spin" />
              <p className="text-sm text-blue-700">
                Processando: extração OCR + análise IA em andamento...
              </p>
            </div>
          )}

          <div className="flex gap-2">
            <Button
              onClick={handleUpload}
              disabled={!file || uploading || processing || status === "processing"}
              variant={file ? "primary" : "secondary"}
              className="flex-1"
            >
              {uploading ? "Enviando..." : processing || status === "processing" ? "Processando..." : "Fazer Upload"}
            </Button>
            {status === "complete" && (
              <Button
                onClick={() => {
                  setFile(null);
                  setStatus("idle");
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
                variant="secondary"
              >
                Upload Outro
              </Button>
            )}
          </div>
        </div>
      </Card>

      {toastMessage && (
        <Toast
          message={toastMessage}
          type={
            status === "complete"
              ? "success"
              : status === "error"
                ? "error"
                : "info"
          }
        />
      )}
    </>
  );
}
