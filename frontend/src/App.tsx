import React, { useEffect, useMemo, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { Bell, BookOpen, ClipboardList, GraduationCap, Sparkles, UserPlus, School as SchoolIcon, LayoutDashboard, ChevronDown, ChevronUp, Users, Bookmark, Shield, Download } from "lucide-react";

import { api, getToken, login, setToken } from "./lib/api";
import type { Child, EvolutionEvent, Notification, Routine, School, Task, User, DailySchoolRecord, PedagogicalMaterial, PedagogicalMethodology } from "./lib/types";

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
import { UserCreateForm } from "./components/domains/user/UserCreateForm";
import { RoutineCreateForm } from "./components/domains/routine/RoutineCreateForm";
import { RoutineList } from "./components/domains/routine/RoutineList";
import { TaskCreateForm } from "./components/domains/task/TaskCreateForm";
import { TaskList } from "./components/domains/task/TaskList";
import { NotificationList } from "./components/domains/notification/NotificationList";
import { EvolutionEventCreateForm } from "./components/domains/evolution/EvolutionEventCreateForm";
import { EvolutionSummary } from "./components/domains/evolution/EvolutionSummary";

// Módulo Pedagógico
import { PedagogicalMaterialForm } from "./components/domains/pedagogy/PedagogicalMaterialForm";
import { PedagogicalMaterialItemForm } from "./components/domains/pedagogy/PedagogicalMaterialItemForm";
import { PedagogicalMaterialList } from "./components/domains/pedagogy/PedagogicalMaterialList";
import { MetricsDashboard } from "./components/domains/pedagogy/MetricsDashboard";
import { LgpdConsentModal } from "./components/ui/LgpdConsentModal";
import { DailyRecordForm } from "./components/domains/pedagogy/DailyRecordForm";
import { DailyRecordList } from "./components/domains/pedagogy/DailyRecordList";
import { FamilyInteractions } from "./components/domains/pedagogy/FamilyInteractions";
import { PedagogicalMethodologyForm } from "./components/domains/pedagogy/PedagogicalMethodologyForm";

// Páginas Fase F
import { TeacherDashboard } from "./pages/TeacherDashboard";
import { ParentDashboard } from "./pages/ParentDashboard";
import { ChildInterface } from "./pages/ChildInterface";

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
  const [dailyRecords, setDailyRecords] = useState<DailySchoolRecord[]>([]);
  const [materials, setMaterials] = useState<PedagogicalMaterial[]>([]);
  const [methodologies, setMethodologies] = useState<PedagogicalMethodology[]>([]);
  const [usersList, setUsersList] = useState<User[]>([]);
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

      if (me.role === "admin") {
        const uList = await api<User[]>("/api/v1/auth/users").catch(() => []);
        setUsersList(uList);
      }

      const nextChildId = selectedChildId || childList[0]?.id || "";
      setSelectedChildId(nextChildId);
      await loadChildData(nextChildId);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao carregar dados.", "error");
      throw error;
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
      setDailyRecords([]);
      setMaterials([]);
      setMethodologies([]);
      setSummary("");
      return;
    }
    try {
      const [routineList, notificationList, taskList, eventList, dailyRecordList] = await Promise.all([
        api<Routine[]>(`/api/v1/routines?child_id=${childId}`),
        api<Notification[]>(`/api/v1/notifications?child_id=${childId}`),
        api<Task[]>(`/api/v1/tasks?child_id=${childId}`),
        api<EvolutionEvent[]>(`/api/v1/evolution-events?child_id=${childId}`),
        api<DailySchoolRecord[]>(`/api/v1/pedagogy/daily-records?child_id=${childId}`).catch(() => []),
      ]);
      setRoutines(routineList);
      setNotifications(notificationList);
      setTasks(taskList);
      setEvents(eventList);
      setDailyRecords(dailyRecordList);

      const activeChild = children.find(c => c.id === childId);
      if (activeChild) {
        const [materialList, methodologyList] = await Promise.all([
          api<PedagogicalMaterial[]>(`/api/v1/pedagogy/materials?school_id=${activeChild.school_id}`).catch(() => []),
          api<PedagogicalMethodology[]>(`/api/v1/pedagogy/methodologies?school_id=${activeChild.school_id}`).catch(() => []),
        ]);
        setMaterials(materialList);
        setMethodologies(methodologyList);
      } else {
        setMaterials([]);
        setMethodologies([]);
      }

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

  async function submit(path: string, payload: any, successMessage: string) {
    try {
      const isEdit = payload && typeof payload === "object" && "id" in payload && payload.id;
      const method = isEdit ? "PUT" : "POST";
      const url = isEdit ? `${path}/${payload.id}` : path;
      await api(url, { method, body: JSON.stringify(payload) });
      notify(successMessage);
      await loadBase();
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao salvar registro.", "error");
      throw error;
    }
  }

  async function handleToggleActive(path: string, id: string, currentIsActive = true) {
    const nextIsActive = !currentIsActive;
    const actionLabel = nextIsActive ? "reativar" : "inativar";
    if (!window.confirm(`Deseja realmente ${actionLabel} este registro?`)) return;
    try {
      await api(`${path}/${id}/status`, { method: "PATCH", body: JSON.stringify({ is_active: nextIsActive }) });
      notify(nextIsActive ? "Registro reativado." : "Registro inativado.");
      await loadBase();
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao atualizar status.", "error");
    }
  }

  async function handleDeleteUser(id: string) {
    if (!window.confirm("Deseja realmente excluir este usuário permanentemente?")) return;
    try {
      await api(`/api/v1/auth/users/${id}`, { method: "DELETE" });
      notify("Usuário excluído com sucesso.");
      await loadBase();
    } catch (error) {
      notify(error instanceof Error ? error.message : "Erro ao excluir usuário.", "error");
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
                setUser={setUser}
                schools={schools}
                childrenList={children}
                selectedChildId={selectedChildId}
                setSelectedChildId={setSelectedChildId}
                routines={routines}
                notifications={notifications}
                tasks={tasks}
                dailyRecords={dailyRecords}
                materials={materials}
                methodologies={methodologies}
                usersList={usersList}
                summary={summary}
                isLoadingData={isLoadingData}
                onLogout={handleLogout}
                onSubmit={submit}
                onToggleActive={handleToggleActive}
                onDeleteUser={handleDeleteUser}
                onCompleteNotification={handleCompleteNotification}
                onGenerateAISummary={handleGenerateAISummary}
                notify={notify}
              />
            )
          }
        />
        <Route
          path="/teacher-dashboard"
          element={!token ? <Navigate to="/login" replace /> : <TeacherDashboard />}
        />
        <Route
          path="/parent-dashboard"
          element={!token ? <Navigate to="/login" replace /> : <ParentDashboard />}
        />
        <Route
          path="/child-interface"
          element={!token ? <Navigate to="/login" replace /> : <ChildInterface />}
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
  const [activeTab, setActiveTab] = useState<"login" | "first-access" | "bootstrap">("login");

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [isLoginLoading, setIsLoginLoading] = useState(false);

  const [adminName, setAdminName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [adminDocument, setAdminDocument] = useState("");
  const [isAdminLoading, setIsAdminLoading] = useState(false);

  const [firstAccessEmail, setFirstAccessEmail] = useState("");
  const [firstAccessName, setFirstAccessName] = useState("");
  const [firstAccessPassword, setFirstAccessPassword] = useState("");
  const [isFirstAccessLoading, setIsFirstAccessLoading] = useState(false);

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
    if (!adminName || !adminEmail || !adminPassword || !adminDocument) return;

    setIsAdminLoading(true);
    try {
      await api<User>("/api/v1/auth/bootstrap-admin", {
        method: "POST",
        body: JSON.stringify({
          name: adminName,
          email: adminEmail,
          password: adminPassword,
          role: "admin",
          document: adminDocument.trim(),
        }),
      });
      notify("Administrador inicial criado! Use as credenciais para fazer login.");
      setAdminName("");
      setAdminEmail("");
      setAdminPassword("");
      setAdminDocument("");
      setActiveTab("login");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Falha ao criar admin inicial.", "error");
    } finally {
      setIsAdminLoading(false);
    }
  }

  async function handleFirstAccess(event: React.FormEvent) {
    event.preventDefault();
    if (!firstAccessEmail || !firstAccessName || !firstAccessPassword) return;

    setIsFirstAccessLoading(true);
    try {
      const response = await api<{ message: string }>("/api/v1/auth/first-access", {
        method: "POST",
        body: JSON.stringify({
          email: firstAccessEmail.trim(),
          name: firstAccessName.trim(),
          password: firstAccessPassword.trim(),
        }),
      });
      notify(response.message || "Cadastro realizado! Faça o login.");
      setFirstAccessEmail("");
      setFirstAccessName("");
      setFirstAccessPassword("");
      setActiveTab("login");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Falha ao registrar senha.", "error");
    } finally {
      setIsFirstAccessLoading(false);
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
      <section className="lg:col-span-7 p-6 md:p-12 lg:p-16 flex flex-col justify-center items-center overflow-y-auto w-full">
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
              Portal do Sistema
            </h1>
            <p className="text-sm text-text-muted mt-2">
              Selecione o acesso abaixo para entrar ou ativar sua conta.
            </p>
          </div>

          {/* Abas para alternar formulários */}
          <div className="flex border-b border-border gap-2">
            <button
              onClick={() => setActiveTab("login")}
              className={`flex-1 pb-3 text-center text-sm font-bold border-b-2 transition-all duration-200 ${
                activeTab === "login"
                  ? "border-primary text-primary"
                  : "border-transparent text-text-muted hover:text-text-primary"
              }`}
            >
              Entrar
            </button>
            <button
              onClick={() => setActiveTab("first-access")}
              className={`flex-1 pb-3 text-center text-sm font-bold border-b-2 transition-all duration-200 ${
                activeTab === "first-access"
                  ? "border-primary text-primary"
                  : "border-transparent text-text-muted hover:text-text-primary"
              }`}
            >
              Primeiro Acesso
            </button>
            <button
              onClick={() => setActiveTab("bootstrap")}
              className={`flex-1 pb-3 text-center text-sm font-bold border-b-2 transition-all duration-200 ${
                activeTab === "bootstrap"
                  ? "border-primary text-primary"
                  : "border-transparent text-text-muted hover:text-text-primary"
              }`}
            >
              Instalação (Admin)
            </button>
          </div>

          <div className="flex flex-col gap-6">
            {activeTab === "login" && (
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
            )}

            {activeTab === "first-access" && (
              <Card title="Primeiro Acesso / Ativar Conta" subtitle="Registre a sua senha pessoal utilizando os dados fornecidos pela escola/administrador">
                <form onSubmit={handleFirstAccess} className="flex flex-col gap-4">
                  <Input
                    label="Endereço de E-mail"
                    type="email"
                    placeholder="Ex: joao@gmail.com"
                    value={firstAccessEmail}
                    onChange={(e) => setFirstAccessEmail(e.target.value)}
                    required
                    disabled={isFirstAccessLoading}
                  />
                  <Input
                    label="Nome Completo (idêntico ao cadastrado)"
                    placeholder="Ex: João da Silva"
                    value={firstAccessName}
                    onChange={(e) => setFirstAccessName(e.target.value)}
                    required
                    disabled={isFirstAccessLoading}
                  />
                  <Input
                    label="Nova Senha (mínimo 8 caracteres)"
                    type="password"
                    placeholder="Defina uma senha segura"
                    value={firstAccessPassword}
                    onChange={(e) => setFirstAccessPassword(e.target.value)}
                    required
                    minLength={8}
                    disabled={isFirstAccessLoading}
                  />
                  <Button type="submit" isLoading={isFirstAccessLoading} className="w-full">
                    Cadastrar Minha Senha
                  </Button>
                </form>
              </Card>
            )}

            {activeTab === "bootstrap" && (
              <Card title="Criar Primeiro Admin" subtitle="Configure o administrador principal do sistema para iniciar">
                <form onSubmit={handleBootstrap} className="flex flex-col gap-4">
                  <Input
                    label="Nome Completo do Administrador"
                    placeholder="Ex: Heitor Silvio Lins"
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
                    label="CPF do Administrador"
                    placeholder="Ex: 000.000.000-00 (apenas 11 números)"
                    value={adminDocument}
                    onChange={(e) => setAdminDocument(e.target.value)}
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
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

// Tela de Dashboard Principal
interface DashboardPageProps {
  user: User | null;
  setUser: (user: User | null) => void;
  schools: School[];
  childrenList: Child[];
  selectedChildId: string;
  setSelectedChildId: (id: string) => void;
  routines: Routine[];
  notifications: Notification[];
  tasks: Task[];
  dailyRecords: DailySchoolRecord[];
  materials: PedagogicalMaterial[];
  methodologies: PedagogicalMethodology[];
  usersList: User[];
  summary: string;
  isLoadingData: boolean;
  onLogout: () => void;
  onSubmit: (path: string, payload: any, successMsg: string) => Promise<void>;
  onToggleActive: (path: string, id: string, currentIsActive?: boolean) => Promise<void>;
  onDeleteUser: (id: string) => Promise<void>;
  onCompleteNotification: (id: string) => Promise<void>;
  onGenerateAISummary: () => Promise<void>;
  notify: (msg: string, type?: ToastType) => void;
}

function DashboardPage({
  user,
  setUser,
  schools,
  childrenList,
  selectedChildId,
  setSelectedChildId,
  routines,
  notifications,
  tasks,
  dailyRecords,
  materials,
  methodologies,
  usersList,
  summary,
  isLoadingData,
  onLogout,
  onSubmit,
  onToggleActive,
  onDeleteUser,
  onCompleteNotification,
  onGenerateAISummary,
  notify,
}: DashboardPageProps) {
  const [isSchoolsExpanded, setIsSchoolsExpanded] = useState(false);
  const [isChildrenExpanded, setIsChildrenExpanded] = useState(false);
  const [isPedagogyExpanded, setIsPedagogyExpanded] = useState(false);
  const [isPedagogyItemExpanded, setIsPedagogyItemExpanded] = useState(false);
  const [isMethodologyExpanded, setIsMethodologyExpanded] = useState(false);
  const [isUsersExpanded, setIsUsersExpanded] = useState(false);
  const [activeDashboardTab, setActiveDashboardTab] = useState<"overview" | "metrics">("overview");
  const [isLgpdExpanded, setIsLgpdExpanded] = useState(false);

  const [schoolToEdit, setSchoolToEdit] = useState<School | null>(null);
  const [childToEdit, setChildToEdit] = useState<Child | null>(null);
  const [materialToEdit, setMaterialToEdit] = useState<PedagogicalMaterial | null>(null);
  const [dailyRecordToEdit, setDailyRecordToEdit] = useState<DailySchoolRecord | null>(null);
  const [methodologyToEdit, setMethodologyToEdit] = useState<PedagogicalMethodology | null>(null);
  const [userToEdit, setUserToEdit] = useState<User | null>(null);

  useEffect(() => {
    if (schoolToEdit) setIsSchoolsExpanded(true);
  }, [schoolToEdit]);

  useEffect(() => {
    if (childToEdit) setIsChildrenExpanded(true);
  }, [childToEdit]);

  useEffect(() => {
    if (materialToEdit) setIsPedagogyExpanded(true);
  }, [materialToEdit]);

  useEffect(() => {
    if (methodologyToEdit) setIsMethodologyExpanded(true);
  }, [methodologyToEdit]);

  useEffect(() => {
    if (userToEdit) setIsUsersExpanded(true);
  }, [userToEdit]);

  const showSchoolCreate = user?.role === "admin";
  const showChildCreate = user?.role === "admin" || user?.role === "school_admin" || user?.role === "teacher";
  const showPedagogyCreate = user?.role === "admin" || user?.role === "school_admin" || user?.role === "teacher";
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
      {showSchoolCreate && (
        <div className="border border-border rounded-2xl overflow-hidden bg-surface">
          <button
            onClick={() => setIsSchoolsExpanded(!isSchoolsExpanded)}
            className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <SchoolIcon className="w-4.5 h-4.5 text-primary" />
              <span>Gerenciar Escolas (Cadastrar / Consultar / Editar)</span>
            </div>
            {isSchoolsExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isSchoolsExpanded && (
            <div className="p-4 border-t border-border bg-background/20">
              <SchoolCreateForm
                schoolToEdit={schoolToEdit}
                onCancelEdit={() => setSchoolToEdit(null)}
                onSubmit={async (payload) => {
                  await onSubmit("/api/v1/schools", payload, schoolToEdit ? "Escola atualizada." : "Escola cadastrada.");
                  setSchoolToEdit(null);
                }}
              />

              <div className="mt-4 pt-4 border-t border-border/80 flex flex-col gap-2 max-h-40 overflow-y-auto">
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Escolas Cadastradas ({schools.length})</span>
                {schools.map(s => (
                  <div key={s.id} className="flex justify-between items-center text-xs p-2 bg-background/45 rounded-lg border border-border/50">
                    <span className={`${s.is_active ? "text-text-primary" : "text-text-muted line-through"}`}>{s.name}</span>
                    <div className="flex gap-2">
                      <button onClick={() => setSchoolToEdit(s)} className="text-primary hover:underline font-semibold">Editar</button>
                      <button onClick={() => onToggleActive("/api/v1/schools", s.id, s.is_active !== false)} className={`${s.is_active ? "text-error" : "text-ok"} hover:underline font-semibold`}>
                        {s.is_active ? "Inativar" : "Ativar"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Accordion para cadastrar Criança */}
      {showChildCreate && (
        <div className="border border-border rounded-2xl overflow-hidden bg-surface">
          <button
            onClick={() => setIsChildrenExpanded(!isChildrenExpanded)}
            className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <UserPlus className="w-4.5 h-4.5 text-primary" />
              <span>Gerenciar Alunos (Cadastrar / Consultar / Editar)</span>
            </div>
            {isChildrenExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isChildrenExpanded && (
            <div className="p-4 border-t border-border bg-background/20">
              <ChildCreateForm
                schools={schools}
                childToEdit={childToEdit}
                onCancelEdit={() => setChildToEdit(null)}
                onSubmit={async (payload) => {
                  await onSubmit("/api/v1/children", payload, childToEdit ? "Aluno atualizado." : "Aluno cadastrado.");
                  setChildToEdit(null);
                }}
              />

              <div className="mt-4 pt-4 border-t border-border/80 flex flex-col gap-2 max-h-40 overflow-y-auto">
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Alunos Cadastrados ({childrenList.length})</span>
                {childrenList.map(c => (
                  <div key={c.id} className="flex justify-between items-center text-xs p-2 bg-background/45 rounded-lg border border-border/50">
                    <div>
                      <span className={`${c.is_active ? "text-text-primary" : "text-text-muted line-through"}`}>{c.full_name}</span>
                      {!c.is_active && <span className="ml-1 text-[8px] bg-error/20 text-error px-1 rounded uppercase font-bold">Inativo</span>}
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => setChildToEdit(c)} className="text-primary hover:underline font-semibold">Editar</button>
                      <button onClick={() => onToggleActive("/api/v1/children", c.id, c.is_active !== false)} className={`${c.is_active ? "text-error" : "text-ok"} hover:underline font-semibold`}>
                        {c.is_active ? "Inativar" : "Ativar"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Accordion para cadastrar Material Didático */}
      {showPedagogyCreate && (
        <div className="border border-border rounded-2xl overflow-hidden bg-surface">
          <button
            onClick={() => setIsPedagogyExpanded(!isPedagogyExpanded)}
            className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <BookOpen className="w-4.5 h-4.5 text-primary" />
              <span>Gerenciar Livros & Materiais (Cadastrar / Consultar / Editar)</span>
            </div>
            {isPedagogyExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isPedagogyExpanded && (
            <div className="p-4 border-t border-border bg-background/20">
              <PedagogicalMaterialForm
                schoolId={selectedChild?.school_id}
                schools={schools}
                materialToEdit={materialToEdit}
                onCancelEdit={() => setMaterialToEdit(null)}
                onSubmit={async (payload) => {
                  await onSubmit("/api/v1/pedagogy/materials", payload, materialToEdit ? "Material atualizado." : "Material cadastrado.");
                  setMaterialToEdit(null);
                }}
                notify={(msg, type) => notify(msg, type === "error" ? "error" : "ok")}
              />

              <div className="mt-4 pt-4 border-t border-border/80 flex flex-col gap-2 max-h-40 overflow-y-auto">
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Livros Cadastrados ({materials.length})</span>
                {materials.map(m => (
                  <div key={m.id} className="flex justify-between items-center text-xs p-2 bg-background/45 rounded-lg border border-border/50">
                    <div>
                      <span className={`${m.is_active !== false ? "text-text-primary" : "text-text-muted line-through"}`}>{m.title}</span>
                      {m.is_active === false && <span className="ml-1 text-[8px] bg-error/20 text-error px-1 rounded uppercase font-bold">Inativo</span>}
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => setMaterialToEdit(m)} className="text-primary hover:underline font-semibold">Editar</button>
                      <button onClick={() => onToggleActive("/api/v1/pedagogy/materials", m.id, m.is_active !== false)} className={`${m.is_active !== false ? "text-error" : "text-ok"} hover:underline font-semibold`}>
                        {m.is_active !== false ? "Inativar" : "Ativar"}
                      </button>
                      <button onClick={async () => {
                        if (window.confirm("Deseja realmente excluir este livro permanentemente?")) {
                          try {
                            await api(`/api/v1/pedagogy/materials/${m.id}`, { method: "DELETE" });
                            notify("Livro excluído com sucesso!");
                            await loadBase();
                          } catch (err) {
                            notify(err instanceof Error ? err.message : "Erro ao excluir livro.", "error");
                          }
                        }
                      }} className="text-error hover:underline font-semibold">Excluir</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Accordion para vincular Capítulos aos Livros */}
      {showPedagogyCreate && (
        <div className="border border-border rounded-2xl overflow-hidden bg-surface mt-4">
          <button
            onClick={() => setIsPedagogyItemExpanded(!isPedagogyItemExpanded)}
            className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Bookmark className="w-4.5 h-4.5 text-primary" />
              <span>Vincular Capítulos aos Livros</span>
            </div>
            {isPedagogyItemExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isPedagogyItemExpanded && (
            <div className="p-4 border-t border-border bg-background/20">
              <PedagogicalMaterialItemForm
                materials={materials}
                onSubmit={async (materialId, payload) => {
                  await api(`/api/v1/pedagogy/materials/${materialId}/items`, {
                    method: "POST",
                    body: JSON.stringify(payload)
                  });
                  await loadBase();
                }}
                onDeleteItem={async (itemId) => {
                  await api(`/api/v1/pedagogy/materials/items/${itemId}`, { method: "DELETE" });
                  await loadBase();
                }}
                onUpdateItem={async (itemId, payload) => {
                  await api(`/api/v1/pedagogy/materials/items/${itemId}`, {
                    method: "PUT",
                    body: JSON.stringify(payload)
                  });
                  await loadBase();
                }}
                notify={(msg, type) => notify(msg, type === "error" ? "error" : "ok")}
              />
            </div>
          )}
        </div>
      )}
      {/* Accordion para cadastrar Metodologia Pedagógica */}
      {showPedagogyCreate && (
        <div className="border border-border rounded-2xl overflow-hidden bg-surface mt-4">
          <button
            onClick={() => setIsMethodologyExpanded(!isMethodologyExpanded)}
            className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <GraduationCap className="w-4.5 h-4.5 text-primary" />
              <span>Gerenciar Metodologias (Cadastrar / Consultar / Editar)</span>
            </div>
            {isMethodologyExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isMethodologyExpanded && (
            <div className="p-4 border-t border-border bg-background/20">
              <PedagogicalMethodologyForm
                schoolId={selectedChild?.school_id}
                schools={schools}
                methodologyToEdit={methodologyToEdit}
                onCancelEdit={() => setMethodologyToEdit(null)}
                onSubmit={async (payload) => {
                  await onSubmit("/api/v1/pedagogy/methodologies", payload, methodologyToEdit ? "Metodologia atualizada." : "Metodologia cadastrada.");
                  setMethodologyToEdit(null);
                }}
                notify={(msg, type) => notify(msg, type === "error" ? "error" : "ok")}
              />

              <div className="mt-4 pt-4 border-t border-border/80 flex flex-col gap-2 max-h-40 overflow-y-auto">
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Metodologias Cadastradas ({methodologies.length})</span>
                {methodologies.map(m => (
                  <div key={m.id} className="flex justify-between items-center text-xs p-2 bg-background/45 rounded-lg border border-border/50">
                    <div>
                      <span className={`${m.is_active !== false ? "text-text-primary" : "text-text-muted line-through"}`}>{m.name}</span>
                      {m.is_active === false && <span className="ml-1 text-[8px] bg-error/20 text-error px-1 rounded uppercase font-bold">Inativo</span>}
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => setMethodologyToEdit(m)} className="text-primary hover:underline font-semibold">Editar</button>
                      <button onClick={() => onToggleActive("/api/v1/pedagogy/methodologies", m.id, m.is_active !== false)} className={`${m.is_active !== false ? "text-error" : "text-ok"} hover:underline font-semibold`}>
                        {m.is_active !== false ? "Inativar" : "Ativar"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Accordion para cadastrar Usuários */}
      {showSchoolCreate && (
        <div className="border border-border rounded-2xl overflow-hidden bg-surface mt-4">
          <button
            onClick={() => setIsUsersExpanded(!isUsersExpanded)}
            className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Users className="w-4.5 h-4.5 text-primary" />
              <span>Gerenciar Usuários (Cadastrar / Consultar / Editar)</span>
            </div>
            {isUsersExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isUsersExpanded && (
            <div className="p-4 border-t border-border bg-background/20">
              <UserCreateForm
                schools={schools}
                userToEdit={userToEdit}
                onCancelEdit={() => setUserToEdit(null)}
                onSubmit={async (payload) => {
                  await onSubmit("/api/v1/auth/users", payload, userToEdit ? "Usuário atualizado." : "Usuário cadastrado.");
                  setUserToEdit(null);
                }}
              />

              <div className="mt-4 pt-4 border-t border-border/80 flex flex-col gap-2 max-h-40 overflow-y-auto">
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Usuários Cadastrados ({usersList.length})</span>
                {usersList.map(u => (
                  <div key={u.id} className="flex justify-between items-center text-xs p-2 bg-background/45 rounded-lg border border-border/50">
                    <div>
                      <span className={`${u.is_active !== false ? "text-text-primary" : "text-text-muted line-through"}`}>{u.name} ({u.role === "guardian" ? "Responsável" : u.role})</span>
                      {u.is_active === false && <span className="ml-1 text-[8px] bg-error/20 text-error px-1 rounded uppercase font-bold">Inativo</span>}
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => setUserToEdit(u)} className="text-primary hover:underline font-semibold">Editar</button>
                      <button onClick={() => onToggleActive("/api/v1/auth/users", u.id, u.is_active !== false)} className={`${u.is_active !== false ? "text-error" : "text-ok"} hover:underline font-semibold`}>
                        {u.is_active !== false ? "Inativar" : "Ativar"}
                      </button>
                      <button onClick={() => onDeleteUser(u.id)} className="text-error hover:underline font-semibold">Excluir</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Accordion para LGPD & Privacidade */}
      {selectedChildId && (
        <div className="border border-border rounded-2xl overflow-hidden bg-surface mt-4">
          <button
            onClick={() => setIsLgpdExpanded(!isLgpdExpanded)}
            className="w-full px-5 py-4 flex items-center justify-between text-sm font-bold text-text-primary hover:bg-surface-hover/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Shield className="w-4.5 h-4.5 text-primary" />
              <span>Privacidade & LGPD (Portabilidade / Esquecimento)</span>
            </div>
            {isLgpdExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isLgpdExpanded && (
            <div className="p-4 border-t border-border bg-background/20 flex flex-col gap-3">
              <p className="text-[10px] text-text-muted leading-relaxed">
                Em conformidade com a LGPD, você pode baixar seus dados ou solicitar a exclusão total do prontuário deste aluno.
              </p>
              <div className="flex flex-col gap-2">
                <Button
                  onClick={() => {
                    window.open(`/api/v1/children/${selectedChildId}/export-lgpd`, "_blank");
                  }}
                  variant="outline"
                  className="w-full text-xs py-2 flex items-center justify-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" /> Exportar Dados (Portabilidade)
                </Button>
                <Button
                  onClick={async () => {
                    if (window.confirm("ATENÇÃO: Esta ação é irreversível. Todos os dados pedagógicos, rotinas, tarefas e histórico deste aluno serão excluídos permanentemente. Deseja continuar?")) {
                      try {
                        await api(`/api/v1/children/${selectedChildId}/forget-lgpd`, { method: "DELETE" });
                        notify("Todos os dados do aluno foram apagados definitivamente.");
                        window.location.reload();
                      } catch (err) {
                        notify(err instanceof Error ? err.message : "Erro ao excluir dados.", "error");
                      }
                    }
                  }}
                  className="w-full text-xs py-2 bg-error hover:bg-error/95 text-white flex items-center justify-center gap-1.5"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Excluir Todos os Dados (Esquecimento)
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <>
      {user && !user.lgpd_accepted && (
        <LgpdConsentModal
          onAccept={() => {
            setUser({ ...user, lgpd_accepted: true });
            notify("Consentimento LGPD registrado com sucesso!");
          }}
        />
      )}
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
          {/* Navegação de Abas do Dashboard */}
          <div className="flex border-b border-border gap-6 mb-2">
            <button
              onClick={() => setActiveDashboardTab("overview")}
              className={`pb-2.5 text-sm font-bold border-b-2 transition-all duration-200 ${
                activeDashboardTab === "overview"
                  ? "border-primary text-primary"
                  : "border-transparent text-text-muted hover:text-text-primary"
              }`}
            >
              Visão Geral
            </button>
            <button
              onClick={() => setActiveDashboardTab("metrics")}
              className={`pb-2.5 text-sm font-bold border-b-2 transition-all duration-200 ${
                activeDashboardTab === "metrics"
                  ? "border-primary text-primary"
                  : "border-transparent text-text-muted hover:text-text-primary"
              }`}
            >
              Relatórios & Métricas
            </button>
          </div>

          {activeDashboardTab === "overview" ? (
            <>
              {/* Seção 1: Nova Rotina / Nova Tarefa */}
          {showPedagogyCreate && (
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
          )}

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
              showGenerateButton={showPedagogyCreate}
            />
            <div className="flex flex-col gap-6">
              {showPedagogyCreate && (
                <EvolutionEventCreateForm
                  childId={selectedChildId}
                  onSubmit={(payload) => onSubmit("/api/v1/evolution-events", payload, "Evento de evolução registrado com sucesso.")}
                />
              )}
              <EvolutionSummary
                childId={selectedChildId}
                summaryText={summary}
                onGenerateSummary={onGenerateAISummary}
              />
              <FamilyInteractions
                childId={selectedChildId}
                notify={(msg, type) => notify(msg, type === "error" ? "error" : "ok")}
              />
            </div>
          </section>

          {/* Seção Pedagógica Integrada */}
          <div className="border-t border-border/60 pt-6 mt-2">
            <h3 className="text-sm font-black uppercase tracking-wider text-text-primary mb-4 flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-primary" /> Módulo Pedagógico Integrado
            </h3>
            
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              {showPedagogyCreate && (
                <div className="xl:col-span-1">
                  <DailyRecordForm
                    childId={selectedChildId}
                    recordToEdit={dailyRecordToEdit}
                    onCancelEdit={() => setDailyRecordToEdit(null)}
                    onSubmit={async (payload) => {
                      await onSubmit("/api/v1/pedagogy/daily-records", payload, dailyRecordToEdit ? "Relatório diário atualizado." : "Relatório diário registrado.");
                      setDailyRecordToEdit(null);
                    }}
                    notify={(msg, type) => notify(msg, type === "error" ? "error" : "ok")}
                  />
                </div>
              )}
              <div className={`${showPedagogyCreate ? "xl:col-span-2" : "xl:col-span-3"} grid grid-cols-1 md:grid-cols-2 gap-6`}>
                <DailyRecordList
                  records={dailyRecords}
                  showActions={showPedagogyCreate}
                  onEdit={(r) => setDailyRecordToEdit(r)}
                  onToggleActive={async (id) => {
                    const record = dailyRecords.find((item) => item.id === id);
                    await onToggleActive("/api/v1/pedagogy/daily-records", id, record?.is_active !== false);
                  }}
                />
                <PedagogicalMaterialList
                  materials={materials}
                  showActions={showPedagogyCreate}
                  onEdit={(m) => setMaterialToEdit(m)}
                  onToggleActive={async (id) => {
                    const material = materials.find((item) => item.id === id);
                    await onToggleActive("/api/v1/pedagogy/materials", id, material?.is_active !== false);
                  }}
                  onDeleteItem={async (itemId) => {
                    if (window.confirm("Deseja realmente excluir este capítulo do livro?")) {
                      try {
                        await api(`/api/v1/pedagogy/materials/items/${itemId}`, { method: "DELETE" });
                        notify("Capítulo excluído com sucesso!");
                        await loadBase();
                      } catch (err) {
                        notify(err instanceof Error ? err.message : "Erro ao excluir capítulo.", "error");
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>

              {/* Seção 3: Visualização em Listas / Tabelas */}
              <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <RoutineList routines={routines} />
                <TaskList tasks={tasks} />
              </section>
            </>
          ) : (
            <MetricsDashboard childId={selectedChildId} />
          )}
        </div>
      )}
    </AppShell>
    </>
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
