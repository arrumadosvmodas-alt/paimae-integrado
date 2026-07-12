from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evolution import EvolutionEvent


MIN_EVENTS_FOR_SUMMARY = 3


def build_child_summary(db: Session, child_id):
    events = list(
        db.scalars(
            select(EvolutionEvent)
            .where(EvolutionEvent.child_id == child_id)
            .order_by(EvolutionEvent.occurred_at.desc())
            .limit(20)
        )
    )
    if len(events) < MIN_EVENTS_FOR_SUMMARY:
        return {
            "status": "insufficient_data",
            "summary": "Dados insuficientes para gerar uma avaliacao confiavel da crianca.",
            "data_points": len(events),
        }
    scores = [event.score for event in events if event.score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None
    event_types = sorted({event.event_type for event in events})
    summary = f"Foram analisados {len(events)} eventos recentes"
    if avg_score is not None:
        summary += f", com media de pontuacao {avg_score}"
    summary += f". Tipos registrados: {', '.join(event_types)}."
    return {"status": "ok", "summary": summary, "data_points": len(events)}

