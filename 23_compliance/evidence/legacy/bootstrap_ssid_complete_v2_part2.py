# ============================================================================
# TEIL 2: ERWEITERTE CONTENT-GENERATOREN
# Diesen Code an Teil 1 anhängen!
# ============================================================================

# ============================================================================
# OPENAPI SPECS - VOLLSTÄNDIG
# ============================================================================

def gen_openapi_risk_scoring(root: Dict, shard: Dict) -> str:
    """Vollständige OpenAPI 3.1 Spec mit allen Response-Codes"""
    ex_hash = h(f"{root['name']}_{shard['name']}_risk")
    
    return f"""openapi: 3.1.0
info:
  title: "{shard['desc']} - Risk Scoring API"
  description: "Risk Scoring API für {root['desc']} im Kontext {shard['sub_desc']}"
  version: "{VERSION}"
  contact:
    name: "SSID {root['name']} Team"
    email: "team-{root['id']}@example.local"
  license:
    name: "Proprietary"

servers:
  - url: "https://{root['name']}-{shard['domain']}.ssid.example"
    description: "Production"
  - url: "https://staging-{root['name']}-{shard['domain']}.ssid.example"
    description: "Staging"

security:
  - mTLS: []

paths:
  /v1/risk-score:
    post:
      operationId: computeRiskScore
      summary: "Compute risk score for {shard['domain']} data"
      description: |
        Computes a risk score based on hash of input data.
        **CRITICAL**: Only hashes are accepted, no raw PII.
      tags:
        - "risk-scoring"
      parameters:
        - $ref: '#/components/parameters/RequestID'
        - $ref: '#/components/parameters/TraceID'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RiskScoreRequest'
            examples:
              valid_request:
                summary: "Valid hash-based request"
                value:
                  data_hash: "{ex_hash}"
                  context:
                    timestamp: "{ISO_DATE}"
                    source: "api"
              invalid_request:
                summary: "Invalid request (wrong hash length)"
                value:
                  data_hash: "invalid"
      responses:
        '200':
          description: "Risk score computed successfully"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RiskScoreResponse'
              examples:
                low_risk:
                  value:
                    risk_score: 0.15
                    confidence: 0.95
                    evidence_anchor:
                      hash: "{h('evidence_low')}"
                      timestamp: "{ISO_DATE}"
                high_risk:
                  value:
                    risk_score: 0.85
                    confidence: 0.92
                    evidence_anchor:
                      hash: "{h('evidence_high')}"
                      timestamp: "{ISO_DATE}"
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '422':
          description: "PII detected or validation failed"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: "pii_detected"
                message: "Raw PII detected in request. Only hashes allowed."
                timestamp: "{ISO_DATE}"
        '429':
          $ref: '#/components/responses/TooManyRequests'
        '500':
          $ref: '#/components/responses/InternalServerError'
        '503':
          $ref: '#/components/responses/ServiceUnavailable'
      x-ratelimit:
        limit: 1000
        window: "1m"
      x-cache:
        enabled: false
        reason: "Dynamic computation required"

  /health/live:
    get:
      operationId: healthLive
      summary: "Liveness probe"
      tags:
        - "health"
      responses:
        '200':
          description: "Service is alive"
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: ["alive"]

  /health/ready:
    get:
      operationId: healthReady
      summary: "Readiness probe"
      tags:
        - "health"
      responses:
        '200':
          description: "Service is ready"
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: ["ready"]
                  dependencies:
                    type: object
                    properties:
                      redis:
                        type: string
                        enum: ["up", "down"]
                      audit_logging:
                        type: string
                        enum: ["up", "down"]

components:
  securitySchemes:
    mTLS:
      type: mutualTLS
      description: "Mutual TLS authentication with client certificates"

  parameters:
    RequestID:
      name: X-Request-ID
      in: header
      required: true
      description: "Unique request identifier for tracing"
      schema:
        type: string
        format: uuid
        example: "550e8400-e29b-41d4-a716-446655440000"
    
    TraceID:
      name: X-Trace-ID
      in: header
      required: false
      description: "Optional trace ID for distributed tracing"
      schema:
        type: string
        pattern: '^[a-f0-9]{{32}}$'

  schemas:
    Hash:
      type: string
      pattern: '^[a-f0-9]{{64}}$'
      minLength: 64
      maxLength: 64
      description: "SHA3-256 hash (64 hex characters)"
      example: "{ex_hash}"
    
    RiskScoreRequest:
      type: object
      required:
        - data_hash
      properties:
        data_hash:
          $ref: '#/components/schemas/Hash'
        context:
          type: object
          description: "Optional context metadata (hashed)"
          additionalProperties: true
      additionalProperties: false
    
    RiskScoreResponse:
      type: object
      required:
        - risk_score
        - evidence_anchor
      properties:
        risk_score:
          type: number
          format: float
          minimum: 0.0
          maximum: 1.0
          description: "Risk score between 0 (low) and 1 (high)"
          example: 0.15
        confidence:
          type: number
          format: float
          minimum: 0.0
          maximum: 1.0
          description: "Confidence in risk score"
          example: 0.95
        evidence_anchor:
          type: object
          required:
            - hash
            - timestamp
          properties:
            hash:
              $ref: '#/components/schemas/Hash'
            timestamp:
              type: string
              format: date-time
            blockchain_tx:
              type: string
              description: "Optional blockchain transaction hash"
      additionalProperties: false
    
    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          description: "Error code"
          example: "validation_error"
        message:
          type: string
          description: "Human-readable error message"
          example: "Invalid hash format"
        timestamp:
          type: string
          format: date-time
        trace_id:
          type: string
          description: "Request trace ID for debugging"

  responses:
    BadRequest:
      description: "Bad Request - Invalid input"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "bad_request"
            message: "Invalid request format"
    
    Unauthorized:
      description: "Unauthorized - Invalid or missing authentication"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    Forbidden:
      description: "Forbidden - Insufficient permissions"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    TooManyRequests:
      description: "Too Many Requests - Rate limit exceeded"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
      headers:
        X-RateLimit-Limit:
          schema:
            type: integer
          description: "Request limit per window"
        X-RateLimit-Remaining:
          schema:
            type: integer
          description: "Remaining requests in current window"
        X-RateLimit-Reset:
          schema:
            type: integer
          description: "Unix timestamp when limit resets"
    
    InternalServerError:
      description: "Internal Server Error"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    ServiceUnavailable:
      description: "Service Unavailable"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
"""

