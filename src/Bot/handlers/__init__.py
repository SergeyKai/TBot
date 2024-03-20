from .main_handlers import router as main_router
from .pars_handlers import router as pars_router

main_router.include_router(pars_router)
