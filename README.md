# FundTrace AI

## Project Status (as of 2026-05-05)

### Implemented in This Workspace

**Backend + Data Layer**
- FastAPI API with graph focus endpoint and websocket alert stream.
- Neo4j integration with focus subgraph query and alert ingestion.
- AML labeling on `Account` nodes using heuristics (`aml_label`).
- Model status ingestion endpoint for monitoring worker runs.

**ML Pipeline (MVP)**
- XGBoost-based risk scoring trained from Neo4j-derived features.
- Heuristic label fallback when ground-truth labels are missing.
- Continuous worker posts alerts to the live stream.

**Frontend + Visualization (MVP)**
- Live threat stream panel with clickable alerts.
- Fraud node highlighting using `aml_label`.
- Node hover tooltip showing account details.
- Focus/zoom behavior on selected cluster with reset.
- Model status panel (latest worker run).

### Known Gaps / Non-Production Areas
- Labels are heuristic; no ground-truth AML labels or investigator feedback loop yet.
- Single-node Neo4j; no enterprise clustering, sharding, or GDS background jobs.
- Monolithic backend; no separate ingestion/scoring/query services.
- No enterprise auth (SAML/OIDC), RBAC, audit logs, or PII masking.
- react-force-graph is MVP only; no WebGL clustering/summarization.

## Roadmap (Required for Production)

### 1) Data Ingestion & Integration (CBS Layer)
**Done**
- MVP ingestion from Neo4j with API-driven queries.

**To Implement**
- Change Data Capture (Debezium) from CBS RDBMS (Oracle/SQL Server).
- Kafka/Redpanda event streaming for transactions/KYC/account events.
- Stream processing (Flink/Kafka Streams) for enrichment + dedupe.
- Nightly reconciliation ETL (Airflow/PySpark).

### 2) Enterprise Graph Infrastructure
**Done**
- Single-node Neo4j integration for MVP.

**To Implement**
- Neo4j Enterprise Causal Cluster (core + read replicas).
- Graph partitioning/sharding + cold storage for dormant nodes.
- Neo4j GDS (Louvain/PageRank) background analytics.

### 3) ML Ops & AI Pipeline (Human-in-the-Loop)
**Done**
- XGBoost worker and heuristic AML labels.

**To Implement**
- Feature store (Feast/Hopsworks) with rolling features.
- Model registry + serving (MLflow + Triton/Seldon).
- Shadow mode deployment for model validation.
- Feedback loop from investigator actions to retraining.

### 4) Backend Microservices
**Done**
- FastAPI monolith with graph + stream endpoints.

**To Implement**
- Ingestion Service (Kafka -> Neo4j).
- Scoring Engine (features + inference + graph risk update).
- Query/API Service with rate limiting.
- Async worker queue (Celery + Redis) for heavy exports.

### 5) Security, Audit, & Compliance
**Done**
- API key auth for MVP.

**To Implement**
- SAML 2.0 / OIDC (Azure AD/Okta).
- RBAC by analyst tier.
- Immutable audit logs (WORM storage).
- PII encryption + dynamic masking.

### 6) Frontend & Visualization Engine
**Done**
- MVP graph UI with focus/zoom, tooltips, live alerts.

**To Implement**
- Custom WebGL rendering (Three.js/deck.gl).
- Graph summarization and super-node clustering.
- State management (Redux Toolkit/Zustand) for high-volume streams.

### 7) Infrastructure & DevOps
**Done**
- Local dev workflow.

**To Implement**
- Kubernetes deployment (EKS/AKS/GKE).
- Terraform IaC for infra provisioning.
- CI/CD pipeline with tests + SAST (SonarQube).
- APM/monitoring (Datadog or Prometheus + Grafana).

## Notes
- This README reflects the current MVP scope and the production-grade roadmap requested.
- For production readiness, each roadmap item should be tracked as a dedicated epic with clear success criteria and non-functional requirements.
