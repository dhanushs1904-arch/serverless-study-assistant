# Project Test Report & Verification Evidence

**Course:** Agile Development Process and DevOps  
**Faculty Guide:** Prof. Arun Kumar  
**Student Name:** Dhanush S  
**Registration Number:** 23MIS0224  
**Institution:** Vellore Institute of Technology (VIT), Vellore  
**Test Framework:** pytest 9.2.0, FastAPI TestClient, unittest.mock  
**Test Execution Timestamp:** Fall Semester 2026  

---

## 1. Test Summary

| Total Test Cases | Passed | Failed | Skipped | Pass Rate | Execution Time |
|---|---|---|---|---|---|
| **27** | **27** | **0** | **0** | **100.0%** | **0.23 seconds** |

---

## 2. Test Execution Breakdown by Category

### Category A: Core API & Schema Validation (`tests/test_api.py`)

| Test ID | Test Name | Purpose / Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **API-01** | `test_root_endpoint` | Verify root metadata, student information, and cloud services list. | HTTP 200, contains student details and AWS services. | HTTP 200, matching metadata returned. | **PASS** |
| **API-02** | `test_health_endpoint` | Health check retrieval and system state validation. | HTTP 200 with status `"healthy"` and environment info. | HTTP 200, status `"healthy"`. | **PASS** |
| **API-03** | `test_metrics_endpoint` | Initial metrics counter and latency reporting. | HTTP 200, metrics keys present and non-negative. | HTTP 200, snapshot returned. | **PASS** |
| **API-04** | `test_metrics_counter_increment` | Verify counter increment following a valid `/api/chat` request. | `total_requests` and `successful_requests` increment by >= 1. | Counters incremented accurately. | **PASS** |
| **API-05** | `test_model_version_endpoint` | Active model version, provider, and lineage tracking. | HTTP 200, `record_version` and `application_version` present. | HTTP 200, returns active version. | **PASS** |
| **API-06** | `test_chat_empty_message_validation` | Validation of empty string `""` in chat request payload. | HTTP 422 Unprocessable Entity with error message. | HTTP 422 returned. | **PASS** |
| **API-07** | `test_chat_whitespace_only_validation` | Validation of whitespace-only `"   \n\t  "` message. | HTTP 422 Unprocessable Entity. | HTTP 422 returned. | **PASS** |
| **API-08** | `test_chat_missing_message_field` | Validation of JSON payload missing required `"message"` key. | HTTP 422 Unprocessable Entity. | HTTP 422 returned. | **PASS** |
| **API-09** | `test_chat_message_too_long_validation` | Validation of message exceeding maximum length (> 2000 chars). | HTTP 422 Unprocessable Entity. | HTTP 422 returned. | **PASS** |

---

### Category B: Chat Reasoning & AI Fallback Engine (`tests/test_chat.py`)

| Test ID | Test Name | Purpose / Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **CHAT-01** | `test_chat_fallback_scrum_topic` | Evaluate keyword routing for Agile Scrum questions. | Returns structured definition with roles, artifacts, and tips. | Concept matched and returned accurately. | **PASS** |
| **CHAT-02** | `test_chat_fallback_devops_topic` | Evaluate keyword routing for DevOps & CI/CD queries. | Returns CI/CD concepts and automated testing details. | Concept matched accurately. | **PASS** |
| **CHAT-03** | `test_chat_fallback_deadlock_topic` | Evaluate OS Coffman conditions matching. | Returns Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait. | All 4 Coffman conditions explained. | **PASS** |
| **CHAT-04** | `test_chat_fallback_general_query` | Evaluate general academic inquiry fallback. | Returns structured 4-step academic study framework. | Structured framework returned. | **PASS** |
| **CHAT-05** | `test_mocked_groq_ai_success` | Mock external Groq API LLaMA 3.3 70B response. | `response_mode` is `"ai"`, reply contains AI content. | AI response properly formatted. | **PASS** |
| **CHAT-06** | `test_mocked_groq_ai_exception_routes_to_fallback` | Simulate Groq API 429 Rate Limit error. | Automatically switches to fallback mode with notice. | Seamless fallback to deterministic engine. | **PASS** |

