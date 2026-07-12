.PHONY: dev test lint migrate revision generate-notifications

dev:
	docker compose up --build

test:
	cd backend && pytest

test-integration:
	docker compose up -d db_test
	cd backend && DATABASE_URL=postgresql+psycopg://paimae:paimae@localhost:5433/paimae_test pytest

lint:
	cd backend && python -m compileall app alembic tests

migrate:
	cd backend && alembic upgrade head

revision:
	cd backend && alembic revision --autogenerate -m "$(m)"

generate-notifications:
	cd backend && python -m app.workers.generate_notifications $(date)
