from backend.app import create_app

app = create_app()
celery_app = app.extensions["celery"]
celery = celery_app

