from typing import Optional

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from ..core.config import Settings


class Neo4jClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._driver: Optional[object] = None

    def connect(self) -> None:
        if self._driver is not None:
            return

        try:
            self._driver = GraphDatabase.driver(
                self._settings.NEO4J_URI,
                auth=(self._settings.NEO4J_USER, self._settings.NEO4J_PASSWORD),
                max_connection_pool_size=self._settings.NEO4J_MAX_POOL_SIZE,
                max_connection_lifetime=self._settings.NEO4J_MAX_CONN_LIFETIME,
            )
            self._driver.verify_connectivity()
        except (ServiceUnavailable, Neo4jError) as exc:
            self._driver = None
            raise RuntimeError("Failed to connect to Neo4j") from exc

    def close(self) -> None:
        if self._driver is None:
            return
        self._driver.close()
        self._driver = None

    @property
    def driver(self) -> object:
        if self._driver is None:
            raise RuntimeError("Neo4j driver not initialized")
        return self._driver
