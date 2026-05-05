#!/usr/bin/env python3
"""Generate synthetic AML data and push it to Neo4j."""

from __future__ import annotations

import argparse
import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from dotenv import load_dotenv
from neo4j import GraphDatabase


@dataclass(frozen=True)
class Account:
    account_id: str
    account_type: str
    kyc_risk_baseline: float
    total_volume: float


@dataclass(frozen=True)
class Transaction:
    tx_id: str
    source_id: str
    target_id: str
    amount: float
    timestamp: str
    is_structuring: bool


def _iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat()


def _rand_account_type(rng: random.Random) -> str:
    roll = rng.random()
    if roll < 0.78:
        return "Retail"
    if roll < 0.95:
        return "Corporate"
    return "Shell"


def _generate_accounts(rng: random.Random, count: int) -> dict[str, Account]:
    accounts: dict[str, Account] = {}
    for idx in range(count):
        account_id = f"ACC-{idx:04d}"
        account_type = _rand_account_type(rng)
        accounts[account_id] = Account(
            account_id=account_id,
            account_type=account_type,
            kyc_risk_baseline=round(rng.uniform(0.02, 0.95), 4),
            total_volume=0.0,
        )
    return accounts


def _generate_normal_transactions(
    rng: random.Random,
    accounts: list[str],
    count: int,
    start: datetime,
) -> list[Transaction]:
    txs: list[Transaction] = []
    for idx in range(count):
        source_id, target_id = rng.sample(accounts, 2)
        amount = round(rng.uniform(2000.0, 180000.0), 2)
        ts = start + timedelta(minutes=rng.randint(5, 60 * 24 * 10))
        txs.append(
            Transaction(
                tx_id=f"TX-NORMAL-{idx:05d}",
                source_id=source_id,
                target_id=target_id,
                amount=amount,
                timestamp=_iso(ts),
                is_structuring=False,
            )
        )
    return txs


def _generate_smurfing_pattern(
    rng: random.Random,
    accounts: dict[str, Account],
    start: datetime,
) -> tuple[list[Transaction], str]:
    shell_ids = [acc.account_id for acc in accounts.values() if acc.account_type == "Shell"]
    if not shell_ids:
        shell_ids = [rng.choice(list(accounts))]
    collector_id = rng.choice(shell_ids)

    source_ids = [acc.account_id for acc in accounts.values() if acc.account_id != collector_id]
    rng.shuffle(source_ids)
    source_ids = source_ids[:14]

    txs: list[Transaction] = []
    for idx, source_id in enumerate(source_ids):
        ts = start + timedelta(hours=rng.randint(1, 72))
        txs.append(
            Transaction(
                tx_id=f"TX-SMURF-{idx:03d}",
                source_id=source_id,
                target_id=collector_id,
                amount=195000.0,
                timestamp=_iso(ts),
                is_structuring=True,
            )
        )
    return txs, collector_id


def _generate_slow_burn_layering(
    rng: random.Random,
    accounts: dict[str, Account],
    start: datetime,
) -> list[Transaction]:
    chain_ids = rng.sample(list(accounts), 4)
    txs: list[Transaction] = []
    amount = round(rng.uniform(350000.0, 900000.0), 2)
    for hop in range(3):
        ts = start + timedelta(hours=48 * (hop + 1))
        txs.append(
            Transaction(
                tx_id=f"TX-LAYER-{hop:03d}",
                source_id=chain_ids[hop],
                target_id=chain_ids[hop + 1],
                amount=amount,
                timestamp=_iso(ts),
                is_structuring=False,
            )
        )
    return txs


def _update_total_volume(accounts: dict[str, Account], txs: Iterable[Transaction]) -> dict[str, Account]:
    totals: dict[str, float] = {acc_id: 0.0 for acc_id in accounts}
    for tx in txs:
        totals[tx.source_id] += tx.amount
        totals[tx.target_id] += tx.amount
    return {
        acc_id: Account(
            account_id=acc.account_id,
            account_type=acc.account_type,
            kyc_risk_baseline=acc.kyc_risk_baseline,
            total_volume=round(totals[acc_id], 2),
        )
        for acc_id, acc in accounts.items()
    }


def _connect_driver() -> object:
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not uri or not user or not password:
        raise RuntimeError("Missing Neo4j configuration in .env")
    return GraphDatabase.driver(uri, auth=(user, password))


def _reset_graph(session) -> None:
    session.run("MATCH (n) DETACH DELETE n")


def _ensure_constraints(session) -> None:
    session.run(
        "CREATE CONSTRAINT account_id_unique IF NOT EXISTS "
        "FOR (a:Account) REQUIRE a.account_id IS UNIQUE"
    )


def _ingest_accounts(session, accounts: Iterable[Account]) -> None:
    session.run(
        "UNWIND $rows AS row "
        "MERGE (a:Account {account_id: row.account_id}) "
        "SET a.account_type = row.account_type, "
        "    a.kyc_risk_baseline = row.kyc_risk_baseline, "
        "    a.total_volume = row.total_volume",
        rows=[acc.__dict__ for acc in accounts],
    )


def _ingest_transactions(session, txs: Iterable[Transaction]) -> None:
    session.run(
        "UNWIND $rows AS row "
        "MATCH (s:Account {account_id: row.source_id}) "
        "MATCH (t:Account {account_id: row.target_id}) "
        "CREATE (s)-[:TRANSACTION {"
        "  tx_id: row.tx_id, "
        "  source_id: row.source_id, "
        "  target_id: row.target_id, "
        "  amount: row.amount, "
        "  timestamp: row.timestamp, "
        "  is_structuring: row.is_structuring"
        "}]->(t)",
        rows=[tx.__dict__ for tx in txs],
    )


def build_dataset(seed: int, account_count: int, normal_tx_count: int) -> tuple[list[Account], list[Transaction]]:
    rng = random.Random(seed)
    base_time = datetime.now(timezone.utc) - timedelta(days=10)

    accounts = _generate_accounts(rng, account_count)
    normal_txs = _generate_normal_transactions(rng, list(accounts), normal_tx_count, base_time)
    smurf_txs, _collector_id = _generate_smurfing_pattern(rng, accounts, base_time + timedelta(days=2))
    layer_txs = _generate_slow_burn_layering(rng, accounts, base_time + timedelta(days=3))

    all_txs = normal_txs + smurf_txs + layer_txs
    accounts = _update_total_volume(accounts, all_txs)

    return list(accounts.values()), all_txs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AML synthetic data and load into Neo4j")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--accounts", type=int, default=160)
    parser.add_argument("--transactions", type=int, default=520)
    parser.add_argument("--reset", action="store_true", help="Delete all nodes and relationships first")
    args = parser.parse_args()

    accounts, txs = build_dataset(args.seed, args.accounts, args.transactions)

    driver = _connect_driver()
    try:
        with driver.session() as session:
            if args.reset:
                _reset_graph(session)
            _ensure_constraints(session)
            _ingest_accounts(session, accounts)
            _ingest_transactions(session, txs)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
