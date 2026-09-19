"""
Ponto de entrada WSGI para plataformas de hospedagem (Render, Heroku, Railway, Gunicorn).
Permite execução direta via `gunicorn app:app` ou `gunicorn wsgi:app`.
"""
from wsgi import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
