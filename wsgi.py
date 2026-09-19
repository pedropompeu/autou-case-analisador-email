"""
WSGI entry point para produção (Gunicorn).
"""
import os
import sys

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app

# Criar aplicação
app = create_app()

if __name__ == "__main__":
    # Para desenvolvimento local
    app.run(host="0.0.0.0", port=5000, debug=True)
