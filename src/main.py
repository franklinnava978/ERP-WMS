from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.modules.tenants.router import router as tenants_router
from src.modules.auth.router import router as auth_router
from src.modules.catalog.router import router as catalog_router
from src.modules.topology.router import router as topology_router   
from src.modules.inventory.router import router as inventory_router
from src.modules.orders.router import router as orders_router
from src.modules.integrations.router import router as integrations_router   



app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers por módulos
app.include_router(tenants_router, prefix="/api/v1")       # Router para gestión de tenants y multi-tenancy
app.include_router(auth_router, prefix="/api/v1")          # Router para autenticación y autorización
app.include_router(catalog_router, prefix="/api/v1")       # Router para catálogo y productos
app.include_router(topology_router, prefix="/api/v1")      # Router para topología y estructura
app.include_router(inventory_router, prefix="/api/v1")     # Router para inventario y stock
app.include_router(orders_router, prefix="/api/v1")        # Router para órdenes y despacho
app.include_router(integrations_router, prefix="/api/v1")  # Router para integraciones y webhooks   





@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "environment": settings.ENV,
        "app": settings.PROJECT_NAME
    }