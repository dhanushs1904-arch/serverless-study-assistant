import { EvalSample, DynamoRecord, CloudWatchLog } from '../types';

export const INITIAL_EVAL_DATASET: EvalSample[] = [
  {
    id: "eval-001",
    category: "Agile",
    question: "What is the difference between a Scrum Sprint Backlog and a Product Backlog?",
    expected_keywords: ["product backlog", "sprint backlog", "prioritized", "sprint goal", "product owner"],
    difficulty: "Easy",
    reference_concept: "The Product Backlog is an ordered, evolving list of everything needed in the product managed by the Product Owner. The Sprint Backlog is a subset chosen by the development team for a specific sprint to achieve the Sprint Goal."
  },
  {
    id: "eval-002",
    category: "Agile",
    question: "Explain the role and value of a Daily Standup in Agile methodologies.",
    expected_keywords: ["daily standup", "scrum", "impediments", "yesterday", "today", "15 minutes"],
    difficulty: "Easy",
    reference_concept: "A time-boxed 15-minute daily ceremony where team members sync on what they did yesterday, what they will do today, and any blockers or impediments."
  },
  {
    id: "eval-003",
    category: "DevOps",
    question: "What is the purpose of Continuous Integration (CI) and Continuous Delivery (CD)?",
    expected_keywords: ["continuous integration", "continuous delivery", "automated testing", "pipeline", "deployment"],
    difficulty: "Medium",
    reference_concept: "CI automates merging code and running automated test suites to detect integration bugs early. CD automates packaging and deploying software safely to staging or production environments."
  },
  {
    id: "eval-004",
    category: "DevOps",
    question: "How does serverless computing like AWS Lambda benefit DevOps deployment?",
    expected_keywords: ["serverless", "aws lambda", "scaling", "no server management", "pay-per-use", "event-driven"],
    difficulty: "Medium",
    reference_concept: "Serverless eliminates the operational overhead of provisioning and patching servers, scales automatically with incoming event traffic, and charges only for compute execution duration."
  },
  {
    id: "eval-005",
    category: "MLOps",
    question: "What is model drift and how does an MLOps pipeline address it?",
    expected_keywords: ["model drift", "concept drift", "data drift", "retraining", "monitoring", "performance"],
    difficulty: "Hard",
    reference_concept: "Model drift occurs when real-world data patterns diverge from training data, degrading inference quality. MLOps pipelines continuously monitor metrics, detect drift thresholds, and trigger automated retraining."
  },
  {
    id: "eval-006",
    category: "MLOps",
    question: "Why is model versioning critical in production AI systems?",
    expected_keywords: ["versioning", "reproducibility", "rollback", "auditability", "metadata"],
    difficulty: "Medium",
    reference_concept: "Model versioning allows tracking code, hyperparameter, and dataset lineage, enabling rollback to known good checkpoints and maintaining compliance audits."
  },
  {
    id: "eval-007",
    category: "Operating Systems",
    question: "Explain the four necessary conditions for deadlock in operating systems.",
    expected_keywords: ["deadlock", "mutual exclusion", "hold and wait", "no preemption", "circular wait"],
    difficulty: "Medium",
    reference_concept: "Coffman conditions: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait must simultaneously hold for a deadlock to occur."
  },
  {
    id: "eval-008",
    category: "Operating Systems",
    question: "What is virtual memory and what is the function of paging?",
    expected_keywords: ["virtual memory", "paging", "page table", "mmu", "address space", "page fault"],
    difficulty: "Medium",
    reference_concept: "Virtual memory gives processes the illusion of contiguous physical memory. Paging maps fixed-size virtual pages to physical frames using page tables."
  },
  {
    id: "eval-009",
    category: "Computer Networks",
    question: "Explain the TCP three-way handshake connection establishment process.",
    expected_keywords: ["tcp", "three-way handshake", "syn", "syn-ack", "ack", "sequence number"],
    difficulty: "Easy",
    reference_concept: "Client sends SYN, server responds with SYN-ACK, and client acknowledges with ACK to establish a reliable full-duplex TCP socket connection."
  },
  {
    id: "eval-010",
    category: "Computer Networks",
    question: "How does DNS resolution resolve a domain name into an IP address?",
    expected_keywords: ["dns", "root nameserver", "tld", "authoritative", "recursive resolver", "ip address"],
    difficulty: "Medium",
    reference_concept: "A recursive resolver queries root DNS servers, then Top-Level Domain (TLD) servers, and finally authoritative name servers to resolve the domain to an IP address."
  },
  {
    id: "eval-011",
    category: "Database Systems",
    question: "What are ACID properties in database transaction management?",
    expected_keywords: ["acid", "atomicity", "consistency", "isolation", "durability", "transaction"],
    difficulty: "Easy",
    reference_concept: "Atomicity ensures all-or-nothing execution, Consistency enforces validity rules, Isolation prevents concurrent collision, and Durability guarantees committed changes survive crashes."
  },
  {
    id: "eval-012",
    category: "Database Systems",
    question: "Contrast relational SQL databases with NoSQL databases like Amazon DynamoDB.",
    expected_keywords: ["sql", "nosql", "dynamodb", "partition key", "schema", "horizontal scaling"],
    difficulty: "Medium",
    reference_concept: "SQL databases use structured schemas and relational joins. DynamoDB uses key-value/document structures with partition keys for high-throughput horizontal scaling."
  }
];

