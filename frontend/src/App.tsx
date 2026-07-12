import React, { useEffect, useMemo, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { Bell, BookOpen, ClipboardList, GraduationCap, Sparkles, UserPlus, School as SchoolIcon, LayoutDashboard, ChevronDown, ChevronUp } from "lucide-react";

import { api, getToken, login, setToken } from "./lib/api";
import type { Child, EvolutionEvent, Notification, Routine, School, Task, User } from "./lib/types";

// Componentes do Design System UI
import { Button } from "./components/ui/Button";
import { Card } from "./components/ui/Card";
import { Input } from "./components/ui/Input";
import { Badge } from "./components/ui/Badge";
import { SkeletonList } from "./components/ui/Skeleton";
import { Toast, ToastType } from "./components/ui/Toast";

// Layout e Tema
import { ThemeProvider, useTheme } from "./components/layout/ThemeContext";
import { AppShell } from "./components/layout/AppShell";

// Componentes de Domínio
import { SchoolCreateForm } from "./components/domains/school/SchoolCreateForm";
import { ChildCreateForm } from "./components/domains/child/ChildCreateForm";
import { ChildSelector } from "./components/domains/child/ChildSelector";
import { RoutineCreateForm } from "./components/domains/routine/RoutineCreateForm";
import { RoutineList } from "./components/domains/routine/RoutineList";
import { TaskCreateForm } from "./components/domains/task/TaskCreateForm";
import { TaskList } from "./components/domains/task/TaskList";
import { NotificationList } from "./components/domains/notification/NotificationList";
import { EvolutionEventCreateForm } from "./components/domains/evolution/EvolutionEventCreateForm";
import { EvolutionSummary } from "./components/domains/evolution/EvolutionSummary";

export function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </ThemeProvider>
  );
}

