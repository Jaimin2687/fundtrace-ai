"""
Graph API endpoints for transaction network visualization and analysis.
Backed by Neo4j (no mock mode).

Performance notes (200k+ nodes):
- All synchronous Neo4j calls are dispatched via run_in_executor to avoid
  blocking the async event loop.
- Cypher queries are bounded with LIMIT to prevent full-graph scans.
- _trim_graph prioritizes fraud/high-risk nodes so they are never dropped.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from neo4j.graph import Node, Relationship

from ...core.security import verify_api_key
from ...core.auth import verify_investigator_access, AuthUser
from ...core.audit import audit_log
from ...db.neo4j_client import get_driver
from .schemas import GraphNode, GraphEdge, GraphResponse, EvidencePackage, GraphStats
from .evidence import build_evidence_package, fetch_chain_nodes, pattern_from_score

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])

# Thread pool for offloading synchronous Neo4j driver calls
_neo4j_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="neo4j")


def _get_driver(request: Request):
    driver = getattr(request.app.state, "neo4j_driver", None)
    if driver is None:
        driver = get_driver()
    if driver is None:
        raise HTTPException(status_code=503, detail="Neo4j driver not initialized")
    return driver


def _normalize_label(value) -> str:
    if value in ("fraud", "Fraud", 1, "1", True):
        return "fraud"
    if value in ("legit", "Legit", 0, "0", False):
        return "legit"
    return "unknown"


def _normalize_risk(score) -> float:
    if score is None:
        return 0.0
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0.0
    if value > 1.0:
        return min(value / 100.0, 1.0)
    return max(value, 0.0)


def _node_to_graph_node(node: Node) -> GraphNode:
    props = dict(node)
    tx_id = (
        props.get("txId")
        or props.get("tx_id")
        or props.get("account_id")
        or props.get("accountId")
        or str(node.id)
    )
    aml_label = _normalize_label(props.get("aml_label"))
    risk_score = _normalize_risk(props.get("risk_score"))
    time_step = props.get("time_step") or props.get("step")
    amount = props.get("amount")
    pattern = props.get("pattern") or pattern_from_score(risk_score)
    return GraphNode(
        txId=str(tx_id),
        aml_label=aml_label,
        risk_score=risk_score,
        time_step=int(time_step) if time_step is not None else None,
        amount=float(amount) if amount is not None else None,
        pattern=pattern,
    )


def _build_edges(
    rels: List[Relationship], node_map: Dict[str, GraphNode]
) -> List[GraphEdge]:
    edges: List[GraphEdge] = []
    for rel in rels:
        start_props = dict(rel.start_node)
        end_props = dict(rel.end_node)
        source_id = (
            start_props.get("txId")
            or start_props.get("tx_id")
            or start_props.get("account_id")
            or start_props.get("accountId")
            or str(rel.start_node.id)
        )
        target_id = (
            end_props.get("txId")
            or end_props.get("tx_id")
            or end_props.get("account_id")
            or end_props.get("accountId")
            or str(rel.end_node.id)
        )
        source_node = node_map.get(str(source_id))
        target_node = node_map.get(str(target_id))
        max_score = max(
            source_node.risk_score if source_node else 0.0,
            target_node.risk_score if target_node else 0.0,
        )
        is_suspicious = max_score >= 0.85 or (
            (source_node and source_node.aml_label == "fraud")
            or (target_node and target_node.aml_label == "fraud")
        )
        edges.append(
            GraphEdge(
                source=str(source_id),
                target=str(target_id),
                is_suspicious=is_suspicious,
                pattern=pattern_from_score(max_score) if is_suspicious else None,
            )
        )
    return edges


def _trim_graph(nodes: List[GraphNode], edges: List[GraphEdge], limit: int = 300) -> GraphResponse:
    """Trim graph to limit, prioritizing fraud/high-risk nodes."""
    if len(nodes) <= limit:
        return GraphResponse(nodes=nodes, edges=edges)
    # Sort: fraud nodes first, then by descending risk_score
    sorted_nodes = sorted(
        nodes,
        key=lambda n: (n.aml_label != "fraud", -n.risk_score),
    )
    trimmed_nodes = sorted_nodes[:limit]
    allowed = {node.txId for node in trimmed_nodes}
    trimmed_edges = [edge for edge in edges if edge.source in allowed and edge.target in allowed]
    return GraphResponse(nodes=trimmed_nodes, edges=trimmed_edges)


def _fetch_focus_graph(driver, tx_id: str, depth: int) -> GraphResponse:
    safe_depth = max(1, min(int(depth), 5))
    # Limit paths BEFORE unwinding to avoid materializing the entire traversal
    query = f"""
    MATCH (t:Transaction)
    WHERE t.txId = $txId OR t.tx_id = $txId
    OPTIONAL MATCH path_out=(t)-[:TRANSFERRED_TO|SENT_TO*1..{safe_depth}]->(n1:Transaction)
    OPTIONAL MATCH path_in=(n2:Transaction)-[:TRANSFERRED_TO|SENT_TO*1..{safe_depth}]->(t)
    WITH t,
         collect(DISTINCT path_out) AS out_paths,
         collect(DISTINCT path_in) AS in_paths
    WITH t, out_paths + in_paths AS all_paths
    UNWIND all_paths AS p
    WITH p WHERE p IS NOT NULL
    WITH p LIMIT 500
    UNWIND relationships(p) AS rel
    WITH DISTINCT rel, startNode(rel) AS source, endNode(rel) AS target
    RETURN source, target, rel
    """
    with driver.session() as session:
        rows = list(session.run(query, txId=tx_id))

    if not rows:
        with driver.session() as session:
            row = session.run(
                """
                MATCH (t:Transaction)
                WHERE t.txId = $txId OR t.tx_id = $txId
                RETURN t
                LIMIT 1
                """,
                txId=tx_id,
            ).single()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        node = _node_to_graph_node(row["t"])
        return GraphResponse(nodes=[node], edges=[])

    nodes: Dict[str, GraphNode] = {}
    rels: List[Relationship] = []
    for record in rows:
        source = record["source"]
        target = record["target"]
        rels.append(record["rel"])
        source_node = _node_to_graph_node(source)
        target_node = _node_to_graph_node(target)
        nodes[source_node.txId] = source_node
        nodes[target_node.txId] = target_node

    edges = _build_edges(rels, nodes)
    return _trim_graph(list(nodes.values()), edges)


def _fetch_cluster_graph(driver, cluster_id: str) -> GraphResponse | None:
    # Limit paths before unwinding
    query = """
    MATCH path=(src:Transaction)-[r:TRANSFERRED_TO|SENT_TO*1..5]->(tgt:Transaction)
    WHERE ALL(rel IN relationships(path) WHERE rel.cluster_id = $cluster_id)
    WITH path LIMIT 400
    UNWIND relationships(path) AS rel
    WITH DISTINCT rel, startNode(rel) AS source, endNode(rel) AS target
    RETURN source, target, rel
    """
    with driver.session() as session:
        rows = list(session.run(query, cluster_id=cluster_id))

    if not rows:
        return None

    nodes: Dict[str, GraphNode] = {}
    rels: List[Relationship] = []
    for record in rows:
        source = record["source"]
        target = record["target"]
        rels.append(record["rel"])
        source_node = _node_to_graph_node(source)
        target_node = _node_to_graph_node(target)
        nodes[source_node.txId] = source_node
        nodes[target_node.txId] = target_node

    edges = _build_edges(rels, nodes)
    return _trim_graph(list(nodes.values()), edges)


@router.get("/stats", response_model=GraphStats, dependencies=[Depends(verify_api_key)])
@audit_log(action_type="VIEW_GRAPH_STATS")
async def get_stats(
    request: Request,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> GraphStats:
    driver = _get_driver(request)

    def _query_stats():
        with driver.session() as session:
            stats_row = session.run(
                """
                MATCH (t:Transaction)
                RETURN
                  count(t) AS total_nodes,
                  sum(CASE
                        WHEN t.aml_label = 'fraud'
                          OR t.aml_label = 1
                          OR t.aml_label = true
                          OR coalesce(t.risk_score, 0) >= 0.85
                        THEN 1 ELSE 0 END) AS fraud_nodes,
                  sum(CASE
                        WHEN t.aml_label = 'legit'
                          OR t.aml_label = 0
                          OR t.aml_label = false
                        THEN 1 ELSE 0 END) AS legit_nodes
                """
            ).single()

            edge_row = session.run(
                """
                MATCH ()-[r]->()
                RETURN count(r) AS total_edges
                """
            ).single()

        return stats_row, edge_row

    loop = asyncio.get_running_loop()
    stats_row, edge_row = await loop.run_in_executor(_neo4j_pool, _query_stats)

    total_nodes = int(stats_row["total_nodes"] or 0)
    fraud_nodes = int(stats_row["fraud_nodes"] or 0)
    legit_nodes = int(stats_row["legit_nodes"] or 0)
    unknown_nodes = max(total_nodes - fraud_nodes - legit_nodes, 0)
    total_edges = int(edge_row["total_edges"] or 0)

    return GraphStats(
        total_nodes=total_nodes,
        fraud_nodes=fraud_nodes,
        legit_nodes=legit_nodes,
        unknown_nodes=unknown_nodes,
        total_edges=total_edges,
    )


@router.get("/focus", response_model=GraphResponse, dependencies=[Depends(verify_api_key)])
@audit_log(action_type="VIEW_FRAUD_CLUSTER")
async def get_focus_subgraph(
    request: Request,
    txId: str = Query(..., description="Transaction ID to focus on"),
    depth: int = Query(2, ge=1, le=5, description="Traversal depth (1-5)"),
    current_user: AuthUser = Depends(verify_investigator_access),
) -> GraphResponse:
    driver = _get_driver(request)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_neo4j_pool, _fetch_focus_graph, driver, txId, depth)


@router.get(
    "/focus/{cluster_id}",
    response_model=GraphResponse,
    dependencies=[Depends(verify_api_key)],
)
@audit_log(action_type="VIEW_FRAUD_CLUSTER")
async def get_focus_cluster(
    request: Request,
    cluster_id: str,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> GraphResponse:
    driver = _get_driver(request)
    loop = asyncio.get_running_loop()
    cluster_graph = await loop.run_in_executor(
        _neo4j_pool, _fetch_cluster_graph, driver, cluster_id
    )
    if cluster_graph is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster_graph


@router.get("/fraud-clusters", response_model=GraphResponse, dependencies=[Depends(verify_api_key)])
@audit_log(action_type="VIEW_FRAUD_CLUSTERS")
async def get_fraud_clusters(
    request: Request,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> GraphResponse:
    driver = _get_driver(request)

    def _query_fraud_clusters():
        # Two-stage query: find seeds, then expand 1 hop out
        query = """
        MATCH (t:Transaction)
        WHERE coalesce(t.risk_score, 0) >= 0.85 OR t.aml_label = 'fraud' OR t.aml_label = 1
        WITH t ORDER BY t.risk_score DESC LIMIT 150
        OPTIONAL MATCH (t)-[r:TRANSFERRED_TO|SENT_TO]-(n:Transaction)
        RETURN t, r, n
        """
        nodes: Dict[str, GraphNode] = {}
        rels: List[Relationship] = []
        with driver.session() as session:
            for record in session.run(query):
                if record.get("t"):
                    node = _node_to_graph_node(record["t"])
                    nodes[node.txId] = node
                if record.get("n"):
                    node = _node_to_graph_node(record["n"])
                    nodes[node.txId] = node
                if record.get("r"):
                    rels.append(record["r"])

        edges = _build_edges(rels, nodes)
        return _trim_graph(list(nodes.values()), edges)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_neo4j_pool, _query_fraud_clusters)


@router.get("/evidence/{txId}", response_model=EvidencePackage, dependencies=[Depends(verify_api_key)])
@audit_log(action_type="VIEW_EVIDENCE")
async def get_evidence(
    request: Request,
    txId: str,
    current_user: AuthUser = Depends(verify_investigator_access),
) -> EvidencePackage:
    driver = _get_driver(request)

    def _query_evidence():
        chain_nodes = fetch_chain_nodes(driver, txId)
        if not chain_nodes:
            return None
        return build_evidence_package(chain_nodes, txId)

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(_neo4j_pool, _query_evidence)
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result