def gen_openapi_matching(root: Dict, shard: Dict) -> str:
    """Vollständige Matching API Spec"""
    ex_hash = h(f"{root['name']}_{shard['name']}_match")
    
    return f"""openapi: 3.1.0
info:
  title: "{shard['desc']} - Matching API"
  description: "Feature matching API für {shard['domain']}"
  version: "{VERSION}"

servers:
  - url: "https://{root['name']}-{shard['domain']}.ssid.example"

security:
  - mTLS: []

paths:
  /v1/match:
    post:
      operationId: performMatching
      summary: "Perform feature matching"
      parameters:
        - $ref: '#/components/parameters/RequestID'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [feature_hash]
              properties:
                feature_hash:
                  $ref: '#/components/schemas/Hash'
                threshold:
                  type: number
                  format: float
                  minimum: 0.0
                  maximum: 1.0
                  default: 0.8
              additionalProperties: false
      responses:
        '200':
          description: "Match result"
          content:
            application/json:
              schema:
                type: object
                properties:
                  match_found:
                    type: boolean
                  similarity:
                    type: number
                    format: float
                  evidence_hash:
                    $ref: '#/components/schemas/Hash'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '422':
          $ref: '#/components/responses/UnprocessableEntity'
        '429':
          $ref: '#/components/responses/TooManyRequests'
        '500':
          $ref: '#/components/responses/InternalServerError'

components:
  securitySchemes:
    mTLS:
      type: mutualTLS
  
  parameters:
    RequestID:
      name: X-Request-ID
      in: header
      required: true
      schema:
        type: string
        format: uuid
  
  schemas:
    Hash:
      type: string
      pattern: '^[a-f0-9]{{64}}$'
      minLength: 64
      maxLength: 64
      example: "{ex_hash}"
    
    Error:
      type: object
      required: [error, message]
      properties:
        error:
          type: string
        message:
          type: string
        timestamp:
          type: string
          format: date-time
  
  responses:
    BadRequest:
      description: "Bad Request"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    Unauthorized:
      description: "Unauthorized"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    UnprocessableEntity:
      description: "Unprocessable Entity - PII detected"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    TooManyRequests:
      description: "Too Many Requests"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    InternalServerError:
      description: "Internal Server Error"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
"""

