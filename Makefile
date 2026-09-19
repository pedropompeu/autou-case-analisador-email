.PHONY: help install dev-install test lint format clean docker-build docker-up docker-down migrate

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências de produção
	pip install -r requirements.txt

dev-install: ## Instala dependências de desenvolvimento
	pip install -r requirements-dev.txt

test: ## Executa testes
	pytest backend/tests/ -v

test-cov: ## Executa testes com cobertura
	pytest backend/tests/ --cov=backend/app --cov-report=html --cov-report=term

lint: ## Executa linting
	flake8 backend/
	mypy backend/

format: ## Formata código
	black backend/
	isort backend/

clean: ## Remove arquivos temporários
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

docker-build: ## Build das imagens Docker
	docker-compose build

docker-up: ## Inicia containers
	docker-compose up -d

docker-down: ## Para containers
	docker-compose down

docker-logs: ## Mostra logs dos containers
	docker-compose logs -f

migrate: ## Executa migrações do banco
	docker-compose exec backend flask db upgrade

migrate-create: ## Cria nova migração
	docker-compose exec backend flask db migrate -m "$(msg)"

shell: ## Abre shell Python no container
	docker-compose exec backend python

db-shell: ## Abre shell do PostgreSQL
	docker-compose exec postgres psql -U postgres -d email_analyzer

redis-cli: ## Abre Redis CLI
	docker-compose exec redis redis-cli

init: docker-build docker-up migrate ## Inicialização completa do projeto
	@echo "✅ Projeto inicializado! Acesse http://localhost:5000"

restart: docker-down docker-up ## Reinicia containers

quality: format lint test ## Executa todos os checks de qualidade
