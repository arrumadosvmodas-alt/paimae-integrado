from typing import Annotated
from uuid import UUID
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.child import Child
from app.models.pedagogy import DailySchoolRecord
from app.models.task import Task
from app.models.evolution import EvolutionEvent
from app.services.permissions import ensure_child_access

router = APIRouter()


@router.get("/metrics")
def get_child_metrics(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Verifica acesso
    ensure_child_access(db, current_user, child_id)

    # 1. Estatísticas de Tarefas
    tasks = db.scalars(select(Task).where(Task.child_id == child_id)).all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status.lower() in ["completed", "concluida", "concluído"])
    pending_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    task_stats = {
        "total": total_tasks,
        "completed": completed_tasks,
        "pending": pending_tasks,
        "completion_rate": round(completion_rate, 1),
    }

    # 2. Histórico de Engajamento
    # Busca registros diários
    records = db.scalars(
        select(DailySchoolRecord)
        .where(DailySchoolRecord.child_id == child_id, DailySchoolRecord.is_active.is_(True))
        .order_by(DailySchoolRecord.date.asc())
    ).all()

    engagement_history = []
    for r in records:
        if r.engagement_score is not None:
            engagement_history.append({
                "date": r.date.strftime("%Y-%m-%d"),
                "score": r.engagement_score,
                "type": "daily_record"
            })

    # Busca eventos de evolução
    events = db.scalars(
        select(EvolutionEvent)
        .where(EvolutionEvent.child_id == child_id)
        .order_by(EvolutionEvent.occurred_at.asc())
    ).all()

    for e in events:
        if e.score is not None:
            engagement_history.append({
                "date": e.occurred_at.date().strftime("%Y-%m-%d"),
                "score": e.score,
                "type": "evolution_event"
            })

    # Ordena histórico por data
    engagement_history.sort(key=lambda x: x["date"])

    # 3. Distribuição de Áreas Curriculares / Habilidades Trabalhadas
    subject_counts = {}
    for r in records:
        if r.observed_skills:
            # Divide habilidades por vírgula e limpa espaços
            skills = [s.strip() for s in r.observed_skills.split(",") if s.strip()]
            for skill in skills:
                # Normaliza capitalização
                skill_normalized = skill.capitalize()
                subject_counts[skill_normalized] = subject_counts.get(skill_normalized, 0) + 1

    subject_distribution = [
        {"subject": k, "count": v} for k, v in sorted(subject_counts.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        "task_stats": task_stats,
        "engagement_history": engagement_history,
        "subject_distribution": subject_distribution,
    }


@router.get("/export-html", response_class=HTMLResponse)
def export_child_report_html(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id)
    child = db.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    metrics = get_child_metrics(child_id, db, current_user)
    
    # Renderização de uma página HTML simples e limpa para impressão
    history_rows = ""
    for entry in metrics["engagement_history"]:
        history_rows += f"<tr><td>{entry['date']}</td><td>{entry['score']}/5</td><td>{entry['type']}</td></tr>"

    subject_rows = ""
    for entry in metrics["subject_distribution"]:
        subject_rows += f"<tr><td>{entry['subject']}</td><td>{entry['count']} vezes</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Pedagógico - {child.name}</title>
        <style>
            body {{ font-family: sans-serif; color: #333; margin: 40px; line-height: 1.5; }}
            h1 {{ border-bottom: 2px solid #3b82f6; padding-bottom: 8px; color: #1e3a8a; }}
            h2 {{ color: #1e3a8a; margin-top: 30px; }}
            .student-info {{ background: #f3f4f6; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .student-info p {{ margin: 5px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #e5e7eb; padding: 10px; text-align: left; }}
            th {{ background-color: #f9fafb; font-weight: bold; }}
            .kpi-container {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .kpi-card {{ flex: 1; background: #eff6ff; border: 1px solid #bfdbfe; padding: 15px; border-radius: 8px; text-align: center; }}
            .kpi-val {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
            @media print {{
                body {{ margin: 20px; }}
                button {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div style="text-align: right; margin-bottom: 20px;">
            <button onclick="window.print()" style="padding: 10px 20px; background: #2563eb; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">Imprimir Relatório</button>
        </div>
        
        <h1>Relatório de Evolução Pedagógica</h1>
        
        <div class="student-info">
            <p><strong>Aluno(a):</strong> {child.name}</p>
            <p><strong>Data de Nascimento:</strong> {child.birth_date.strftime("%d/%m/%Y") if child.birth_date else "Não cadastrado"}</p>
            <p><strong>Gerado em:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </div>

        <h2>Métricas de Desempenho e Tarefas</h2>
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-val">{metrics['task_stats']['completion_rate']}%</div>
                <div>Taxa de Conclusão</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{metrics['task_stats']['completed']}</div>
                <div>Tarefas Concluídas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{metrics['task_stats']['pending']}</div>
                <div>Tarefas Pendentes</div>
            </div>
        </div>

        <h2>Componentes Curriculares Trabalhados</h2>
        <table>
            <thead>
                <tr>
                    <th>Componente / Habilidade</th>
                    <th>Frequência</th>
                </tr>
            </thead>
            <tbody>
                {subject_rows if subject_rows else "<tr><td colspan='2'>Nenhuma habilidade registrada no período.</td></tr>"}
            </tbody>
        </table>

        <h2>Histórico de Engajamento Comportamental</h2>
        <table>
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Nota de Engajamento</th>
                    <th>Origem</th>
                </tr>
            </thead>
            <tbody>
                {history_rows if history_rows else "<tr><td colspan='3'>Nenhum registro de engajamento no período.</td></tr>"}
            </tbody>
        </table>

        <div style="margin-top: 50px; border-top: 1px solid #9ca3af; padding-top: 20px; text-align: center; font-size: 12px; color: #6b7280;">
            Pai&Mãe Integrado - Acompanhamento Escolar em Parceria com a Família
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
