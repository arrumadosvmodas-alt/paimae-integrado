import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogIn, AlertCircle, BookOpen } from "lucide-react";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Toast } from "../components/ui/Toast";
import { login, setToken } from "../lib/api";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    if (!email.trim()) {
      setError("Digite seu e-mail");
      setLoading(false);
      return;
    }

    if (!password.trim()) {
      setError("Digite sua senha");
      setLoading(false);
      return;
    }

    try {
      await login(email, password);
      setToastMessage("✅ Autenticado com sucesso!");
      setTimeout(() => {
        navigate("/dashboard");
      }, 500);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao fazer login";
      setError(errorMessage);
      setToastMessage(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo e Título */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <BookOpen className="w-10 h-10 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-800">Pai&Mãe Integrado</h1>
          </div>
          <p className="text-gray-600">
            Plataforma inteligente de educação personalizada
          </p>
        </div>

        {/* Formulário */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                E-mail
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu.email@escola.com"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Senha
              </label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              variant="primary"
              className="w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Autenticando...
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  Entrar
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Credenciais de teste:
            </p>
            <p className="text-xs text-gray-500 text-center mt-1">
              professor@escola.com / senha123
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="mt-8 grid grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-2xl mb-1">📚</p>
            <p className="text-xs text-gray-700 font-medium">Upload IA</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-2xl mb-1">🧠</p>
            <p className="text-xs text-gray-700 font-medium">Adaptativo</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-2xl mb-1">📊</p>
            <p className="text-xs text-gray-700 font-medium">Análise</p>
          </div>
        </div>
      </div>

      {toastMessage && (
        <Toast
          message={toastMessage}
          type={toastMessage.includes("❌") ? "error" : "ok"}
          onClose={() => setToastMessage(null)}
        />
      )}
    </div>
  );
}
