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


def build_child_interaction(db: Session, child_id, interaction_type: str) -> dict:
    """
    Gera uma sugestão de interação explícita (conversa, pergunta ou orientação)
    baseada nos dados pedagógicos e comportamentais da criança.
    """
    child = db.get(Child, child_id)
    if not child:
        return {"status": "error", "content": "Criança não encontrada."}

    # Busca eventos de evolução
    events = list(
        db.scalars(
            select(EvolutionEvent)
            .where(EvolutionEvent.child_id == child_id)
            .order_by(EvolutionEvent.occurred_at.desc())
            .limit(10)
        )
    )

    # Busca diários
    daily_records = list(
        db.scalars(
            select(DailySchoolRecord)
            .where(DailySchoolRecord.child_id == child_id)
            .order_by(DailySchoolRecord.date.desc())
            .limit(10)
        )
    )

    total_data_points = len(events) + len(daily_records)
    if total_data_points < MIN_DATA_POINTS_FOR_SUMMARY:
        return {
            "status": "insufficient_data",
            "content": "Insira mais registros diários ou eventos de evolução (mínimo de 3 registros ao todo) para liberar essa sugestão pedagógica.",
        }

    # Busca materiais didáticos
    materials = list(
        db.scalars(
            select(PedagogicalMaterial)
            .where(PedagogicalMaterial.school_id == child.school_id)
            .limit(5)
        )
    )

    last_record = daily_records[0] if daily_records else None
    last_event = events[0] if events else None

    if interaction_type == "conversation":
        if last_record:
            subject_info = f" na aula de {materials[0].subject}" if materials else ""
            content = (
                f"💬 **Roteiro de Conversa para hoje com {child.full_name}:**\n\n"
                f"1. Comece de forma calorosa: *'Oi, filho(a)! Como foi o seu dia hoje na escola?'*\n"
                f"2. Faça a ponte com a atividade realizada: *'Fiquei sabendo que hoje vocês trabalharam em: \"{last_record.summary}\"{subject_info}. O que você achou mais divertido?'*\n"
                f"3. Incentive a reflexão: *'Você conseguiu mostrar para o professor o que aprendeu?'*"
            )
        else:
            content = (
                f"💬 **Roteiro de Conversa para hoje com {child.full_name}:**\n\n"
                f"Pergunte sobre as conquistas do dia: *'Como foi seu dia hoje? Soube que você teve um evento de {last_event.event_type if last_event else 'evolução'} na escola. Me conta como foi!'*"
            )

    elif interaction_type == "question":
        if last_record and last_record.observed_skills:
            first_skill = last_record.observed_skills.split(",")[0].strip()
            content = (
                f"❓ **Pergunta reflexiva para fazer a {child.full_name}:**\n\n"
                f"*'Hoje na escola você praticou a habilidade de **{first_skill}**. Você sentiu algum desafio ou achou fácil fazer essa atividade?'*"
            )
        elif last_event:
            content = (
                f"❓ **Pergunta reflexiva para fazer a {child.full_name}:**\n\n"
                f"*'Hoje foi um dia voltado para {last_event.event_type}. O que você aprendeu de novo que gostaria de me ensinar?'*"
            )
        else:
            content = (
                f"❓ **Pergunta reflexiva para fazer a {child.full_name}:**\n\n"
                f"*'Qual foi a melhor coisa que aconteceu na sua aula hoje?'*"
            )

    elif interaction_type == "guidance":
        skills_text = f" habilidades como '{last_record.observed_skills}'" if last_record and last_record.observed_skills else "as tarefas de aula"
        content = (
            f"🌟 **Orientação Pedagógica / Reforço Positivo:**\n\n"
            f"Elogie {child.full_name} hoje focando no esforço, não apenas no resultado! Diga algo como:\n"
            f"*'Estou muito orgulhoso(a) de ver como você está se dedicando a desenvolver {skills_text}. Continue assim!'*\n\n"
            f"**Dica de apoio:** Mantenha um ambiente calmo para as tarefas escolares e revise os cadernos juntos por 5 minutos."
        )
    else:
        return {"status": "error", "content": "Tipo de interação inválido."}

    return {"status": "ok", "content": content}

