import React, { useEffect } from "react";
import { AlertCircle, CheckCircle2, X } from "lucide-react";

export type ToastType = "ok" | "error";

interface ToastProps {
  message: string;
  type: ToastType;
  onClose: () => void;
  duration?: number;
}

export function Toast({ message, type, onClose, duration = 3500 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const styles = {
    ok: {
      bg: "bg-emerald-50 dark:bg-emerald-950/20",
      border: "border-emerald-200 dark:border-emerald-900/50",
      text: "text-emerald-800 dark:text-emerald-300",
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />,
    },
    error: {
      bg: "bg-red-50 dark:bg-red-950/20",
      border: "border-red-200 dark:border-red-900/50",
      text: "text-red-800 dark:text-red-300",
      icon: <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />,
    },
  };

  const currentStyle = styles[type];

  return (
    <div
      role="alert"
      className={`fixed bottom-5 right-5 z-[9999] flex items-center justify-between gap-3 p-4 rounded-xl border shadow-lg max-w-sm w-full md:w-[360px] animate-fade-in transition-all duration-300 ${currentStyle.bg} ${currentStyle.border}`}
    >
      <div className="flex items-start gap-3 min-w-0">
        {currentStyle.icon}
        <p className={`text-sm font-semibold truncate mt-0.5 ${currentStyle.text}`}>
          {message}
        </p>
      </div>
      <button
        onClick={onClose}
        className={`p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors ${currentStyle.text}`}
        aria-label="Fechar notificação"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
