"""Rule-Based Academic Fallback Service
Provides structured, reliable study responses when external AI providers
are unconfigured, unreachable, or rate-limited.
"""

import re
from typing import Dict, Tuple

# Knowledge base of core academic subjects
KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "scrum": {
        "title": "Agile Scrum Framework & Lifecycle",
        "definition": "Scrum is an iterative, incremental Agile framework for developing complex software products through fixed-length iterations called Sprints (typically 1 to 4 weeks).",
        "key_points": [
            "Roles: Product Owner (backlog prioritization), Scrum Master (process coach & impediment remover), Development Team (cross-functional builders).",
            "Artifacts: Product Backlog (prioritized feature list), Sprint Backlog (committed work for current sprint), Product Increment (potentially shippable output).",
            "Ceremonies: Sprint Planning (scope definition), Daily Scrum (15-min sync), Sprint Review (stakeholder demo), Sprint Retrospective (team process reflection)."
        ],
        "exam_tip": "Remember that Scrum emphasizes empirical process control: Transparency, Inspection, and Adaptation."
    },
    "agile": {
        "title": "Agile Development Process Principles",
        "definition": "Agile is a set of software development methodologies based on iterative development, customer collaboration, and rapid response to change (Agile Manifesto, 2001).",
        "key_points": [
            "Individuals and interactions over processes and tools.",
            "Working software over comprehensive documentation.",
            "Customer collaboration over contract negotiation.",
            "Responding to change over following a plan."
        ],
        "exam_tip": "Agile minimizes risk by building software in short timeboxes with continuous feedback loops."
    },
    "devops": {
        "title": "DevOps Practices & Culture",
        "definition": "DevOps is an organizational culture and engineering practice combining Software Development (Dev) and IT Operations (Ops) to shorten systems development life cycles and deliver continuous high software quality.",
        "key_points": [
            "CI/CD: Automated build, test, and release pipelines to eliminate manual handoffs.",
            "Infrastructure as Code (IaC): Provisioning servers, VPCs, and storage through versioned declarations (e.g. Terraform, AWS SAM, CloudFormation).",
            "Observability: Proactive logging, distributed tracing, and metrics alarms (e.g. Amazon CloudWatch, Prometheus)."
        ],
        "exam_tip": "CALMS framework: Culture, Automation, Lean, Measurement, and Sharing."
    },
    "ci/cd": {
        "title": "Continuous Integration & Continuous Delivery (CI/CD)",
        "definition": "CI/CD automates the steps in software delivery from code commit to production deployment.",
        "key_points": [
            "Continuous Integration (CI): Developers merge code frequently to main branch; automated unit and integration tests run on every commit to catch defects early.",
            "Continuous Delivery (CD): Ensures code is always in a deployable state with automated release packaging and staging deployment.",
            "Continuous Deployment: Automatically pushes changes directly to production if all pipeline stages pass without manual intervention."
        ],
        "exam_tip": "In this project, GitHub Actions handles CI by running pytest across Python matrices on pull requests."
    },
    "serverless": {
        "title": "Serverless Architecture & AWS Lambda",
        "definition": "Serverless computing executes code in stateless compute containers triggered by events without requiring server provisioning, maintenance, or scaling management.",
        "key_points": [
            "Event-Driven: Triggered by HTTP requests (API Gateway), database streams (DynamoDB Streams), or S3 uploads.",
            "Scale-to-Zero: Zero cost when idle; bills only for the millisecond duration and memory allocated during execution.",
            "Microservices Integration: Decoupled architecture communicating via HTTP APIs, queues (SQS), or message buses (EventBridge)."
        ],
        "exam_tip": "Be aware of cold starts—the slight latency incurred when Lambda initializes a new runtime container."
    },
    "dynamodb": {
        "title": "Amazon DynamoDB NoSQL Architecture",
        "definition": "Amazon DynamoDB is a fully managed, serverless, key-value and document NoSQL database designed for single-digit millisecond latency at any scale.",
        "key_points": [
            "Primary Keys: Partition Key (HASH) distributes data across physical partitions; optional Sort Key (RANGE) sorts data within a partition.",
            "Schema-Free: Attributes are flexible per item, with only the primary key being required upon creation.",
            "Capacity Modes: On-Demand capacity (auto-scaling pay-per-request) or Provisioned capacity with auto-scaling."
        ],
        "exam_tip": "In our project, table 'StudyAssistantRecords' uses PK as category/ID and SK as timestamp for efficient time-series queries."
    },
    "s3": {
        "title": "Amazon Simple Storage Service (Amazon S3)",
        "definition": "Amazon S3 is an object storage service offering 99.999999999% (11 9's) data durability, high availability, and virtually unlimited scalability.",
        "key_points": [
            "Buckets & Objects: Data is stored as objects (file + metadata) inside globally unique buckets.",
            "Storage Classes: Standard, Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier Flexible, and Deep Archive.",
            "Security: Private by default; controlled via IAM policies, Bucket Policies, and Access Control Lists (ACLs)."
        ],
        "exam_tip": "We use Amazon S3 for storing MLOps evaluation datasets and retraining simulation report artifacts."
    },
    "cloudwatch": {
        "title": "Amazon CloudWatch Monitoring & Observability",
        "definition": "Amazon CloudWatch provides telemetry data and actionable insights for AWS resources and applications running on AWS and on-premises.",
        "key_points": [
            "CloudWatch Logs: Centralized aggregation of Lambda stdout/stderr and application log events.",
            "CloudWatch Metrics: Standard metrics (Invocations, Errors, Duration) and custom metrics generated via embedded metric format.",
            "CloudWatch Alarms: Automated triggers configured on metric thresholds to send SNS notifications or take recovery actions."
        ],
        "exam_tip": "Lambda automatically streams all standard Python logging statements to CloudWatch Log Groups."
    },
    "mlops": {
        "title": "Machine Learning Operations (MLOps) Lifecycle",
        "definition": "MLOps is the discipline of automating and standardizing the end-to-end machine learning lifecycle from data ingestion to model deployment and monitoring.",
        "key_points": [
            "Continuous Training (CT): Automated pipelines that retrain models when data drift or performance degradation exceeds set thresholds.",
            "Model Registry & Versioning: Tracking model artifacts, hyperparameters, benchmark evaluation metrics, and lineage.",
            "Continuous Monitoring: Tracking prediction drift, feature distributions, latency, and business KPIs in real time."
        ],
        "exam_tip": "In academic demonstrations, distinguish clearly between educational retraining simulation and full distributed training cluster runs."
    },
    "deadlock": {
        "title": "Operating Systems: Deadlock & Coffman Conditions",
        "definition": "A deadlock is a situation where a set of processes are blocked because each process is holding a resource and waiting for another resource acquired by some other process.",
        "key_points": [
            "Mutual Exclusion: At least one resource must be held in a non-shareable mode.",
            "Hold and Wait: A process must be holding at least one resource and waiting to acquire additional resources held by others.",
            "No Preemption: Resources cannot be preempted; they can only be released voluntarily by the holding process.",
            "Circular Wait: A closed chain of processes exists such that each process holds at least one resource needed by the next."
        ],
        "exam_tip": "To prevent deadlock, invalidate at least one of the four Coffman conditions (e.g. enforce resource ordering to eliminate circular wait)."
    },
    "tcp": {
        "title": "Computer Networks: TCP Three-Way Handshake",
        "definition": "Transmission Control Protocol (TCP) uses a three-way handshake to establish a reliable, full-duplex connection between a client and a server before transmitting data.",
        "key_points": [
            "Step 1 (SYN): Client sends a SYN segment with an initial sequence number (ISN = x) to request a connection.",
            "Step 2 (SYN-ACK): Server receives SYN, allocates buffers, and sends SYN-ACK with ACK = x + 1 and server ISN = y.",
            "Step 3 (ACK): Client receives SYN-ACK and sends ACK with ACK = y + 1. The connection is now ESTABLISHED."
        ],
        "exam_tip": "TCP provides reliable, ordered, and error-checked byte stream delivery; UDP is connectionless and best-effort."
    },
    "acid": {
        "title": "Database Systems: ACID Properties",
        "definition": "ACID is an acronym representing the four key properties that guarantee reliable processing of database transactions.",
        "key_points": [
            "Atomicity: 'All or nothing'—either all statements of a transaction complete successfully, or all changes are rolled back.",
            "Consistency: Transactions take the database from one valid state to another, maintaining all schema constraints and invariants.",
            "Isolation: Concurrent transactions execute independently without interfering with one another (isolation levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable).",
            "Durability: Once a transaction commits, its modifications are permanently recorded on non-volatile storage, surviving crashes."
        ],
        "exam_tip": "NoSQL databases often relax strict ACID in favor of BASE (Basically Available, Soft state, Eventual consistency) for horizontal scale."
    }
}


