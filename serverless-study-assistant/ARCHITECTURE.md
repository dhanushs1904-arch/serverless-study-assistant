# System Architecture & Technical Design Document

**Project Title:** Serverless Chatbot with MLOps Pipeline  
**Student:** Dhanush S (Registration Number: 23MIS0224)  
**Institution:** Vellore Institute of Technology (VIT)  
**Course:** Agile Development Process and DevOps  
**Faculty Guide:** Prof. Arun Kumar  

---

## 1. Architectural Overview

The **Serverless Study Assistant** is engineered around a hybrid, decoupled architecture that supports:
1. **Local Friction-Free Mode:** Runs completely on a developer workstation using SQLite, Python Uvicorn, and local filesystem reports without requiring AWS credentials or cloud billing.
2. **AWS Cloud-Native Serverless Mode:** Leverages five managed AWS services (S3, Lambda, API Gateway, DynamoDB, and CloudWatch) to provide a resilient, auto-scaling, scale-to-zero production environment.

The system incorporates dual-engine inference (Groq/LLaMA + Rule-Based Fallback) and an automated educational MLOps continuous delivery pipeline.

---

## 2. Mermaid Architecture Diagrams

### 2.1 Complete End-to-End Cloud & Local Architecture

```mermaid
flowchart TD
    subgraph Client_Layer ["Client Layer (Presentation)"]
        UI["Student Web Interface\n(HTML5 / CSS3 / Vanilla JS)"]
    end

    subgraph API_and_Compute ["Ingress & Serverless Compute Layer"]
        APIGW["Amazon API Gateway\n(HTTP API v2 / REST)\nRoutes: /api/chat, /health, /metrics"]
        LAMBDA["AWS Lambda Function\n(Python 3.10 Runtime)\nMangum ASGI Adapter"]
        UVICORN["Local Uvicorn Server\n(Port 8000)"]
    end

    subgraph Backend_Core ["FastAPI Core Application Layer"]
        ROUTER["FastAPI Router\n(Pydantic Validation)"]
        CHAT_SVC["Chat Service Coordinator"]
        PROV["Model Provider\n(Groq LLaMA 3.3 70B)"]
        FALLBACK["Deterministic Academic\nFallback Engine"]
        METRICS_SVC["Observability &\nMetrics Service"]
        MLOPS_SVC["MLOps Pipeline &\nRetrain Simulator"]
        VERSION_SVC["Model Version Registry"]
    end

    subgraph Persistence_Layer ["Dual Persistence Layer"]
        SQLITE[("Local SQLite Database\nstudy_assistant.db\nLocal Mode")]
        DYNAMO[("Amazon DynamoDB\nTable: StudyAssistantRecords\nCloud Mode")]
        S3[("Amazon S3 Bucket\nArtifacts & Evaluation Datasets\nvit-study-assistant-artifacts")]
    end

    subgraph Monitoring_Layer ["Observability Layer"]
        CW_LOGS["Amazon CloudWatch Logs\n(/aws/lambda/study-assistant)"]
        CW_METRICS["Amazon CloudWatch Metrics\n(Invocations, Duration, Errors)"]
    end

    %% Interactions
    UI -->|HTTP Requests| APIGW
    UI -.->|Local Testing| UVICORN
    APIGW -->|Proxy Event| LAMBDA
    UVICORN --> ROUTER
    LAMBDA --> ROUTER

    ROUTER --> CHAT_SVC
    ROUTER --> METRICS_SVC
    ROUTER --> VERSION_SVC
    ROUTER --> MLOPS_SVC

    CHAT_SVC -->|Primary AI Query| PROV
    PROV -->|Fallback on RateLimit/Offline| FALLBACK
    CHAT_SVC -->|Local Save| SQLITE
    CHAT_SVC -->|Cloud Save| DYNAMO

    MLOPS_SVC -->|Read Benchmark| S3
    MLOPS_SVC -->|Save Local Report| SQLITE
    MLOPS_SVC -->|Upload Report Artifact| S3
    MLOPS_SVC -->|Log Run Record| DYNAMO

    LAMBDA -.->|Structured Stdout| CW_LOGS
    LAMBDA -.->|Execution Telemetry| CW_METRICS
```

---

