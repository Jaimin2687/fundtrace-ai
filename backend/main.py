from fastapi import FastAPI

from .api.v1.graph import router as graph_router
from .api.v1.stream import router as stream_router
from .api.v1.stream import start_broadcaster, stop_broadcaster
from .core.config import get_settings
from .core.security import configure_cors
from .db.neo4j_client import Neo4jClient


settings = get_settings()
neo4j_client = Neo4jClient(settings)

app = FastAPI(title="FundTrace AI API", version="0.1.0")
configure_cors(app, settings)
app.include_router(graph_router)
app.include_router(stream_router)


@app.on_event("startup")
def on_startup() -> None:
    neo4j_client.connect()
    app.state.neo4j_driver = neo4j_client.driver
    if settings.STREAM_MOCK_MODE:
        start_broadcaster()


@app.on_event("shutdown")
def on_shutdown() -> None:
    stop_broadcaster()
    neo4j_client.close()


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}