---

### Category C: Local Persistence & Storage (`tests/test_database.py`)

| Test ID | Test Name | Purpose / Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **DB-01** | `test_sqlite_table_initialization` | Verify automatic creation of SQLite tables on startup. | Database file created, initial model version seeded. | Tables created, baseline version seeded. | **PASS** |
| **DB-02** | `test_sqlite_insert_and_retrieve_conversation` | Insert conversation and retrieve via parameterized query. | Record stored with matching ID, message, and duration. | Correct record retrieved. | **PASS** |
| **DB-03** | `test_sqlite_model_version_update` | Record and retrieve new model version increment. | Latest version returns newly updated version string. | Version updated accurately. | **PASS** |
| **DB-04** | `test_sqlite_retrain_run_record` | Record MLOps retraining simulation execution. | Retrain run stored with parsed JSON metrics. | Run retrieved with valid metrics. | **PASS** |

---

### Category D: MLOps Simulation & Benchmarking (`tests/test_mlops.py`)

| Test ID | Test Name | Purpose / Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **MLOPS-01**| `test_evaluation_dataset_structure` | Verify `data/evaluation_dataset.json` contains valid benchmark schema. | Contains `dataset_metadata`, >= 10 samples, expected keywords. | 12 valid academic samples loaded. | **PASS** |
| **MLOPS-02**| `test_evaluate_single_sample` | Test sample keyword matching and F1 computation. | `keyword_recall` and `f1_score` calculated correctly. | Valid recall and precision scores. | **PASS** |
| **MLOPS-03**| `test_mlops_run_simulation` | End-to-end retraining simulation pipeline execution. | Generates run ID, evaluation reports, and bumps version. | Reports written to disk, version bumped. | **PASS** |
| **MLOPS-04**| `test_mlops_api_endpoint` | Test `POST /api/mlops/retrain-simulation` endpoint. | HTTP 200, response matches `RetrainSimulationResponse` schema. | HTTP 200 with complete metrics. | **PASS** |

---

### Category E: AWS Services Integration with Mocks (`tests/test_aws_services.py`)

| Test ID | Test Name | Purpose / Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **AWS-01** | `test_s3_upload_mock` | Verify Amazon S3 artifact upload using mocked boto3 client. | `upload_file` invoked with correct bucket, key, and SSE AES256. | S3 client invoked with correct arguments. | **PASS** |
| **AWS-02** | `test_dynamodb_insert_mock` | Verify Amazon DynamoDB insertion into `StudyAssistantRecords`. | `put_item` invoked with Partition Key `PK` and Sort Key `SK`. | Item matches schema specifications. | **PASS** |
| **AWS-03** | `test_lambda_handler_api_gateway_health_event` | Dispatch synthetic API Gateway v2 HTTP event for `GET /api/health`. | Lambda handler returns HTTP 200 with health JSON body. | Mangum adapter processed event successfully. | **PASS** |
| **AWS-04** | `test_lambda_handler_api_gateway_chat_event` | Dispatch synthetic API Gateway v2 event for `POST /api/chat`. | Lambda handler returns HTTP 200 with chat reply JSON body. | Request successfully processed and returned. | **PASS** |

---

## 3. Command Line Execution Evidence

Executed in project root:
```bash
$ pytest -v /app/applet/serverless-study-assistant/tests
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.2.0, pluggy-1.7.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /app/applet
plugins: anyio-4.15.1
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

## 4. Known Limitations & Verification Notes

1. **Simulated Model Training:** The MLOps retraining simulation executes automated benchmark evaluation, keyword scoring, F1 calculation, report generation, and version bumping. It does not train new neural network weights on GPU clusters, which is intentionally designed to avoid excessive cloud compute costs during academic evaluation.
2. **Local vs Cloud Durability:** Process-local in-memory metrics reset if the local server process restarts; however, on AWS Lambda, Amazon CloudWatch provides durable metric storage and historical time-series analytics.
3. **Mock Isolation:** Cloud service tests use `unittest.mock` to guarantee that automated testing is fast (0.23s), reliable, and incurs zero AWS infrastructure expenses.
