#!/usr/bin/env python
"""
Script de gerenciamento da aplicação.
"""
import click
from flask.cli import FlaskGroup
from backend.app import create_app, db
from backend.app.models import EmailAnalysis


def create_cli_app():
    """Cria aplicação para CLI."""
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def cli():
    """Management script para Email Analyzer."""
    pass


@cli.command()
def init_db():
    """Inicializa o banco de dados."""
    click.echo("Criando tabelas...")
    db.create_all()
    click.echo("✅ Banco de dados inicializado!")


@cli.command()
def drop_db():
    """Remove todas as tabelas (CUIDADO!)."""
    if click.confirm("⚠️  Tem certeza? Isso vai apagar todos os dados!"):
        db.drop_all()
        click.echo("✅ Banco de dados limpo!")


@cli.command()
def seed_db():
    """Popula banco com dados de exemplo."""
    click.echo("Criando dados de exemplo...")

    # Exemplo de análise
    analysis = EmailAnalysis(
        content_hash="example_hash_123",
        email_content="Email de exemplo para testes",
        category="Produtivo",
        summary="Email de teste",
        suggested_response="Resposta de exemplo",
        processing_time_ms=100,
        model_used="gemini-1.5-flash",
    )

    db.session.add(analysis)
    db.session.commit()

    click.echo("✅ Dados de exemplo criados!")


@cli.command()
def test():
    """Executa os testes."""
    import pytest

    pytest.main(["-v", "backend/tests/"])


@cli.command()
def lint():
    """Executa linting."""
    import subprocess

    click.echo("Executando Black...")
    subprocess.run(["black", "backend/"])

    click.echo("Executando Flake8...")
    subprocess.run(["flake8", "backend/"])

    click.echo("Executando MyPy...")
    subprocess.run(["mypy", "backend/"])

    click.echo("✅ Linting completo!")


if __name__ == "__main__":
    cli()
