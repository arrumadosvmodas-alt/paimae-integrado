import sys
from datetime import date

from app.db.session import SessionLocal
from app.services.notifications import generate_notifications_for_date


def main() -> None:
    target_date = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else date.today()
    with SessionLocal() as db:
        created = generate_notifications_for_date(db, target_date)
        db.commit()
        print(f"created={len(created)} target_date={target_date.isoformat()}")


if __name__ == "__main__":
    main()

