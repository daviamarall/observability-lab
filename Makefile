.PHONY: help up down logs traffic test lint clean

help:
	@echo "up       - sobe toda a stack (docker compose up --build)"
	@echo "down     - derruba a stack"
	@echo "logs     - logs seguidos"
	@echo "traffic  - gera trafego de exemplo contra a API"
	@echo "test     - testes da aplicacao"
	@echo "lint     - ruff na aplicacao"

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f

traffic:
	bash scripts/traffic.sh

test:
	cd app && python -m pytest -q

lint:
	cd app && ruff check src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