function AppRoutes() {
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const navigate = useNavigate();

  // Estados compartilhados e orquestrados
  const [user, setUser] = useState<User | null>(null);
  const [schools, setSchools] = useState<School[]>([]);
  const [children, setChildren] = useState<Child[]>([]);
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [events, setEvents] = useState<EvolutionEvent[]>([]);
  const [selectedChildId, setSelectedChildId] = useState("");
  const [summary, setSummary] = useState("");
  const [toast, setToast] = useState<{ message: string; type: ToastType } | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(false);

  const selectedChild = useMemo(
    () => children.find((child) => child.id === selectedChildId) ?? children[0],
    [children, selectedChildId]
  );

  function notify(message: string, type: ToastType = "ok") {
    setToast({ message, type });
  }

  async function loadBase() {
    setIsLoadingData(true);
    try {
      const [me, schoolList, childList] = await Promise.all([
        api<User>("/api/v1/auth/me"),
        api<School[]>("/api/v1/schools"),
        api<Child[]>("/api/v1/children"),
      ]);
      setUser(me);
      setSchools(schoolList);
      setChildren(childList);
      const nextChildId = selectedChildId || childList[0]?.id || "";
      setSelectedChildId(nextChildId);
      await loadChildData(nextChildId);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao carregar dados.", "error");
    } finally {
      setIsLoadingData(false);
    }
  }

  async function loadChildData(childId: string) {
    if (!childId) {
      setRoutines([]);
      setNotifications([]);
      setTasks([]);
      setEvents([]);
      setSummary("");
      return;
    }
    try {
      const [routineList, notificationList, taskList, eventList] = await Promise.all([
        api<Routine[]>(`/api/v1/routines?child_id=${childId}`),
        api<Notification[]>(`/api/v1/notifications?child_id=${childId}`),
        api<Task[]>(`/api/v1/tasks?child_id=${childId}`),
        api<EvolutionEvent[]>(`/api/v1/evolution-events?child_id=${childId}`),
      ]);
      setRoutines(routineList);
      setNotifications(notificationList);
      setTasks(taskList);
      setEvents(eventList);
      setSummary(""); // Limpa o resumo de IA da criança anterior
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao carregar dados da criança.", "error");
    }
  }

  useEffect(() => {
    if (!token) return;
    loadBase().catch((error) => {
      notify(error.message, "error");
      setToken(null);
      setTokenState(null);
      navigate("/login");
    });
  }, [token]);

  useEffect(() => {
    if (selectedChildId) {
      loadChildData(selectedChildId).catch((error) => notify(error.message, "error"));
    }
  }, [selectedChildId]);

  const handleLogout = () => {
    setToken(null);
    setTokenState(null);
    setUser(null);
    navigate("/login");
    notify("Você saiu do sistema.");
  };

  const handleLoginSubmit = async (tokenString: string) => {
    setTokenState(tokenString);
    navigate("/");
  };

  async function submit(path: string, payload: unknown, successMessage: string) {
    try {
      await api(path, { method: "POST", body: JSON.stringify(payload) });
      notify(successMessage);
      await loadBase();
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao salvar registro.", "error");
      throw error;
    }
  }

  async function handleCompleteNotification(id: string) {
    try {
      await api(`/api/v1/notifications/${id}/complete`, { method: "POST" });
      notify("Notificação concluída.");
      if (selectedChildId) {
        await loadChildData(selectedChildId);
      }
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao concluir notificação.", "error");
    }
  }

  async function handleGenerateAISummary() {
    if (!selectedChildId) return;
    try {
      const result = await api<{ summary: string; status: string; data_points: number }>("/api/v1/ai/summaries", {
        method: "POST",
        body: JSON.stringify({ child_id: selectedChildId }),
      });
      setSummary(`${result.status}: ${result.summary}`);
      notify("Resumo gerado por IA com sucesso.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao gerar resumo.", "error");
    }
  }

  return (
    <>
      <Routes>
        <Route
          path="/login"
          element={
            token ? (
              <Navigate to="/" replace />
            ) : (
              <LoginPage onLoginSuccess={handleLoginSubmit} notify={notify} />
            )
          }
        />
        <Route
          path="/"
          element={
            !token ? (
              <Navigate to="/login" replace />
            ) : (
              <DashboardPage
                user={user}
                schools={schools}
                childrenList={children}
                selectedChildId={selectedChildId}
                setSelectedChildId={setSelectedChildId}
                routines={routines}
                notifications={notifications}
                tasks={tasks}
                summary={summary}
                isLoadingData={isLoadingData}
                onLogout={handleLogout}
                onSubmit={submit}
                onCompleteNotification={handleCompleteNotification}
                onGenerateAISummary={handleGenerateAISummary}
              />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </>
  );
}

// Tela de Login e Bootstrap
interface LoginPageProps {
  onLoginSuccess: (token: string) => Promise<void>;
  notify: (msg: string, type?: ToastType) => void;
}

function LoginPage({ onLoginSuccess, notify }: LoginPageProps) {
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [isLoginLoading, setIsLoginLoading] = useState(false);

  const [adminName, setAdminName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [isAdminLoading, setIsAdminLoading] = useState(false);

  async function handleLogin(event: React.FormEvent) {
    event.preventDefault();
    if (!loginEmail || !loginPassword) return;
    
    setIsLoginLoading(true);
    try {
      const nextToken = await login(loginEmail, loginPassword);
      notify("Login realizado com sucesso!");
      await onLoginSuccess(nextToken);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Falha no login.", "error");
    } finally {
      setIsLoginLoading(false);
    }
  }

  async function handleBootstrap(event: React.FormEvent) {
    event.preventDefault();
    if (!adminName || !adminEmail || !adminPassword) return;

    setIsAdminLoading(true);
    try {
      await api<User>("/api/v1/auth/bootstrap-admin", {
        method: "POST",
        body: JSON.stringify({
          name: adminName,
          email: adminEmail,
          password: adminPassword,
          role: "admin",
        }),
      });
      notify("Admin inicial criado. Faça login.");
      setAdminName("");
      setAdminEmail("");
      setAdminPassword("");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Falha ao criar admin inicial.", "error");
    } finally {
      setIsAdminLoading(false);
    }
  }

  return (
    <main className="min-h-screen grid grid-cols-1 lg:grid-cols-12 bg-background transition-colors duration-200">
      {/* Coluna da Esquerda: Ilustrativa Premium */}
      <section className="lg:col-span-5 bg-gradient-to-br from-primary to-indigo-700 text-white p-8 md:p-12 flex flex-col justify-between relative overflow-hidden hidden lg:flex">
        {/* Elemento de iluminação decorativo */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/10 rounded-full blur-[80px] -mr-40 -mt-40 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-black/10 rounded-full blur-[60px] -ml-20 -mb-20 pointer-events-none" />
        
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white border border-white/20">
            <GraduationCap className="w-6 h-6" />
          </div>
          <span className="font-display font-extrabold text-xl tracking-tight">
            Pai&MãeIntegrado
          </span>
        </div>

        <div className="relative z-10 flex flex-col gap-4 my-auto">
          <Badge variant="primary" className="bg-white/10 text-white border-white/20 w-fit">
            Acompanhamento Escolar & Familiar
          </Badge>
          <h2 className="text-3xl md:text-4xl font-display font-black leading-tight">
            Sintonia perfeita entre a escola e o lar.
          </h2>
          <p className="text-sm md:text-base text-white/80 leading-relaxed max-w-md">
            Acompanhe rotinas diárias, tarefas pendentes, receba notificações cruciais e visualize análises comportamentais consolidadas por inteligência artificial para o desenvolvimento completo de seu filho.
          </p>
        </div>

        <div className="relative z-10 text-xs text-white/60">
          © {new Date().getFullYear()} Pai&MãeIntegrado. Todos os direitos reservados.
        </div>
      </section>

      {/* Coluna da Direita: Formulários */}
      <section className="lg:col-span-7 p-6 md:p-12 lg:p-16 flex flex-col justify-center items-center overflow-y-auto">
        <div className="w-full max-w-[480px] flex flex-col gap-8">
          <div className="text-center lg:text-left">
            {/* Logo para Mobile */}
            <div className="flex items-center justify-center gap-2 mb-4 lg:hidden">
              <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center text-white">
                <GraduationCap className="w-5.5 h-5.5" />
              </div>
              <span className="font-display font-extrabold text-lg text-text-primary tracking-tight">
                Pai&MãeIntegrado
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-display font-black text-text-primary leading-tight">
              Acesso à Plataforma
            </h1>
            <p className="text-sm text-text-muted mt-2">
              Seja bem-vindo de volta! Faça login na sua conta ou configure o administrador inicial.
            </p>
          </div>

          <div className="flex flex-col gap-6">
            {/* Form Login */}
            <Card title="Entrar na sua Conta">
              <form onSubmit={handleLogin} className="flex flex-col gap-4">
                <Input
                  label="Endereço de E-mail"
                  type="email"
                  placeholder="Ex: seuemail@dominio.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                  disabled={isLoginLoading}
                />
                <Input
                  label="Senha"
                  type="password"
                  placeholder="Digite sua senha"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  disabled={isLoginLoading}
                />
                <Button type="submit" isLoading={isLoginLoading} className="w-full">
                  Entrar
                </Button>
              </form>
            </Card>

            {/* Form Primeiro Admin */}
            <Card title="Criar Primeiro Admin" subtitle="Configure o administrador do sistema para iniciar os testes">
              <form onSubmit={handleBootstrap} className="flex flex-col gap-4">
                <Input
                  label="Nome Completo"
                  placeholder="Ex: Administrador Principal"
                  value={adminName}
                  onChange={(e) => setAdminName(e.target.value)}
                  required
                  disabled={isAdminLoading}
                />
                <Input
                  label="Endereço de E-mail"
                  type="email"
                  placeholder="Ex: admin@escola.com"
                  value={adminEmail}
                  onChange={(e) => setAdminEmail(e.target.value)}
                  required
                  disabled={isAdminLoading}
                />
                <Input
                  label="Senha do Admin (8+ caracteres)"
                  type="password"
                  placeholder="Crie uma senha forte"
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  required
                  minLength={8}
                  disabled={isAdminLoading}
                />
                <Button variant="secondary" type="submit" isLoading={isAdminLoading} className="w-full">
                  Criar Administrador
                </Button>
              </form>
            </Card>
          </div>
        </div>
      </section>
    </main>
  );
}

// Tela de Dashboard Principal
interface DashboardPageProps {
  user: User | null;
  schools: School[];
  childrenList: Child[];
  selectedChildId: string;
  setSelectedChildId: (id: string) => void;
  routines: Routine[];
  notifications: Notification[];
  tasks: Task[];
  summary: string;
  isLoadingData: boolean;
  onLogout: () => void;
  onSubmit: (path: string, payload: unknown, successMsg: string) => Promise<void>;
  onCompleteNotification: (id: string) => Promise<void>;
  onGenerateAISummary: () => Promise<void>;
}

function DashboardPage({
  user,
  schools,
  childrenList,
  selectedChildId,
  setSelectedChildId,
  routines,
  notifications,
  tasks,
  summary,
  isLoadingData,
  onLogout,
  onSubmit,
  onCompleteNotification,
  onGenerateAISummary,
}: DashboardPageProps) {
  const [isSchoolsExpanded, setIsSchoolsExpanded] = useState(false);
  const [isChildrenExpanded, setIsChildrenExpanded] = useState(false);

  // Filtros de contagem para métricas
  const selectedChild = childrenList.find((c) => c.id === selectedChildId);

  const sidebarContent = (
    <div className="flex flex-col gap-6">
      {/* Seletor da criança em foco */}
      <ChildSelector
        childrenList={childrenList}
        selectedChildId={selectedChildId}
        onSelectChild={setSelectedChildId}
      />

      {/* Accordion para cadastrar Escola */}
      <div className="border border-border rounded-2xl overflow-hidden bg-surface">
        <button
          onClick={() => setIsSchoolsExpanded(!isSchoolsExpanded)}
          className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <SchoolIcon className="w-4.5 h-4.5 text-primary" />
            <span>Cadastros de Escolas</span>
          </div>
          {isSchoolsExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {isSchoolsExpanded && (
          <div className="p-4 border-t border-border bg-background/20">
            <SchoolCreateForm
              onSubmit={(payload) => onSubmit("/api/v1/schools", payload, "Escola cadastrada com sucesso.")}
            />
          </div>
        )}
      </div>

      {/* Accordion para cadastrar Criança */}
      <div className="border border-border rounded-2xl overflow-hidden bg-surface">
        <button
          onClick={() => setIsChildrenExpanded(!isChildrenExpanded)}
          className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <UserPlus className="w-4.5 h-4.5 text-primary" />
            <span>Cadastros de Crianças</span>
          </div>
          {isChildrenExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {isChildrenExpanded && (
          <div className="p-4 border-t border-border bg-background/20">
            <ChildCreateForm
              schools={schools}
              onSubmit={(payload) => onSubmit("/api/v1/children", payload, "Criança cadastrada com sucesso.")}
            />
          </div>
        )}
      </div>
    </div>
  );

  return (
    <AppShell user={user} onLogout={onLogout} sidebarContent={sidebarContent}>
      {/* Seção superior de Métricas */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          icon={<SchoolIcon className="w-5.5 h-5.5 text-primary" />}
          label="Escolas Cadastradas"
          value={schools.length}
          colorClass="bg-primary/10"
        />
        <MetricCard
          icon={<UserPlus className="w-5.5 h-5.5 text-secondary" />}
          label="Crianças Cadastradas"
          value={childrenList.length}
          colorClass="bg-secondary/10"
        />
        <MetricCard
          icon={<Bell className="w-5.5 h-5.5 text-tertiary" />}
          label="Notificações da Criança"
          value={notifications.length}
          colorClass="bg-tertiary/10"
        />
        <MetricCard
          icon={<ClipboardList className="w-5.5 h-5.5 text-error" />}
          label="Tarefas da Criança"
          value={tasks.length}
          colorClass="bg-error/10"
        />
      </section>

      {/* Conteúdo Principal com skeletons se carregando */}
      {isLoadingData ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkeletonList count={2} />
          <SkeletonList count={2} />
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          {/* Seção 1: Nova Rotina / Nova Tarefa */}
          <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RoutineCreateForm
              childId={selectedChildId}
              onSubmit={(payload) => onSubmit("/api/v1/routines", payload, "Rotina criada com sucesso.")}
            />
            <TaskCreateForm
              childId={selectedChildId}
              onSubmit={(payload) => onSubmit("/api/v1/tasks", payload, "Tarefa criada com sucesso.")}
            />
          </section>

          {/* Seção 2: Notificações / Evolução por IA */}
          <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <NotificationList
              notifications={notifications}
              childId={selectedChildId}
              onGenerateToday={async () => {
                await onSubmit(
                  "/api/v1/notifications/generate",
                  { child_id: selectedChildId, target_date: new Date().toISOString().slice(0, 10) },
                  "Notificações geradas para o dia de hoje."
                );
              }}
              onCompleteNotification={onCompleteNotification}
            />
            <div className="flex flex-col gap-6">
              <EvolutionEventCreateForm
                childId={selectedChildId}
                onSubmit={(payload) => onSubmit("/api/v1/evolution-events", payload, "Evento de evolução registrado com sucesso.")}
              />
              <EvolutionSummary
                childId={selectedChildId}
                summaryText={summary}
                onGenerateSummary={onGenerateAISummary}
              />
            </div>
          </section>

          {/* Seção 3: Visualização em Listas / Tabelas */}
          <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RoutineList routines={routines} />
            <TaskList tasks={tasks} />
          </section>
        </div>
      )}
    </AppShell>
  );
}

// Componente local para Metric Card
interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  colorClass: string;
}

function MetricCard({ icon, label, value, colorClass }: MetricCardProps) {
  return (
    <Card className="hover:shadow-md transition-all duration-200">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colorClass}`}>
          {icon}
        </div>
        <div className="min-w-0">
          <span className="block text-2xl md:text-3xl font-display font-black text-text-primary">
            {value}
          </span>
          <span className="block text-[11px] font-bold font-display uppercase tracking-wider text-text-muted truncate mt-0.5">
            {label}
          </span>
        </div>
      </div>
    </Card>
  );
}
