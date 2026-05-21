"""
Shared evidence helpers for graph and export endpoints.
"""

from datetime import datetime, timezone
from typing import List

from neo4j import Driver
from neo4j.graph import Node

from .schemas import EvidencePackage


def _node_identifier(node: Node) -> str:
    return str(
        node.get("txId")
        or node.get("tx_id")
        or node.get("account_id")
        or node.get("accountId")
        or node.id
    )

def _node_amount(node: Node) -> float | None:
    raw = node.get("amount")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def pattern_from_score(risk_score: float) -> str:
    if risk_score >= 0.90:
        return "Round-tripping"
    if risk_score >= 0.85:
        return "Layering"
    if risk_score >= 0.80:
        return "Structuring"
    if risk_score >= 0.75:
        return "Dormant Account Activated"
    return "Normal"


def fetch_chain_nodes(driver: Driver, tx_id: str) -> List[Node]:
    """Fetch the longest transaction chain for a given transaction ID."""
    query = """
    MATCH (t:Transaction)
    WHERE t.txId = $txId OR t.tx_id = $txId
    OPTIONAL MATCH path_out=(t)-[:TRANSFERRED_TO|SENT_TO*1..6]->(n1:Transaction)
    OPTIONAL MATCH path_in=(n2:Transaction)-[:TRANSFERRED_TO|SENT_TO*1..6]->(t)
    WITH t,
         collect(DISTINCT path_out) AS out_paths,
         collect(DISTINCT path_in) AS in_paths
    WITH t, out_paths + in_paths AS all_paths
    UNWIND all_paths AS p
    WITH p WHERE p IS NOT NULL
    WITH p, length(p) AS pathLength
    ORDER BY pathLength DESC
    LIMIT 1
    RETURN nodes(p) AS chain_nodes
    """

    with driver.session() as session:
        result = session.run(query, txId=tx_id).single()

        if result is None or not result["chain_nodes"]:
            single_result = session.run(
                """
                MATCH (t:Transaction)
                WHERE t.txId = $txId OR t.tx_id = $txId
                RETURN t
                """,
                txId=tx_id,
            ).single()

            if single_result is None:
                return []

            return [single_result["t"]]

        chain_nodes = result["chain_nodes"]
        ordered: List[Node] = []
        seen = set()
        for node in chain_nodes:
            node_id = _node_identifier(node)
            if node_id in seen:
                continue
            ordered.append(node)
            seen.add(node_id)
        return ordered


def build_evidence_package(chain_nodes: List[Node], tx_id: str) -> EvidencePackage:
    chain = [str(node.get("txId")) for node in chain_nodes]
    risk_scores = [float(node.get("risk_score", 0.0)) for node in chain_nodes]
    patterns = [pattern_from_score(score) for score in risk_scores]

    amounts: List[float] = []
    selected_amount: float | None = None
    for node in chain_nodes:
        amount = _node_amount(node)
        if amount is not None:
            amounts.append(amount)
        if selected_amount is None and _node_identifier(node) == tx_id:
            selected_amount = amount

    if selected_amount is not None:
        total_amount = selected_amount
    elif amounts:
        total_amount = sum(amounts)
    else:
        total_amount = sum(risk_scores) * 10000
    max_score = max(risk_scores) if risk_scores else 0.0
    high_risk = sum(1 for score in risk_scores if score >= 0.85)
    structuring_hits = patterns.count("Structuring")
    layering_hits = patterns.count("Layering")
    round_trip_hits = patterns.count("Round-tripping")

    primary_pattern = patterns[risk_scores.index(max_score)] if patterns else "Unknown"
    narrative = (
        f"Transaction {tx_id} initiated a {primary_pattern} chain spanning "
        f"{len(chain)} hops with {high_risk} high-risk nodes. "
    )
    if structuring_hits:
        narrative += f"Structuring detected in {structuring_hits} nodes. "
    if layering_hits:
        narrative += f"Layering signals in {layering_hits} nodes. "
    if round_trip_hits:
        narrative += f"Round-tripping risk flagged in {round_trip_hits} nodes. "
    narrative += f"Aggregate risk score peak: {max_score:.2f}."

    return EvidencePackage(
        txId=tx_id,
        chain=chain,
        risk_scores=risk_scores,
        patterns=patterns,
        total_amount=total_amount,
        generated_at=datetime.now(timezone.utc),
        narrative=narrative,
    )