def generate_fallback_response(query: str) -> Tuple[str, str]:
    """
    Generate an honest, structured academic study response based on keyword matching.
    Returns (response_text, matched_topic).
    """
    cleaned = query.lower().strip()

    # Search for matching knowledge base entry
    matched_entry = None
    matched_topic = "general_academic"

    # Priority check for specific keywords
    keywords_map = {
        "scrum": ["scrum", "sprint", "standup", "daily scrum", "product owner", "scrum master"],
        "agile": ["agile", "agile manifesto", "user story", "kanban", "velocity", "iteration"],
        "devops": ["devops", "ci/cd", "pipeline", "infrastructure as code", "iac", "deployment"],
        "ci/cd": ["continuous integration", "continuous delivery", "continuous deployment", "github actions"],
        "serverless": ["serverless", "lambda", "aws lambda", "api gateway", "faas", "microservice"],
        "dynamodb": ["dynamodb", "nosql", "partition key", "sort key", "dynamo"],
        "s3": ["s3", "amazon s3", "bucket", "object storage", "simple storage service"],
        "cloudwatch": ["cloudwatch", "logging", "metrics", "alarm", "observability", "log group"],
        "mlops": ["mlops", "model drift", "retraining", "model version", "machine learning operations"],
        "deadlock": ["deadlock", "coffman", "mutual exclusion", "circular wait", "resource allocation"],
        "tcp": ["tcp", "three-way handshake", "handshake", "syn", "ack", "transmission control protocol"],
        "acid": ["acid", "atomicity", "consistency", "isolation", "durability", "transaction"]
    }

    for topic, kw_list in keywords_map.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", cleaned) for kw in kw_list):
            matched_entry = KNOWLEDGE_BASE[topic]
            matched_topic = topic
            break

    if matched_entry:
        reply = (
            f"### [Academic Concept] {matched_entry['title']}\n\n"
            f"**Core Definition:**\n{matched_entry['definition']}\n\n"
            f"**Key Architectural & Academic Principles:**\n"
            + "\n".join(f"- {pt}" for pt in matched_entry['key_points'])
            + f"\n\n**VIT Exam & Viva Tip:**\n{matched_entry['exam_tip']}\n\n"
            "---\n"
            "*Status: Generated via Rule-Based Academic Fallback (Deterministic Knowledge Engine).*"
        )
        return reply, matched_topic

    # General structured response for unmatched queries
    reply = (
        f"### [Study Assistant Guidance] Academic Analysis\n\n"
        f"**Topic Inquired:** \"{query[:120]}\"\n\n"
        "**Recommended Academic Study Framework:**\n"
        "1. **Core Fundamentals:** Define the underlying computer science or engineering principle.\n"
        "2. **Architectural Analysis:** Identify inputs, transformation processes, and expected outputs.\n"
        "3. **Trade-off Evaluation:** Compare advantages, limitations, and operational complexities.\n"
        "4. **Practical Demonstration:** Verify concepts through unit tests, metrics, and CI/CD pipelines.\n\n"
        "**Suggested Follow-up Prompts:**\n"
        "- *Explain Agile Scrum ceremonies and artifacts*\n"
        "- *What is the role of CI/CD in DevOps pipelines?*\n"
        "- *How does AWS Lambda serverless execution work?*\n"
        "- *Explain ACID properties and transaction isolation*\n"
        "- *What causes model drift in MLOps systems?*\n\n"
        "---\n"
        "*Status: Generated via Rule-Based Academic Fallback. To enable full generative AI reasoning, configure `GROQ_API_KEY` in your environment.*"
    )
    return reply, "general_academic"