# ============================================================================
# JSON SCHEMAS - VOLLSTÄNDIG
# ============================================================================

def gen_schema_document(root: Dict, shard: Dict) -> str:
    """Vollständiges JSON Schema mit $defs und Examples"""
    return f"""{{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ssid.example/schemas/{shard['domain']}_document.json",
  "title": "{shard['desc']} Document",
  "description": "Schema for {shard['domain']} documents in SSID system",
  "type": "object",
  "required": ["id", "data_hash"],
  "properties": {{
    "id": {{
      "type": "string",
      "format": "uuid",
      "description": "Unique document identifier"
    }},
    "data_hash": {{
      "$ref": "#/$defs/Hash",
      "description": "SHA3-256 hash of document content"
    }},
    "metadata_hash": {{
      "$ref": "#/$defs/Hash",
      "description": "SHA3-256 hash of metadata"
    }},
    "created_at": {{
      "type": "string",
      "format": "date-time",
      "description": "Document creation timestamp"
    }},
    "updated_at": {{
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp"
    }},
    "version": {{
      "type": "integer",
      "minimum": 1,
      "description": "Document version number"
    }}
  }},
  "additionalProperties": false,
  "$defs": {{
    "Hash": {{
      "type": "string",
      "pattern": "^[a-f0-9]{{64}}$",
      "minLength": 64,
      "maxLength": 64,
      "description": "SHA3-256 hash (64 hex characters)"
    }}
  }},
  "examples": [
    {{
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "data_hash": "{h(f'{shard['domain']}_doc_example')}",
      "metadata_hash": "{h(f'{shard['domain']}_meta_example')}",
      "created_at": "{ISO_DATE}",
      "updated_at": "{ISO_DATE}",
      "version": 1
    }}
  ]
}}
"""

def gen_schema_evidence(root: Dict, shard: Dict) -> str:
    """Vollständiges Evidence Schema"""
    return f"""{{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ssid.example/schemas/{shard['domain']}_evidence.json",
  "title": "{shard['desc']} Evidence",
  "description": "Evidence record for {shard['domain']} operations",
  "type": "object",
  "required": ["evidence_id", "evidence_hash", "operation"],
  "properties": {{
    "evidence_id": {{
      "type": "string",
      "format": "uuid",
      "description": "Unique evidence identifier"
    }},
    "evidence_hash": {{
      "$ref": "#/$defs/Hash",
      "description": "SHA3-256 hash of evidence data"
    }},
    "operation": {{
      "type": "string",
      "enum": ["create", "read", "update", "delete", "verify"],
      "description": "Operation type that generated evidence"
    }},
    "timestamp": {{
      "type": "string",
      "format": "date-time",
      "description": "Evidence creation timestamp"
    }},
    "anchors": {{
      "type": "array",
      "description": "Blockchain anchors",
      "items": {{
        "$ref": "#/$defs/Anchor"
      }},
      "minItems": 0
    }},
    "metadata": {{
      "type": "object",
      "description": "Additional metadata (hashed)",
      "additionalProperties": true
    }}
  }},
  "additionalProperties": false,
  "$defs": {{
    "Hash": {{
      "type": "string",
      "pattern": "^[a-f0-9]{{64}}$",
      "minLength": 64,
      "maxLength": 64
    }},
    "Anchor": {{
      "type": "object",
      "required": ["network", "tx_hash", "status"],
      "properties": {{
        "network": {{
          "type": "string",
          "enum": ["ethereum:sepolia", "polygon:amoy"],
          "description": "Blockchain network"
        }},
        "tx_hash": {{
          "type": "string",
          "pattern": "^[a-f0-9]{{64}}$",
          "description": "Transaction hash"
        }},
        "block_number": {{
          "type": "integer",
          "minimum": 0,
          "description": "Block number"
        }},
        "status": {{
          "type": "string",
          "enum": ["pending", "confirmed", "failed"],
          "description": "Anchor status"
        }},
        "timestamp": {{
          "type": "string",
          "format": "date-time"
        }}
      }}
    }}
  }},
  "examples": [
    {{
      "evidence_id": "660f9511-f39c-52e5-b827-557766551111",
      "evidence_hash": "{h(f'{shard['domain']}_evidence')}",
      "operation": "create",
      "timestamp": "{ISO_DATE}",
      "anchors": [
        {{
          "network": "polygon:amoy",
          "tx_hash": "{h('tx_example')}",
          "block_number": 12345678,
          "status": "confirmed",
          "timestamp": "{ISO_DATE}"
        }}
      ]
    }}
  ]
}}
"""

