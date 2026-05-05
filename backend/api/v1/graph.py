from typing import List

from fastapi import APIRouter, Request
from neo4j.graph import Node, Relationship

from .schemas import AccountNode, GraphFocusResponse, TransactionEdge

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


GRAPH_FOCUS_QUERY = """
MATCH (start:Account {account_id: $cluster_id})
CALL (start) {
    MATCH (start)-[:TRANSACTION*1..3]-(n:Account)
    WITH start, collect(DISTINCT n) AS neighbors
    RETURN neighbors + [start] AS nodes
}
WITH nodes[0..$node_limit] AS limited_nodes
UNWIND limited_nodes AS node
WITH collect(DISTINCT node) AS nodes
MATCH (a:Account)-[t:TRANSACTION]->(b:Account)
WHERE a IN nodes AND b IN nodes
RETURN nodes, collect(DISTINCT t) AS rels
"""

START_NODE_QUERY = """
MATCH (start:Account {account_id: $cluster_id})
RETURN start
"""


def _node_to_account(node: Node) -> AccountNode:
    props = dict(node)
    return AccountNode(
        account_id=str(props.get("account_id")),
        account_type=str(props.get("account_type")),
        kyc_risk_baseline=float(props.get("kyc_risk_baseline", 0.0)),
        total_volume=float(props.get("total_volume", 0.0)),
        aml_label=int(props.get("aml_label")) if props.get("aml_label") is not None else None,
    )


def _edge_to_transaction(rel: Relationship) -> TransactionEdge:
    props = dict(rel)
    return TransactionEdge(
        tx_id=str(props.get("tx_id")),
        source_id=str(props.get("source_id")),
        target_id=str(props.get("target_id")),
        amount=float(props.get("amount", 0.0)),
        timestamp=str(props.get("timestamp")),
        is_structuring=bool(props.get("is_structuring", False)),
    )


@router.get("/focus/{cluster_id}", response_model=GraphFocusResponse)
def get_focus_cluster(cluster_id: str, request: Request) -> GraphFocusResponse:
    driver = request.app.state.neo4j_driver
    node_limit = 150

    with driver.session() as session:
        result = session.run(
            GRAPH_FOCUS_QUERY, cluster_id=cluster_id, node_limit=node_limit
        ).single()
        if result is None:
            start_node = session.run(START_NODE_QUERY, cluster_id=cluster_id).single()
            if start_node is None:
                return GraphFocusResponse(nodes=[], edges=[])
            node = start_node["start"]
            return GraphFocusResponse(nodes=[_node_to_account(node)], edges=[])

        nodes: List[Node] = result["nodes"] or []
        rels: List[Relationship] = result["rels"] or []

    node_out = [_node_to_account(node) for node in nodes]
    edge_out = [_edge_to_transaction(rel) for rel in rels]

    return GraphFocusResponse(nodes=node_out, edges=edge_out)
