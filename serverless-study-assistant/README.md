# Serverless Chatbot with MLOps Pipeline
### An AI-Powered Study Assistant with Monitoring and Delivery Automation

[![CI Pipeline](https://github.com/dhanushs1904/serverless-study-assistant/actions/workflows/tests.yml/badge.svg)](https://github.com/dhanushs1904/serverless-study-assistant/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://www.python.org/)
[![AWS Serverless](https://img.shields.io/badge/AWS-Lambda%20%7C%20API%20Gateway%20%7C%20DynamoDB%20%7C%20S3%20%7C%20CloudWatch-FF9900.svg?logo=amazon-aws)](https://aws.amazon.com/)
[![Tests](https://img.shields.io/badge/pytest-27%20passed%20(100%25)-brightgreen.svg)](tests/)

---

## Academic Project Information

- **Institution:** Vellore Institute of Technology (VIT), Vellore
- **Project Title:** SERVERLESS CHATBOT WITH MLOps PIPELINE
- **Subtitle:** An AI-Powered Study Assistant with Monitoring and Delivery Automation
- **Student Name:** Dhanush S
- **Registration Number:** 23MIS0224
- **Course Name:** Agile Development Process and DevOps
- **Faculty Guide:** Prof. Arun Kumar
- **Academic Term:** Fall Semester 2026

---

## 1. Executive Summary

This project delivers an end-to-end cloud-native academic study assistant designed to assist university students in computer science, agile software methodologies, and DevOps engineering subjects.

The system bridges modern software development with the complete operational lifecycle (DevOps & MLOps):
1. **Full-Stack Application:** Responsive modern web frontend coupled with high-performance Python FastAPI backend.
2. **Dual-Mode AI Reasoning:** Groq API leveraging modern LLaMA-family foundation models (`llama-3.3-70b-versatile`) with automatic, deterministic rule-based fallback for high availability.
3. **5 AWS Cloud Integrations:**
   - **Amazon S3:** Benchmark evaluation dataset storage & versioned MLOps simulation report archiving.
   - **AWS Lambda:** Serverless ASGI event execution via Mangum adapter with scale-to-zero economics.
   - **Amazon API Gateway:** Managed HTTP API routing (`/api/chat`, `/api/health`, `/api/metrics`, `/api/model-version`, `/api/mlops/retrain-simulation`) with strict CORS.
   - **Amazon DynamoDB:** NoSQL cloud persistence using `StudyAssistantRecords` with Partition Key (`PK`) and Sort Key (`SK`) schema.
   - **Amazon CloudWatch:** Real-time log streams, invocation telemetry, latency alarms, and error rate tracking.
4. **Local Zero-Cost Mode:** Automatically falls back to local SQLite storage and local filesystem artifact storage when AWS credentials are not configured, requiring $0 to run and demonstrate.
5. **Continuous MLOps Retraining Simulation:** Automates benchmark dataset validation, precision/recall/F1 scoring, model version bumping (`v1.0.0` -> `v1.1.0`), and artifact delivery.
6. **Robust Quality Assurance:** 27 automated unit and integration tests executed via `pytest`, with GitHub Actions CI workflow.

---

## 2. System Architecture

### Local Development Architecture
```
Student Browser (HTML/CSS/JS)
      │
      ▼
FastAPI Application (Uvicorn :8000)
      ├── Groq API (LLaMA 3.3 70B) ──[Fallback on Error]──► Rule-Based Knowledge Engine
      ├── SQLite Database (data/study_assistant.db)
      ├── Local In-Memory & Process Metrics
      ├── Model-Version Registry
      └── MLOps Simulation (data/reports/)
```

### AWS Serverless Cloud Architecture
```
Student Browser (S3 Static Hosting / Local)
      │
      ▼
Amazon API Gateway (HTTP API v2)
      │
      ▼
AWS Lambda (Mangum ASGI Handler)
      ├── Groq API / Fallback Engine
      ├── Amazon DynamoDB (StudyAssistantRecords Table)
      ├── Amazon S3 (Artifacts & Benchmark Datasets)
      └── Amazon CloudWatch (Logs, Invocations, Alarms)
```

---

## 3. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Programming Language** | Python 3.10+ | Standard language for AI, MLOps, backend APIs, and AWS Lambda runtimes. |
| **API Framework** | FastAPI 0.162.0 | Async performance, Pydantic type validation, automatic Swagger OpenAPI docs. |
| **ASGI Server** | Uvicorn 0.54.0 | Lightweight, standard ASGI web server. |
| **Serverless Adapter** | Mangum 0.22.0 | Seamlessly transforms API Gateway events into ASGI HTTP requests for Lambda. |
| **Cloud Provider** | Amazon Web Services (AWS) | Real integration with S3, Lambda, API Gateway, DynamoDB, and CloudWatch. |
| **Local Database** | SQLite 3 | Embedded, zero-configuration local database for student demo. |
| **Cloud Database** | Amazon DynamoDB | High-throughput serverless NoSQL database with flexible item schema. |
| **AI Provider** | Groq API (LLaMA 3.3 70B) | Low latency inference for academic tutoring. |
| **Fallback Engine** | Rule-Based Expert System | Deterministic response generator ensuring 100% uptime when external AI is offline. |
| **Testing** | pytest 9.2.0 & httpx | Automated unit, regression, mock, and API test execution. |
| **CI/CD** | GitHub Actions | Automated build, test, and lint execution on every push or pull request. |
| **Frontend** | HTML5, CSS3, Vanilla JS | Ultra-fast, framework-free responsive UI accessible anywhere. |

---

## 4. Local Quick Start Guide (Windows PowerShell)

### Step 1: Open PowerShell and Clone Repository
```powershell
git clone https://github.com/dhanushs1904/serverless-study-assistant.git
cd serverless-study-assistant
```

### Step 2: Create and Activate Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell blocks script execution, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

### Step 3: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(Optional: Open `.env` and paste your free Groq API key from https://console.groq.com/ if you wish to enable LLaMA AI mode. If left empty, the application will automatically run in Rule-Based Fallback mode).*

### Step 5: Start the Backend Server
```powershell
python -m uvicorn app.main:app --reload --port 8000
```
The FastAPI application is now running at:
- **API Server:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **Health Endpoint:** `http://127.0.0.1:8000/api/health`

### Step 6: Launch the Frontend
Open `frontend/index.html` in your web browser, or serve it via Python:
```powershell
python -m http.server 3000 --directory frontend
```
Navigate to `http://127.0.0.1:3000` in Google Chrome or Microsoft Edge.

---

## 5. Running Automated Tests

Run the complete test suite with verbose reporting:
```powershell
pytest -v tests/
```
Output:
```
============================= test session starts ==============================
collected 27 items
tests/test_api.py::test_root_endpoint PASSED                            [  3%]
tests/test_api.py::test_health_endpoint PASSED                          [  7%]
tests/test_api.py::test_metrics_endpoint PASSED                         [ 11%]
tests/test_api.py::test_metrics_counter_increment PASSED                [ 14%]
tests/test_api.py::test_model_version_endpoint PASSED                   [ 18%]
tests/test_api.py::test_chat_empty_message_validation PASSED           [ 22%]
tests/test_api.py::test_chat_whitespace_only_validation PASSED         [ 25%]
tests/test_api.py::test_chat_missing_message_field PASSED               [ 29%]
tests/test_api.py::test_chat_message_too_long_validation PASSED         [ 33%]
tests/test_aws_services.py::test_s3_upload_mock PASSED                  [ 37%]
tests/test_aws_services.py::test_dynamodb_insert_mock PASSED            [ 40%]
tests/test_aws_services.py::test_lambda_handler_api_gateway_health_event PASSED [ 44%]
tests/test_aws_services.py::test_lambda_handler_api_gateway_chat_event PASSED   [ 48%]
tests/test_chat.py::test_chat_fallback_scrum_topic PASSED               [ 51%]
tests/test_chat.py::test_chat_fallback_devops_topic PASSED              [ 55%]
tests/test_chat.py::test_chat_fallback_deadlock_topic PASSED            [ 59%]
tests/test_chat.py::test_chat_fallback_general_query PASSED             [ 62%]
tests/test_chat.py::test_mocked_groq_ai_success PASSED                  [ 66%]
tests/test_chat.py::test_mocked_groq_ai_exception_routes_to_fallback PASSED [ 70%]
tests/test_database.py::test_sqlite_table_initialization PASSED         [ 74%]
tests/test_database.py::test_sqlite_insert_and_retrieve_conversation PASSED [ 77%]
tests/test_database.py::test_sqlite_model_version_update PASSED        [ 81%]
tests/test_database.py::test_sqlite_retrain_run_record PASSED          [ 85%]
tests/test_mlops.py::test_evaluation_dataset_structure PASSED          [ 88%]
tests/test_mlops.py::test_evaluate_single_sample PASSED                [ 92%]
tests/test_mlops.py::test_mlops_run_simulation PASSED                   [ 96%]
tests/test_mlops.py::test_mlops_api_endpoint PASSED                    [100%]
======================== 27 passed in 0.23s =========================
```

---

## 6. Running the MLOps Simulation via CLI

Execute the educational MLOps retraining simulation:
```powershell
python scripts/simulate_retraining.py
```
This script:
1. Ingests `data/evaluation_dataset.json` (12 curated academic benchmark samples).
2. Runs evaluation against expected domain keywords.
3. Computes Precision, Recall, and F1-Scores.
4. Advances model version record (e.g. `v1.0.0-baseline` -> `v1.1.0-retrained`).
5. Generates Markdown and JSON reports in `data/reports/`.
6. Logs run metadata to SQLite and Amazon DynamoDB.

Export the latest system audit report:
```powershell
python scripts/export_report.py
```

---

## 7. API Specification

| Method | Endpoint | Description | Request Body | Response Codes |
|---|---|---|---|---|
| `GET` | `/` | Root verification & project metadata | None | `200` |
| `GET` | `/api/health` | System health & cloud configuration | None | `200` |
| `POST` | `/api/chat` | Chatbot inference endpoint | `{"message": str, "conversation_id": str}` | `200`, `422`, `500` |
| `GET` | `/api/metrics` | Operational counters & latencies | None | `200` |
| `GET` | `/api/model-version` | Active model version & lineage | None | `200` |
| `POST` | `/api/mlops/retrain-simulation` | Trigger MLOps evaluation run | `{"trigger_reason": str}` | `200`, `500` |
| `GET` | `/api/conversations` | Inspect stored conversation records | Query param `limit` (int) | `200` |
| `GET` | `/api/mlops/runs` | Inspect MLOps simulation history | Query param `limit` (int) | `200` |

---

## 8. Five AWS Services Implementation Details

1. **Amazon S3:** Implemented in `app/services/s3_service.py`. Enforces `AES256` server-side encryption and private bucket permissions. Archives `data/evaluation_dataset.json` and generated MLOps reports.
2. **AWS Lambda:** Implemented in `app/lambda_handler.py`. Uses `Mangum(app, lifespan="off")` to transform API Gateway events directly into ASGI HTTP requests.
3. **Amazon API Gateway:** Exposes HTTP API v2 routes mapped directly to the Lambda function. Full CORS enabled for frontend integration.
4. **Amazon DynamoDB:** Implemented in `app/database/dynamodb_store.py`. Persists records into table `StudyAssistantRecords` with Partition Key `PK` and Sort Key `SK` across 4 categories (`CONVERSATION`, `MODEL_VERSION`, `RETRAIN_RUN`, `METRIC`).
5. **Amazon CloudWatch:** Configured in `app/services/metrics_service.py` and `app/main.py`. Emits structured JSON logs and monitors Lambda invocations, error counts, and latency percentiles.

See `ARCHITECTURE.md` for full architectural diagrams and `AWS_DEPLOYMENT.md` for step-by-step cloud deployment instructions.

---

## 9. Academic Coursework Verification

Built strictly adhering to the requirements for:
- **Course:** Agile Development Process and DevOps
- **Faculty Guide:** Prof. Arun Kumar
- **Student:** Dhanush S (23MIS0224)
- **Institution:** Vellore Institute of Technology (VIT)
