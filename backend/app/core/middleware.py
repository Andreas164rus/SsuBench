import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)

        logger.info(f"{request.method} {request.url.path} | IP: {client_ip}")

        response = await call_next(request)

        logger.info(f"{response.status_code} | IP: {client_ip}")

        return response

    def get_client_ip(self, request: Request) -> str:
        """Получение реального IP клиента за прокси"""
        # Проверяем заголовки прокси (если приложение за nginx)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Берем первый IP (реальный клиент)
            return forwarded.split(",")[0].strip()

        # Альтернативные заголовки
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Стандартный IP
        if request.client:
            return request.client.host