export const INITIAL_DYNAMO_RECORDS: DynamoRecord[] = [
  {
    PK: "MODEL_VERSION",
    SK: "v1.0.0-baseline",
    EntityType: "MODEL_VERSION",
    Timestamp: "2026-10-30T07:10:00Z",
    Summary: "Initial baseline model version deployment",
    Details: {
      application_version: "1.0.0",
      model_provider: "Groq (LLaMA 3.3 70B)",
      model_identifier: "llama-3.3-70b-versatile",
      change_reason: "Initial project deployment for VIT coursework",
      pipeline_stage: "Production-Baseline"
    }
  },
  {
    PK: "RETRAIN_RUN",
    SK: "mlops-run-20261030-141419-884bfb",
    EntityType: "RETRAIN_RUN",
    Timestamp: "2026-10-30T07:14:19Z",
    Summary: "Automated benchmark evaluation run on 12 samples",
    Details: {
      run_id: "mlops-run-20261030-141419-884bfb",
      previous_version: "v1.0.0-baseline",
      new_version: "v1.1.0-retrained",
      accuracy: 0.833,
      f1_score: 0.812,
      artifact_s3_uri: "s3://vit-study-assistant-artifacts-23mis0224/mlops-reports/mlops-run-20261030-141419-884bfb/report.json"
    }
  },
  {
    PK: "CONVERSATION#conv-7f41a8e9",
    SK: "2026-10-30T07:12:30Z",
    EntityType: "CONVERSATION",
    Timestamp: "2026-10-30T07:12:30Z",
    Summary: "Query: Explain Coffman conditions for OS deadlock",
    Details: {
      user_message: "What are the four conditions for deadlock in OS?",
      response_mode: "fallback",
      model_identifier: "heuristic-academic-v1",
      duration_ms: 4.2,
      status: "success"
    }
  },
  {
    PK: "METRICS_SNAPSHOT",
    SK: "2026-10-30T07:15:00Z",
    EntityType: "METRIC",
    Timestamp: "2026-10-30T07:15:00Z",
    Summary: "Operational telemetry heartbeat snapshot",
    Details: {
      total_requests: 24,
      successful_requests: 24,
      failed_requests: 0,
      fallback_rate_pct: 12.5,
      average_duration_ms: 18.4
    }
  }
];

export const INITIAL_CLOUDWATCH_LOGS: CloudWatchLog[] = [
  {
    timestamp: "2026-10-30T07:10:02.140Z",
    level: "INFO",
    requestId: "c4a7e912-8812-4f11-9a2c-982141512301",
    message: "START RequestId: c4a7e912-8812-4f11-9a2c-982141512301 Version: $LATEST"
  },
  {
    timestamp: "2026-10-30T07:10:02.145Z",
    level: "INFO",
    requestId: "c4a7e912-8812-4f11-9a2c-982141512301",
    message: "Lambda invocation received",
    eventPayload: { http_method: "GET", path: "/api/health", function_name: "StudyAssistantBackend" }
  },
  {
    timestamp: "2026-10-30T07:10:02.152Z",
    level: "INFO",
    requestId: "c4a7e912-8812-4f11-9a2c-982141512301",
    message: "REPORT RequestId: c4a7e912-8812-4f11-9a2c-982141512301 Duration: 7.21 ms Billed Duration: 8 ms Memory Size: 512 MB Max Memory Used: 78 MB"
  },
  {
    timestamp: "2026-10-30T07:12:30.081Z",
    level: "INFO",
    requestId: "f8b91012-3490-4a81-bb01-112349811202",
    message: "START RequestId: f8b91012-3490-4a81-bb01-112349811202 Version: $LATEST"
  },
  {
    timestamp: "2026-10-30T07:12:30.085Z",
    level: "INFO",
    requestId: "f8b91012-3490-4a81-bb01-112349811202",
    message: "METRICS_EVENT: {\"event\": \"api_request\", \"duration_ms\": 4.2, \"success\": true, \"response_mode\": \"fallback\"}"
  },
  {
    timestamp: "2026-10-30T07:12:30.091Z",
    level: "INFO",
    requestId: "f8b91012-3490-4a81-bb01-112349811202",
    message: "DynamoDB: Saved conversation conv-7f41a8e9 to StudyAssistantRecords"
  },
  {
    timestamp: "2026-10-30T07:12:30.095Z",
    level: "INFO",
    requestId: "f8b91012-3490-4a81-bb01-112349811202",
    message: "REPORT RequestId: f8b91012-3490-4a81-bb01-112349811202 Duration: 14.32 ms Billed Duration: 15 ms Memory Size: 512 MB Max Memory Used: 82 MB"
  }
];

