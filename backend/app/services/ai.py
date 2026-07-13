from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.evolution import EvolutionEvent
from app.models.pedagogy import DailySchoolRecord, PedagogicalMaterial, MaterialItem


MIN_DATA_POINTS_FOR_SUMMARY = 3


def build_child_summary(db: Session, child_id) -> dict:
    """
    Gera um resumo pedagógico integrando:
    - Eventos de evolução
    - Registros escolares diários
    - Materiais pedagógicos e seus itens (capítulo, tema, etc)
    """
    child = db.get(Child, child_id)
    if not child:
        return {
            "status": "error",
            "summary": "Criança não encontrada.",
            "data_points": 0,
        }

    # 1. Busca eventos de evolução
    events = list(
        db.scalars(
            select(EvolutionEvent)
            .where(EvolutionEvent.child_id == child_id)
            .order_by(EvolutionEvent.occurred_at.desc())
            .limit(20)
        )
    )

    # 2. Busca registros diários
    daily_records = list(
        db.scalars(
            select(DailySchoolRecord)
            .where(DailySchoolRecord.child_id == child_id)
            .order_by(DailySchoolRecord.date.desc())
            .limit(20)
        )
    )

    total_data_points = len(events) + len(daily_records)

    # Regra de segurança: Se não houver dados suficientes, responde que os dados são insuficientes
    if total_data_points < MIN_DATA_POINTS_FOR_SUMMARY:
        return {
            "status": "insufficient_data",
            "summary": "Dados insuficientes para gerar uma avaliação pedagógica confiável da criança.",
            "data_points": total_data_points,
        }

    # 3. Busca materiais pedagógicos e itens da escola da criança
    materials = list(
        db.scalars(
            select(PedagogicalMaterial)
            .where(PedagogicalMaterial.school_id == child.school_id)
            .limit(10)
        )
    )

    # Compilação dos dados para compor o resumo
    # Resumo dos eventos de evolução
    scores = [event.score for event in events if event.score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None
    event_types = sorted({event.event_type for event in events})

    summary_text = (
        f"Com base na análise de {len(events)} eventos de evolução e {len(daily_records)} registros diários "
        f"recentes sobre a criança {child.full_name}:\n\n"
    )

    # Detalhamento de Evolução
    if events:
        summary_text += f"- Evolução Comportamental/Pedagógica: Registrados eventos do tipo {', '.join(event_types)}"
        if avg_score is not None:
            summary_text += f" com média de aproveitamento de {avg_score}/100"
        summary_text += ".\n"

    # Detalhamento de Registros Diários
    if daily_records:
        engagements = [r.engagement_score for r in daily_records if r.engagement_score is not None]
        avg_engagement = round(sum(engagements) / len(engagements), 1) if engagements else None
        skills = {s.strip() for r in daily_records if r.observed_skills for s in r.observed_skills.split(",")}
        
        summary_text += f"- Desempenho em Aula: "
        if avg_engagement:
            summary_text += f"Nível de engajamento médio de {avg_engagement}/5. "
        if skills:
            summary_text += f"Habilidades e competências observadas: {', '.join(skills)}. "
        summary_text += f"Última atividade: '{daily_records[0].summary}'.\n"

    # Detalhamento de Livros e Itens Pedagógicos associados
    if materials:
        material_titles = []
        themes = []
        for mat in materials:
            material_titles.append(f"'{mat.title}' ({mat.subject} - Linha {mat.pedagogical_line})")
            for item in mat.items:
                ref = f"Cap. {item.chapter}" if item.chapter else ""
                ref_page = f"p. {item.page}" if item.page else ""
                ref_full = f" ({ref} {ref_page})".replace("  ", " ").strip()
                themes.append(f"{item.theme}{ref_full}")
                
        summary_text += f"- Material Didático Adotado: Utilizando {', '.join(material_titles)}.\n"
        if themes:
            summary_text += f"- Tópicos e Habilidades do Material: {', '.join(themes)}.\n"
        
        # Proposta de Interação
        orientations = [m.family_orientation for m in materials if m.family_orientation]
        if orientations:
            summary_text += f"\n👉 Orientação Pedagógica e Sugestão de Interação para a Família:\n{orientations[0]}\n"

    return {
        "status": "ok",
        "summary": summary_text.strip(),
        "data_points": total_data_points,
    }
