"""
WSGI entry point para produção (Gunicorn).
"""
import os
import sys

# Adicionar diretório raiz ao path para imports funcionarem
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.app import create_app

# Criar aplicação
app = create_app()

if __name__ == "__main__":
    # Para desenvolvimento local
    app.run(host="0.0.0.0", port=5000, debug=True)
