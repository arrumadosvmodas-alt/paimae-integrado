import React, { useState } from "react";
import { LogOut, Menu, Moon, Sun, X, ChevronLeft, ChevronRight, GraduationCap } from "lucide-react";
import { useTheme } from "./ThemeContext";
import type { User } from "../../lib/types";

interface AppShellProps {
  children: React.ReactNode;
  user: User | null;
  onLogout: () => void;
  sidebarContent?: React.ReactNode;
}

export function AppShell({ children, user, onLogout, sidebarContent }: AppShellProps) {
  const { theme, toggleTheme } = useTheme();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-text-primary flex transition-colors duration-200">
      {/* Sidebar para telas grandes */}
      <aside
        className={`hidden md:flex flex-col bg-surface border-r border-border transition-all duration-300 relative z-20 ${
          isSidebarOpen ? "w-[300px]" : "w-[72px]"
        }`}
      >
        {/* Topo da Sidebar */}
        <div className="h-[72px] px-6 border-b border-border flex items-center justify-between gap-3 overflow-hidden">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-white flex-shrink-0">
              <GraduationCap className="w-5 h-5" />
            </div>
            {isSidebarOpen && (
              <span className="font-display font-extrabold text-base text-text-primary tracking-tight truncate">
                Pai&MãeIntegrado
              </span>
            )}
          </div>
        </div>

        {/* Botão de colapsar sidebar */}
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="absolute -right-3.5 top-[18px] w-7 h-7 bg-surface border border-border text-text-muted hover:text-text-primary rounded-full flex items-center justify-center shadow-sm z-30 transition-transform active:scale-90"
          aria-label={isSidebarOpen ? "Recolher barra lateral" : "Expandir barra lateral"}
        >
          {isSidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>

        {/* Conteúdo da Sidebar */}
        <div className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-6">
          {isSidebarOpen ? (
            sidebarContent
          ) : (
            <div className="flex flex-col items-center gap-4 text-text-muted">
              {/* Ícones ou indicações rápidas simplificadas quando recolhido */}
              <div className="w-10 h-10 rounded-full bg-background flex items-center justify-center border border-border">
                📍
              </div>
            </div>
          )}
        </div>

        {/* Rodapé da Sidebar */}
        {isSidebarOpen && (
          <div className="p-4 border-t border-border bg-background/30 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-xs text-primary uppercase">
                {user?.name?.slice(0, 2) ?? "US"}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-bold text-text-primary truncate">{user?.name ?? "Usuário"}</p>
                <p className="text-[10px] text-text-muted truncate">{user?.role === "admin" ? "Administrador" : "Membro"}</p>
              </div>
            </div>
            <button
              onClick={onLogout}
              className="p-2 text-text-muted hover:text-error hover:bg-error/5 rounded-lg transition-colors"
              title="Sair"
            >
              <LogOut className="w-4.5 h-4.5" />
            </button>
          </div>
        )}
      </aside>

      {/* Sidebar Móvel (Overlay) */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[999] md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Menu Lateral Móvel */}
      <aside
        className={`fixed top-0 bottom-0 left-0 w-[280px] bg-surface border-r border-border z-[1000] flex flex-col transition-transform duration-300 md:hidden ${
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="h-[72px] px-6 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-white">
              <GraduationCap className="w-5 h-5" />
            </div>
            <span className="font-display font-extrabold text-base text-text-primary tracking-tight">
              Pai&MãeIntegrado
            </span>
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(false)}
            className="p-1.5 rounded-lg hover:bg-surface-hover text-text-muted"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-6">
          {sidebarContent}
        </div>

        <div className="p-4 border-t border-border bg-background/30 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-xs text-primary">
              {user?.name?.slice(0, 2) ?? "US"}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold text-text-primary truncate">{user?.name ?? "Usuário"}</p>
              <p className="text-[10px] text-text-muted truncate">{user?.role === "admin" ? "Administrador" : "Membro"}</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="p-2 text-text-muted hover:text-error hover:bg-error/5 rounded-lg transition-colors"
          >
            <LogOut className="w-4.5 h-4.5" />
          </button>
        </div>
      </aside>

      {/* Área Principal */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="h-[72px] bg-surface border-b border-border px-6 flex items-center justify-between sticky top-0 z-10 transition-colors duration-200">
          <div className="flex items-center gap-4">
            {/* Menu hambúrguer móvel */}
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-2 rounded-lg hover:bg-surface-hover text-text-muted md:hidden"
              aria-label="Abrir menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-bold font-display text-text-primary hidden md:block">
              Área de Trabalho
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {/* Alternador de Tema claro/escuro */}
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-lg border border-border bg-surface text-text-muted hover:text-text-primary hover:bg-surface-hover transition-all active:scale-95"
              aria-label={theme === "light" ? "Mudar para tema escuro" : "Mudar para tema claro"}
            >
              {theme === "light" ? <Moon className="w-4.5 h-4.5" /> : <Sun className="w-4.5 h-4.5" />}
            </button>

            {/* Informações rápidas no mobile (Sair) */}
            <button
              onClick={onLogout}
              className="md:hidden p-2.5 rounded-lg border border-border bg-surface text-text-muted hover:text-error hover:bg-error/5 transition-all"
              title="Sair"
            >
              <LogOut className="w-4.5 h-4.5" />
            </button>
          </div>
        </header>

        {/* Conteúdo Principal */}
        <main className="flex-1 p-4 md:p-8 overflow-y-auto">
          <div className="max-w-[1360px] mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
