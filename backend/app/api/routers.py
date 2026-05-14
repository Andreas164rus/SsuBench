from fastapi import APIRouter

from app.api.endpoints import user_router, task_router, bid_router, payment_router

main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(task_router)
main_router.include_router(bid_router)
main_router.include_router(payment_router)