export const TEST_SUITE_RESULTS = [
  { id: "API-01", file: "tests/test_api.py", name: "test_root_endpoint", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-02", file: "tests/test_api.py", name: "test_health_endpoint", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-03", file: "tests/test_api.py", name: "test_metrics_endpoint", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-04", file: "tests/test_api.py", name: "test_metrics_counter_increment", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-05", file: "tests/test_api.py", name: "test_model_version_endpoint", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-06", file: "tests/test_api.py", name: "test_chat_empty_message_validation", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-07", file: "tests/test_api.py", name: "test_chat_whitespace_only_validation", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-08", file: "tests/test_api.py", name: "test_chat_missing_message_field", status: "PASSED", time: "0.01s", category: "API" },
  { id: "API-09", file: "tests/test_api.py", name: "test_chat_message_too_long_validation", status: "PASSED", time: "0.01s", category: "API" },
  { id: "AWS-01", file: "tests/test_aws_services.py", name: "test_s3_upload_mock", status: "PASSED", time: "0.02s", category: "AWS" },
  { id: "AWS-02", file: "tests/test_aws_services.py", name: "test_dynamodb_insert_mock", status: "PASSED", time: "0.01s", category: "AWS" },
  { id: "AWS-03", file: "tests/test_aws_services.py", name: "test_lambda_handler_api_gateway_health_event", status: "PASSED", time: "0.02s", category: "AWS" },
  { id: "AWS-04", file: "tests/test_aws_services.py", name: "test_lambda_handler_api_gateway_chat_event", status: "PASSED", time: "0.02s", category: "AWS" },
  { id: "CHAT-01", file: "tests/test_chat.py", name: "test_chat_fallback_scrum_topic", status: "PASSED", time: "0.01s", category: "Chat" },
  { id: "CHAT-02", file: "tests/test_chat.py", name: "test_chat_fallback_devops_topic", status: "PASSED", time: "0.01s", category: "Chat" },
  { id: "CHAT-03", file: "tests/test_chat.py", name: "test_chat_fallback_deadlock_topic", status: "PASSED", time: "0.01s", category: "Chat" },
  { id: "CHAT-04", file: "tests/test_chat.py", name: "test_chat_fallback_general_query", status: "PASSED", time: "0.01s", category: "Chat" },
  { id: "CHAT-05", file: "tests/test_chat.py", name: "test_mocked_groq_ai_success", status: "PASSED", time: "0.01s", category: "Chat" },
  { id: "CHAT-06", file: "tests/test_chat.py", name: "test_mocked_groq_ai_exception_routes_to_fallback", status: "PASSED", time: "0.01s", category: "Chat" },
  { id: "DB-01", file: "tests/test_database.py", name: "test_sqlite_table_initialization", status: "PASSED", time: "0.01s", category: "Database" },
  { id: "DB-02", file: "tests/test_database.py", name: "test_sqlite_insert_and_retrieve_conversation", status: "PASSED", time: "0.01s", category: "Database" },
  { id: "DB-03", file: "tests/test_database.py", name: "test_sqlite_model_version_update", status: "PASSED", time: "0.01s", category: "Database" },
  { id: "DB-04", file: "tests/test_database.py", name: "test_sqlite_retrain_run_record", status: "PASSED", time: "0.01s", category: "Database" },
  { id: "MLOPS-01", file: "tests/test_mlops.py", name: "test_evaluation_dataset_structure", status: "PASSED", time: "0.01s", category: "MLOps" },
  { id: "MLOPS-02", file: "tests/test_mlops.py", name: "test_evaluate_single_sample", status: "PASSED", time: "0.01s", category: "MLOps" },
  { id: "MLOPS-03", file: "tests/test_mlops.py", name: "test_mlops_run_simulation", status: "PASSED", time: "0.02s", category: "MLOps" },
  { id: "MLOPS-04", file: "tests/test_mlops.py", name: "test_mlops_api_endpoint", status: "PASSED", time: "0.01s", category: "MLOps" }
];
