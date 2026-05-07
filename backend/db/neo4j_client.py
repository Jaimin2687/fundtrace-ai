"""
Neo4j database client with singleton driver pattern.
"""

from typing import Optional
from urllib.parse import urlparse

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from ..core.config import Settings, get_settings


# Singleton driver instance
_driver: Optional[Driver] = None


def get_driver() -> Driver:
    """
    Get or create the singleton Neo4j driver instance.
    
    Returns:
        Neo4j Driver instance
        
    Raises:
        RuntimeError: If driver initialization fails
    """
    global _driver
    
    if _driver is not None:
        return _driver
    
    settings = get_settings()
    
    try:
        uri = settings.NEO4J_URI
        scheme = urlparse(uri).scheme

        # Handle TLS configuration for development
        ssl_context = None
        driver_uri = uri
        if ("+s" in scheme or "+ssc" in scheme) and not settings.NEO4J_ENCRYPTION:
            driver_uri = uri.replace("+s", "").replace("+ssc", "")
            import ssl

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        driver_kwargs = {
            "auth": (settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            "max_connection_pool_size": settings.NEO4J_MAX_POOL_SIZE,
            "max_connection_lifetime": settings.NEO4J_MAX_CONN_LIFETIME,
        }

        if ssl_context is not None:
            driver_kwargs["ssl_context"] = ssl_context
        else:
            if scheme in ("bolt", "neo4j"):
                driver_kwargs["encrypted"] = settings.NEO4J_ENCRYPTION

        _driver = GraphDatabase.driver(driver_uri, **driver_kwargs)
        _driver.verify_connectivity()
        
        return _driver
        
    except (ServiceUnavailable, Neo4jError) as exc:
        raise RuntimeError(f"Failed to connect to Neo4j: {exc}") from exc


def close_driver() -> None:
    """Close the singleton Neo4j driver instance."""
    global _driver
    
    if _driver is not None:
        _driver.close()
        _driver = None


# Legacy class for backward compatibility
class Neo4jClient:
    """Legacy Neo4j client class for backward compatibility."""
    
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._driver: Optional[Driver] = None

    def connect(self) -> None:
        """Connect to Neo4j using singleton driver."""
        self._driver = get_driver()

    def close(self) -> None:
        """Close connection (no-op for singleton)."""
        pass

    @property
    def driver(self) -> Driver:
        """Get the Neo4j driver instance."""
        if self._driver is None:
            self._driver = get_driver()
        return self._driver