# ============================================================================
# POLICIES - ALLE 7
# ============================================================================

def gen_policy_no_pii(root: Dict, shard: Dict) -> str:
    """Policy 1: No PII Storage"""
    return f"""# Policy: No PII Storage
version: 1.0.0
policy_id: "no_pii_{root['id']}_{shard['id']}"

scope:
  - "All implementations"
  - "{root['id']}_{root['name']}/shards/{shard_folder_name(shard)}"

rules:
  - rule_id: "R001"
    description: "Forbid raw PII storage"
    enforcement: "blocking"
    checks:
      - type: "semgrep"
        severity: "ERROR"
        patterns:
          - "ssn"
          - "passport"
          - "biometric"
          - "password"
      - type: "runtime"
        detector: "pii_detector"
        action: "reject_request"

  - rule_id: "R002"
    description: "Enforce immediate hashing"
    requirement: "Hash within 100ms of receipt"
    algorithm: "SHA3-256"
    pepper: "per_tenant"

violations:
  - level: "CRITICAL"
    action: "system_block"
    notification: "compliance@example.local"
    escalation: "immediate"

audit:
  log_to: "02_audit_logging"
  retention_days: 3650
  evidence_required: true
"""

def gen_policy_hash_only(root: Dict, shard: Dict) -> str:
    """Policy 2: Hash-Only Enforcement"""
    return f"""# Policy: Hash-Only Enforcement
version: 1.0.0
policy_id: "hash_only_{root['id']}_{shard['id']}"

hash_requirements:
  algorithm: "sha3_256"
  output_format: "hex"
  length: 64
  deterministic: true
  pepper_strategy: "per_tenant"
  rotation_policy:
    enabled: true
    frequency_days: 90

validation:
  - field: "data_hash"
    regex: "^[a-f0-9]{{64}}$"
    required: true
    min_length: 64
    max_length: 64
  
  - field: "metadata_hash"
    regex: "^[a-f0-9]{{64}}$"
    required: false

storage:
  raw_data_retention: "0 seconds"
  hash_retention: "3650 days"
  backup_strategy: "hash_only"

enforcement:
  pre_storage_check: true
  runtime_validation: true
  audit_trail: true
"""

def gen_policy_gdpr(root: Dict, shard: Dict) -> str:
    """Policy 3: GDPR Compliance"""
    return f"""# Policy: GDPR Compliance
version: 1.0.0
policy_id: "gdpr_{root['id']}_{shard['id']}"

scope:
  - "EU Data Subjects"
  - "{shard['domain']} domain"

rights:
  right_to_access:
    enabled: true
    response_time_days: 30
    format: "JSON"
    includes:
      - "all_hashes"
      - "metadata"
      - "audit_trail"
  
  right_to_erasure:
    enabled: true
    mechanism: "hash_rotation"
    implementation: "new_pepper_invalidates_old_hashes"
    retention_override: "legal_hold_only"
  
  right_to_portability:
    enabled: true
    format: "JSON"
    scope: "all_user_hashes"
  
  right_to_rectification:
    enabled: true
    mechanism: "new_hash_generation"

purpose_limitation:
  allowed_purposes:
    - "{shard['desc']} processing"
    - "audit_trail"
    - "compliance_reporting"
  forbidden_purposes:
    - "marketing"
    - "profiling_without_consent"

data_minimization:
  principle: "hash_only_no_raw_data"
  enforcement: "automatic"

consent:
  required_for:
    - "data_processing"
    - "hash_storage"
  granularity: "per_purpose"
  withdrawal: "immediate_effect"

breach_notification:
  authority_notification_hours: 72
  data_subject_notification: "without_undue_delay"
  documentation_required: true
"""

