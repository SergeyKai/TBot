from .main_handlers import router as admin_router
from .vk_console import router as vk_console_router
from .tg_console import router as tg_console_router

admin_router.include_routers(
    vk_console_router,
    tg_console_router,
)
