# Design System - Pai&MaeIntegrado

Este documento detalha as decisões de design, tokens visuais e arquitetura de componentes criados para o redesenho visual profissional e responsivo da plataforma **Pai&MaeIntegrado**. O design foi desenvolvido com base nas diretrizes do **Stitch MCP**, utilizando o conceito de **Vibrant Professionalism**.

---

## 1. Princípios de Design

1. **Confiança e Acolhimento**: A aplicação atende a escolas e famílias. O design deve transmitir estabilidade institucional (através do azul profissional) com toques acolhedores e vibrantes.
2. **Clareza de Dados**: Informações sobre rotinas e evolução escolar de crianças devem ser de fácil leitura, com contraste correto, tipografia legível e gráficos/estatísticas estruturados.
3. **Eficiência Operacional**: Layouts focados na facilidade de uso diário (ex: criar tarefas ou rotinas rapidamente), com feedback visual imediato e suporte a atalhos e acessibilidade por teclado.
4. **Design Adaptativo**: Interface responsiva de ponta a ponta (Desktop, Tablet e Mobile), mantendo consistência em todas as resoluções.
5. **Tema Dual**: Suporte completo a tema Claro (Light Mode) e tema Escuro (Dark Mode) utilizando classes utilitárias do Tailwind CSS baseadas no seletor `.dark`.

---

## 2. Design Tokens

Não são utilizadas cores fixas (hardcoded hex) diretamente nos componentes. Toda a estilização consome os tokens centralizados definidos na configuração do Tailwind.

### 2.1. Cores e Temas

| Token | Propósito | Tema Claro (Light) | Tema Escuro (Dark) |
| :--- | :--- | :--- | :--- |
| **`primary`** | Marca principal, ações primárias, foco | `#0052FF` (Electric Blue) | `#3B82F6` (Lighter Blue) |
| **`secondary`** | Sucesso, conclusões, marcos positivos | `#00C853` (Vibrant Green) | `#10B981` (Emerald Green) |
| **`tertiary`** | Alertas, metas, status pendente | `#FFAB00` (Amber) | `#F59E0B` (Amber Dark) |
| **`error`** | Ações destrutivas, erros críticos | `#FF5252` (Red) | `#EF4444` (Red Dark) |
| **`background`** | Tela de fundo da aplicação | `#F5F7FB` | `#0F172A` (Slate 900) |
| **`surface`** | Cards, painéis, inputs, sidebar | `#FFFFFF` | `#1E293B` (Slate 800) |
| **`surface-hover`** | Estados de hover em cards/itens | `#F8FAFD` | `#334155` (Slate 700) |
| **`border`** | Linhas divisórias, bordas de componentes | `#E5EAF2` | `#334155` (Slate 700) |
| **`text-primary`** | Texto principal e cabeçalhos | `#172033` (Slate 900) | `#F8FAFC` (Slate 50) |
| **`text-muted`** | Texto secundário, rótulos e apoios | `#5D6B82` (Slate 600) | `#94A3B8` (Slate 400) |

### 2.2. Tipografia

A hierarquia de fontes foi otimizada para legibilidade e visual corporativo limpo.
- **Família da Fonte**:
  - Títulos e Destaques: `Plus Jakarta Sans`, `ui-sans-serif`, `system-ui`
  - Corpo de texto, formulários e metadados: `Inter`, `ui-sans-serif`
- **Escala Tipográfica**:
  - `Display / H1`: `28px` (desktop: `32px`), Bold (peso `700`)
  - `Subtítulo / H2`: `18px` (desktop: `20px`), SemiBold (peso `600`)
  - `Corpo Grande`: `16px`, Regular (peso `400`)
  - `Corpo Médio`: `14px`, Regular (peso `400`)
  - `Labels / Metadados`: `12px`, SemiBold/Medium (peso `500` / `600`), com leve espaçamento adicional (`tracking-wide`).

### 2.3. Espaçamento e Grid

Ritmo de espaçamento estrito baseado em múltiplos de `4px` (padrão Tailwind):
- `base`: `4px` (`space-1` / `p-1`)
- `xs`: `8px` (`space-2` / `p-2`)
- `sm`: `12px` (`space-3` / `p-3`)
- `md`: `16px` (`space-4` / `p-4`)
- `lg`: `24px` (`space-6` / `p-6`)
- `xl`: `32px` (`space-8` / `p-8`)

### 2.4. Arredondamentos (Bordas)

- Componentes pequenos (botões, badges, inputs): `8px` (`rounded-lg`)
- Componentes médios (cards, painéis de formulário): `16px` (`rounded-2xl`)
- Avatares e Chips de status: `9999px` (`rounded-full`)

---

## 3. Arquitetura de Componentes

Para evitar arquivos sobrecarregados e garantir reuso, a interface é fragmentada nas seguintes categorias:

### 3.1. Design System Core (Base UI)
Componentes agnósticos a regras de negócio:
- `Button`: Botão com variações `primary`, `secondary`, `outline`, `ghost` e estados de loading e desabilitado.
- `Card`: Contêiner com padding, sombra suave e suporte a hover interativo.
- `Input` / `Select` / `Textarea`: Campos de formulário com rótulo (label) integrado, validação visual e foco de alta acessibilidade.
- `Badge`: Chips de status estilizados para diferentes prioridades (success, warning, error, neutral).
- `Skeleton`: Espaço reservado com animação pulsação para carregamentos assíncronos.
- `Toast`: Notificações flutuantes com animação de entrada e auto-hide.

### 3.2. Layout
- `AppShell`: Estrutura de navegação global.
- `Sidebar`: Barra lateral recolhível com links de navegação rápida e informações contextuais do app.
- `Topbar`: Cabeçalho responsivo com seletor de perfil e ações rápidas.

### 3.3. Domínios de Negócio (Domain Components)
Componentes organizados e tipados estritamente:
- **School**: `SchoolCreateForm`
- **Child**: `ChildSelector`, `ChildCreateForm`
- **Routine**: `RoutineCreateForm`, `RoutineList`
- **Task**: `TaskCreateForm`, `TaskList`
- **Notification**: `NotificationList`
- **Evolution**: `EvolutionEventCreateForm`, `EvolutionSummary`

---

## 4. Requisitos de Acessibilidade (a11y)

- **Foco Visível**: Elementos focáveis pelo teclado possuem anel de foco evidente (`ring-2 ring-primary ring-offset-2`).
- **Navegação por Tabulação**: Todos os formulários seguem ordem lógica de `tabindex`.
- **Contraste**: Relação de contraste mínima de 4.5:1 para textos médios e 3:1 para títulos, tanto em tema claro quanto escuro.
- **Aria Attributes**: Utilização de `aria-label`, `aria-hidden` e estados adequados nos botões e inputs interativos.
