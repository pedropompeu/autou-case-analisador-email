"""
Middleware para logging de requisições HTTP em formato JSON estruturado.

Logs de exemplo (linha única por request):
    {"ts": "2026-04-17 12:00:01", "method": "POST", "path": "/api/v1/analyze",
     "status": 200, "duration_ms": 1234}
"""
import json
import time
from logging import Logger
from typing import Callable


class RequestLoggerMiddleware:
    """
    Middleware WSGI que loga cada request em JSON estruturado.

    Compatível com sistemas de agregação de logs (Loki, ELK, CloudWatch).
    """

    def __init__(self, app: Callable, logger: Logger):
        self.app = app
        self.logger = logger

    def __call__(self, environ, start_response):
        start_time = time.time()
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "")
        remote_addr = environ.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or environ.get(
            "REMOTE_ADDR", ""
        )

        def custom_start_response(status, headers, exc_info=None):
            duration_ms = int((time.time() - start_time) * 1000)
            status_code = int(status.split()[0])

            log_record = {
                "event": "http_request",
                "method": method,
                "path": path,
                "status": status_code,
                "duration_ms": duration_ms,
                "remote_addr": remote_addr,
            }

            # Nível do log baseado no status code
            if status_code >= 500:
                self.logger.error(json.dumps(log_record, ensure_ascii=False))
            elif status_code >= 400:
                self.logger.warning(json.dumps(log_record, ensure_ascii=False))
            else:
                self.logger.info(json.dumps(log_record, ensure_ascii=False))

            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)