def gen_policy_bias_fairness(root: Dict, shard: Dict) -> str:
    """Policy 4: Bias & Fairness"""
    return f"""# Policy: Bias & Fairness
version: 1.0.0
policy_id: "bias_fairness_{root['id']}_{shard['id']}"

scope:
  - "All AI/ML models in {shard['domain']}"

metrics:
  demographic_parity:
    enabled: true
    threshold: 0.05
    protected_attributes:
      - "gender"
      - "age"
      - "ethnicity"
  
  equal_opportunity:
    enabled: true
    threshold: 0.05
  
  disparate_impact:
    enabled: true
    ratio_threshold: 0.8

testing:
  frequency: "quarterly"
  datasets:
    - "production_sample"
    - "synthetic_adversarial"
  reporting: "mandatory"
  reviewer: "ethics_board@example.local"

mitigation:
  strategies:
    - "fairness_aware_training"
    - "adversarial_debiasing"
    - "threshold_optimization"
  continuous_monitoring: true
  alert_on_drift: true

transparency:
  model_cards: "required"
  explainability: "mandatory"
  disclosure: "public"

audit:
  frequency: "quarterly"
  external_auditor: true
  reports_published: true
"""

def gen_policy_evidence_audit(root: Dict, shard: Dict) -> str:
    """Policy 5: Evidence & Audit"""
    return f"""# Policy: Evidence & Audit
version: 1.0.0
policy_id: "evidence_audit_{root['id']}_{shard['id']}"

strategy: "hash_ledger_with_anchoring"

evidence_collection:
  events:
    - "data_received"
    - "data_processed"
    - "model_inference"
    - "evidence_created"
    - "hash_generated"
  granularity: "per_operation"
  storage: "WORM"

hash_ledger:
  algorithm: "SHA3-256"
  chain_validation: true
  immutability: "enforced"

anchoring:
  chains:
    - network: "ethereum:sepolia"
      frequency: "hourly"
      batch_size: 1000
    - network: "polygon:amoy"
      frequency: "hourly"
      batch_size: 1000
  retry_policy:
    max_retries: 3
    backoff: "exponential"
  verification: "automatic"

retention:
  evidence_days: 3650
  audit_logs_days: 3650
  anchors_permanent: true

compliance_reporting:
  formats:
    - "JSON"
    - "PDF"
  frequency: "on_demand"
  automated: true
  encryption: "AES-256-GCM"
"""

def gen_policy_secrets(root: Dict, shard: Dict) -> str:
    """Policy 6: Secrets Management"""
    return f"""# Policy: Secrets Management
version: 1.0.0
policy_id: "secrets_{root['id']}_{shard['id']}"

provider: "15_infra/vault"

secrets_types:
  - "api_keys"
  - "database_credentials"
  - "encryption_keys"
  - "tls_certificates"
  - "pepper_values"

storage:
  location: "vault://ssid/{root['name']}/{shard['domain']}"
  encryption: "AES-256-GCM"
  access_control: "RBAC"

rotation:
  frequency_days: 90
  automatic: true
  grace_period_hours: 24
  notification: true

access:
  authentication: "mTLS"
  authorization: "RBAC"
  audit_logging: true
  
policies:
  - no_secrets_in_code: "enforced"
  - no_secrets_in_logs: "enforced"
  - no_secrets_in_git: "enforced"
  - template_files_only: ".template suffix required"

violations:
  detection: "automatic"
  action: "block_commit"
  notification: "security@example.local"
"""

def gen_policy_versioning(root: Dict, shard: Dict) -> str:
    """Policy 7: Versioning & Breaking Changes"""
    return f"""# Policy: Versioning & Breaking Changes
version: 1.0.0
policy_id: "versioning_{root['id']}_{shard['id']}"

versioning_scheme: "semver"
format: "MAJOR.MINOR.PATCH"

breaking_changes:
  notice_period_days: 180
  requirements:
    - migration_guide: "mandatory"
    - compatibility_layer: "mandatory"
    - rfc_approval: "architecture_board"
  
  examples:
    - "API endpoint removal"
    - "Schema field removal"
    - "Response format change"

deprecation_process:
  steps:
    - announcement: "180 days before removal"
    - warnings: "in responses + documentation"
    - compatibility_layer: "maintained during period"
    - removal: "after notice period"
  
  communication:
    - "changelog"
    - "email_notification"
    - "api_headers"

compatibility:
  backward_compatibility: "preferred"
  forward_compatibility: "when_possible"
  version_support: "N-1 major versions"

release_process:
  rfc_required_for: ["MAJOR", "breaking_MINOR"]
  approval_quorum: 2
  reviewers:
    - "architecture_board"
    - "affected_teams"
"""

# ============================================================================
# WEITER IN TEIL 3...
# ============================================================================
