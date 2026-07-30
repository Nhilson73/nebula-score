import uvicorn

from backend.app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.api.main:app",
        host=settings.nebula_host,
        port=settings.nebula_port,
        reload=settings.nebula_env == "development",
    )
