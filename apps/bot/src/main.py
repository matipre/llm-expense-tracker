"""
Main entry point for the Bot Service.
"""
import uvicorn
from fastapi import FastAPI
from presentation.routers.health import router as health_router

app = FastAPI(
    title="Darwin Challenge - Bot Service",
    description="Python Bot Service for Telegram Expense Tracking",
    version="1.0.0"
)

# Register routers
app.include_router(health_router, prefix="/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=3002,
        reload=True,
        log_level="info"
    )
