export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  response_mode?: 'ai' | 'fallback' | 'groq';
  model_identifier?: string;
  duration_ms?: number;
  timestamp: string;
  storage_recorded?: boolean;
}

export interface EvalSample {
  id: string;
  category: string;
  question: string;
  expected_keywords: string[];
  difficulty: 'Easy' | 'Medium' | 'Hard';
  reference_concept: string;
  matched_keywords?: string[];
  precision?: number;
  recall?: number;
  f1_score?: number;
  passed?: boolean;
}

export interface RetrainRun {
  run_id: string;
  timestamp: string;
  status: string;
  previous_version: string;
  new_version: string;
  samples_evaluated: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  artifact_path: string;
  s3_uploaded: boolean;
  dynamodb_recorded: boolean;
}

export interface DynamoRecord {
  PK: string;
  SK: string;
  EntityType: 'CONVERSATION' | 'MODEL_VERSION' | 'RETRAIN_RUN' | 'METRIC';
  Timestamp: string;
  Summary: string;
  Details: Record<string, any>;
}

export interface CloudWatchLog {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR';
  requestId: string;
  message: string;
  eventPayload?: Record<string, any>;
}
