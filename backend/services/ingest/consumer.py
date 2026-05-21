"""
fundtrace-ingest: Ingestion & Routing Service (mock implementation).
Listens to Kafka topics (cbs.transactions.raw) and writes to Neo4j.
"""

import json
from dataclasses import dataclass
from typing import Iterable

from ...core.universal_models import TransactionEdge, AccountNode


@dataclass
class RawTransaction:
    tx_id: str
    source_id: str
    target_id: str
    amount: float
    timestamp: str


def validate_transaction(raw: dict) -> TransactionEdge:
    return TransactionEdge(
        tx_id=str(raw["tx_id"]),
        source_id=str(raw["source_id"]),
        target_id=str(raw["target_id"]),
        amount=float(raw["amount"]),
        currency=raw.get("currency", "INR"),
        timestamp=raw["timestamp"],
        is_structuring_flag=bool(raw.get("is_structuring_flag", False)),
    )


def consume_mock_stream(events: Iterable[dict]) -> list[TransactionEdge]:
    """
    Mock consumer for local testing without Kafka.
    """
    validated = []
    for event in events:
        validated.append(validate_transaction(event))
    return validated


def run_demo() -> None:
    sample = [
        {
            "tx_id": "TX-DEMO-1",
            "source_id": "ACC-001",
            "target_id": "ACC-002",
            "amount": 250000.0,
            "timestamp": "2026-05-18T10:00:00Z",
            "currency": "INR",
            "is_structuring_flag": False,
        }
    ]
    events = consume_mock_stream(sample)
    print(f"[ingest] validated {len(events)} events")


if __name__ == "__main__":
    run_demo()
