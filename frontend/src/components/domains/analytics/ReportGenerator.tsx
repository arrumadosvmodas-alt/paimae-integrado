import React, { useRef, useState } from "react";
import { Download, FileText, Loader } from "lucide-react";
import { Card } from "../../ui/Card";
import { Button } from "../../ui/Button";
import { Toast } from "../../ui/Toast";
import { api } from "../../../lib/api";
import type { LearningMetrics, Child } from "../../../lib/types";

interface ReportGeneratorProps {
  childId: string;
  childData?: Child;
}

export function ReportGenerator({ childId, childData }: ReportGeneratorProps) {
  const [generating, setGenerating] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const reportRef = useRef<HTMLDivElement>(null);
  const [metrics, setMetrics] = useState<LearningMetrics | null>(null);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const metricsData = await api<LearningMetrics>(`/api/v1/learning/metrics?child_id=${childId}`);
      setMetrics(metricsData);
      setToast("✅ Relatório gerado com sucesso!");
    } catch (err) {
      setToast("❌ Erro ao gerar relatório");
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!reportRef.current || !metrics) return;

    try {
      const element = reportRef.current;
      const opt = {
        margin: 10,
        filename: `relatorio-${childData?.full_name || "aluno"}-${new Date().toLocaleDateString("pt-BR")}.pdf`,
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { orientation: "portrait", unit: "mm", format: "a4" },
      };

      // Usa html2pdf se estiver disponível, caso contrário usa print
      if (typeof (window as any).html2pdf !== "undefined") {
        (window as any).html2pdf().set(opt).from(element).save();
        setToast("✅ PDF baixado com sucesso!");
      } else {
        window.print();
        setToast("Usando impressão do navegador");
      }
    } catch (err) {
      setToast("❌ Erro ao gerar PDF");
      console.error(err);
    }
  };

  const handleExportJSON = () => {
    if (!metrics) return;

    const dataStr = JSON.stringify(metrics, null, 2);
    const dataUri = "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

    const exportFileDefaultName = `dados-${childData?.full_name || "aluno"}-${new Date().toLocaleDateString("pt-BR")}.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();

    setToast("✅ Dados exportados em JSON!");
  };

  const handleExportCSV = () => {
    if (!metrics) return;

    const rows = [
      ["Métrica", "Valor"],
      ["Taxa de Sucesso", `${Math.round(metrics.overall_success_rate * 100)}%`],
      ["Engajamento", `${metrics.average_engagement}/5`],
      ["Risco de Dropout", metrics.dropout_risk],
      ["Previsão Próximo Sucesso", `${Math.round(metrics.predicted_next_success_rate * 100)}%`],
      ["Temas Dominados", metrics.themes_mastered.join(", ")],
      ["Temas em Dificuldade", metrics.themes_struggling.join(", ")],
      ["Total de Atividades", metrics.total_activities],
      ["Atividades Bem-Sucedidas", metrics.successful_activities],
    ];

    let csvContent = "data:text/csv;charset=utf-8,";
    rows.forEach((row) => {
      csvContent += row.join(",") + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `dados-${childData?.full_name || "aluno"}.csv`);
    link.click();

    setToast("✅ Dados exportados em CSV!");
  };

  return (
    <>
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Gerador de Relatórios
          </h3>
        </div>

        <div className="space-y-3">
          <Button
            onClick={handleGenerateReport}
            disabled={generating}
            variant="primary"
            className="w-full flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Gerando relatório...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4" />
                Gerar Relatório
              </>
            )}
          </Button>

          {metrics && (
            <div className="space-y-2">
              <Button
                onClick={handleDownloadPDF}
                variant="secondary"
                className="w-full flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Baixar PDF
              </Button>

              <Button
                onClick={handleExportJSON}
                variant="secondary"
                className="w-full flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Exportar JSON
              </Button>

              <Button
                onClick={handleExportCSV}
                variant="secondary"
                className="w-full flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Exportar CSV
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Conteúdo oculto para PDF */}
      {metrics && (
        <div
          ref={reportRef}
          style={{ display: "none" }}
          className="p-8 bg-white"
        >
          <h1 className="text-3xl font-bold mb-2">
            Relatório de Aprendizagem — {childData?.full_name}
          </h1>
          <p className="text-gray-600 mb-8">
            Gerado em {new Date().toLocaleDateString("pt-BR")}
          </p>

          <div className="space-y-6">
            <div className="border-b pb-4">
              <h2 className="text-xl font-semibold mb-3">Resumo Executivo</h2>
              <p className="text-sm text-gray-700">
                Taxa de Sucesso: {Math.round(metrics.overall_success_rate * 100)}%
              </p>
              <p className="text-sm text-gray-700">
                Engajamento: {metrics.average_engagement}/5
              </p>
              <p className="text-sm text-gray-700">
                Risco de Dropout: {metrics.dropout_risk}
              </p>
            </div>

            <div className="border-b pb-4">
              <h2 className="text-xl font-semibold mb-3">Temas Dominados</h2>
              <p className="text-sm">
                {metrics.themes_mastered.length > 0
                  ? metrics.themes_mastered.join(", ")
                  : "Nenhum tema dominado ainda"}
              </p>
            </div>

            <div className="border-b pb-4">
              <h2 className="text-xl font-semibold mb-3">Temas em Dificuldade</h2>
              <p className="text-sm">
                {metrics.themes_struggling.length > 0
                  ? metrics.themes_struggling.join(", ")
                  : "Sem dificuldades identificadas"}
              </p>
            </div>

            <div className="border-b pb-4">
              <h2 className="text-xl font-semibold mb-3">Estatísticas</h2>
              <p className="text-sm">Total de Atividades: {metrics.total_activities}</p>
              <p className="text-sm">Bem-Sucedidas: {metrics.successful_activities}</p>
              <p className="text-sm">
                Previsão Próximo Sucesso: {Math.round(metrics.predicted_next_success_rate * 100)}%
              </p>
            </div>

            {metrics.recommendations.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold mb-3">Recomendações</h2>
                <ul className="text-sm list-disc pl-5">
                  {metrics.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {toast && (
        <Toast
          message={toast}
          type={toast.includes("❌") ? "error" : "success"}
          onClose={() => setToast(null)}
        />
      )}
    </>
  );
}