### 2.2 Chat Request Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student (Browser)
    participant APIGW as Amazon API Gateway
    participant Lambda as AWS Lambda (Mangum)
    participant FastAPI as FastAPI Router
    participant ChatService as Chat Service
    participant ModelProv as Model Provider (Groq)
    participant Fallback as Fallback Engine
    participant Dynamo as Amazon DynamoDB
    participant CW as Amazon CloudWatch

    Student->>APIGW: POST /api/chat { "message": "Explain Scrum..." }
    APIGW->>Lambda: Dispatches Proxy Event
    Lambda->>FastAPI: Mangum adapts event to ASGI Scope
    FastAPI->>ChatService: Validates ChatRequest (Pydantic)
    
    alt GROQ_API_KEY Configured & Healthy
        ChatService->>ModelProv: Query Groq LLaMA 3.3 70B
        ModelProv-->>ChatService: Return AI Response Payload
    else API Key Missing, Rate Limited, or Provider Timeout
        ChatService->>Fallback: Trigger generate_fallback_response()
        Fallback-->>ChatService: Return Structured Domain Concept
    end

    par Telemetry & Persistence
        ChatService->>Dynamo: Insert Item (PK: CONVERSATION#id, SK: timestamp)
        ChatService->>CW: Emit Structured JSON Metrics Log
    end

    ChatService-->>FastAPI: Return ChatResponse Model
    FastAPI-->>Lambda: Return ASGI HTTP 200 Response
    Lambda-->>APIGW: Return API Gateway Payload
    APIGW-->>Student: HTTP 200 { reply, response_mode, duration_ms }
```

---

### 2.3 Educational MLOps Retraining Simulation Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Student / CI Pipeline
    participant API as POST /api/mlops/retrain-simulation
    participant MLOps as MLOps Simulation Service
    participant Dataset as Evaluation Benchmark (JSON)
    participant Evaluator as Domain Keyword Evaluator
    participant VersionReg as Model Version Service
    participant S3 as Amazon S3
    participant Dynamo as Amazon DynamoDB

    Dev->>API: Trigger Simulation Request
    API->>MLOps: Execute run_simulation()
    MLOps->>Dataset: Ingest 12 Benchmark Question Samples
    loop For Each Sample
        MLOps->>Evaluator: Generate Concept & Match Keywords
        Evaluator-->>MLOps: Return Precision, Recall, and F1-Score
    end
    MLOps->>MLOps: Compute Aggregate Accuracy & F1
    MLOps->>VersionReg: Advance Version (v1.0.0 -> v1.1.0-retrained)
    MLOps->>MLOps: Generate JSON and Markdown Audit Reports
    
    par Cloud Artifact Delivery
        MLOps->>S3: Upload Report to s3://bucket/mlops-reports/run-id/
        MLOps->>Dynamo: Insert Record (PK: RETRAIN_RUN, SK: run_id)
    end

    MLOps-->>API: Return RetrainSimulationResponse
    API-->>Dev: HTTP 200 with Accuracy, F1, and Lineage
```

---

## 3. Deep Dive: The Five AWS Services

### Service 1: Amazon Simple Storage Service (Amazon S3)
- **Role:** Immutable artifact repository and model benchmark evaluation dataset archive.
- **Bucket Configuration:** `vit-study-assistant-artifacts-23mis0224` (Region: `us-east-1`).
- **Security:** Private bucket by default with `BlockPublicAcls`, `BlockPublicPolicy`, and `ServerSideEncryption: AES256`.
- **Stored Objects:**
  - `datasets/evaluation_dataset.json`: Versioned ground-truth evaluation benchmark.
  - `mlops-reports/{run_id}/report.json`: Machine-readable evaluation metrics.
  - `mlops-reports/{run_id}/report.md`: Formatted academic evaluation summary.

### Service 2: AWS Lambda
- **Role:** Serverless compute runtime executing the FastAPI application.
- **Runtime:** Python 3.10 / Python 3.11 with 512 MB memory and 15-second timeout.
- **Execution Model:** Stateless container invocation adapted via `Mangum(app, lifespan="off")`.
- **Economics:** Scale-to-zero; zero charges incurred when the application is idle.

### Service 3: Amazon API Gateway
- **Role:** Managed API ingress providing secure HTTP endpoints to the frontend.
- **Type:** HTTP API v2 (optimized for low latency and serverless payloads).
- **Configured Routes:**
  - `GET /` -> Root metadata verification
  - `GET /api/health` -> System health & cloud configuration audit
  - `POST /api/chat` -> Student question submission and AI inference
  - `GET /api/metrics` -> Operational latency and success rates
  - `GET /api/model-version` -> Model lineage and version auditing
  - `POST /api/mlops/retrain-simulation` -> Educational MLOps pipeline trigger
- **CORS:** Configured for `*` or specific frontend origins with allowed methods `GET, POST, OPTIONS`.

### Service 4: Amazon DynamoDB
- **Role:** Managed NoSQL database for fast key-value and document persistence.
- **Table Name:** `StudyAssistantRecords`
- **Primary Key Design:**
  - **Partition Key (`PK`):** String (`CONVERSATION#{id}`, `MODEL_VERSION`, `RETRAIN_RUN`, `METRICS_SNAPSHOT`)
  - **Sort Key (`SK`):** String (`{timestamp}` or `{run_id}` or `{record_version}`)
- **Capacity Mode:** On-Demand (pay-per-request) with automated scaling.

### Service 5: Amazon CloudWatch
- **Role:** Centralized logging, operational monitoring, and alerting.
- **Components:**
  - **CloudWatch Logs:** Log Group `/aws/lambda/study-assistant-backend` aggregating Python structured logs.
  - **CloudWatch Metrics:** Real-time tracking of `Invocations`, `Duration`, `Errors`, and custom Embedded Metric Format events.
  - **CloudWatch Alarms:** Configured alarm `StudyAssistant-HighErrorRate` triggering when error rate exceeds 5% over 5 minutes.

---

## 4. Local vs. Cloud Comparison

| Characteristic | Local Development Mode | AWS Cloud-Native Mode |
|---|---|---|
| **Host Environment** | Developer PC (Windows / Linux) | AWS Lambda + API Gateway |
| **Persistence** | Embedded SQLite (`study_assistant.db`) | Amazon DynamoDB (`StudyAssistantRecords`) |
| **Artifact Storage** | Local directory (`data/reports/`) | Amazon S3 (`vit-study-assistant-artifacts`) |
| **Observability** | Console stdout & in-memory counters | Amazon CloudWatch Logs & Metrics |
| **Cost** | **$0.00 (Zero)** | **Free Tier Eligible (~$0.00)** |
| **Setup Time** | < 2 minutes via PowerShell | ~5 minutes via AWS CLI / SAM |
