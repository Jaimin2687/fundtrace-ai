"""
fundtrace-scoring: ML Scoring Engine (mock implementation).
Calculates graph features and generates ExplainableNarrative.
"""

import random
from datetime import datetime, timezone

from ...core.universal_models import (
    AlertPayload,
    ExplainableNarrative,
    AccountNode,
    TransactionEdge,
)


def generate_mock_alert(cluster_id: str) -> AlertPayload:
    narrative = ExplainableNarrative(
        threat_type=random.choice(["Round-Tripping", "Rapid Layering", "Smurfing"]),
        risk_score=round(random.uniform(85, 99), 2),
        feature_contributions={"velocity": 0.34, "centrality": 0.27, "amount": 0.18},
        human_readable_text="Rapid multi-hop transfers detected across related accounts.",
    )
    nodes = [
        AccountNode(
            account_id=f"ACC-{i:03d}",
            entity_type=random.choice(["Retail", "Corporate", "Shell", "Unknown"]),
            kyc_risk_tier=random.randint(1, 5),
            total_30d_volume=random.uniform(1e5, 5e6),
            created_at=datetime.now(timezone.utc),
        )
        for i in range(1, 4)
    ]
    edges = [
        TransactionEdge(
            tx_id=f"TX-{cluster_id}-{i}",
            source_id=nodes[i - 1].account_id,
            target_id=nodes[i % len(nodes)].account_id,
            amount=random.uniform(10000, 80000),
            currency="INR",
            timestamp=datetime.now(timezone.utc),
            is_structuring_flag=False,
        )
        for i in range(1, 3)
    ]
    return AlertPayload(
        cluster_id=cluster_id,
        narrative=narrative,
        nodes=nodes,
        edges=edges,
    )


def run_demo() -> None:
    alert = generate_mock_alert("CLUSTER-DEMO-1")
    print(f"[scoring] generated alert {alert.cluster_id} risk={alert.narrative.risk_score}")


if __name__ == "__main__":
    run_demo()
