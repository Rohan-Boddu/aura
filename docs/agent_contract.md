# AURA 4.0 Agent API Contract

AURA 4.0 functions as an **Architecture Intelligence Layer for AI Coding Agents** (such as Claude Code, Cursor Agent, Antigravity, OpenHands, etc.). Before an AI agent attempts to edit code or apply changes to a codebase, it should consume these API endpoints to align with the repository structure, subsystem boundaries, blast radius, risks, and verification requirements.

---

## Core Operational Guarantees

### 1. Strict Read-Only Guarantee
AURA operates strictly as a read-only repository intelligence service. AURA will never:
- Edit, patch, or write to any files in the workspace.
- Run code compilation, execution, or automated test command runs outside of its metadata analysis.
- Apply git commits or changes.
The reference repositories (`D:\aura`, `D:\max_got_a_face`) and any scanned workspace remain 100% untouched.

### 2. Zero Fabrication Policy
All outputs originate from real static analysis (AST), dependency structures, route handlers, and git history commit data. If evidence cannot be retrieved, AURA returns:
```json
{
  "status": "unavailable",
  "reason": "Evidence not available."
}
```
AURA never invents synthetic nodes, edges, or mock confidence scores.

---

## API Endpoints Reference

### 1. Repository Brief API
**Endpoint:** `GET /api/repository_brief/<analysis_id>`

**Purpose:** Provides a concise architectural overview of the repository.

#### Response Example
```json
{
  "status": "available",
  "project_type": "Python/Flask",
  "entry_points": ["main.py"],
  "major_subsystems": [
    {
      "name": "Database Layer",
      "description": "Database adapters, schemas, models, SQL engines, and local stores.",
      "files": ["database.py"],
      "confidence": 0.98
    }
  ],
  "databases": ["ecommerce.db"],
  "architectural_risks": [],
  "confidence": 0.87,
  "evidence": [
    {
      "status": "available",
      "confidence": 0.87,
      "evidence_type": "ast",
      "evidence": ["AST coverage calculated at 100% on 7 files."]
    }
  ]
}
```

---

### 2. Agent Context API
**Endpoint:** `POST /api/agent_context/<analysis_id>`

**Purpose:** Generates goal-aware architectural recommendations and verification checklists.

#### Request Payload
```json
{
  "goal": "Add JWT Authentication"
}
```

#### Response Example
```json
{
  "status": "available",
  "goal": "Add JWT Authentication",
  "recommended_target": {
    "file": "auth.py",
    "subsystem": "Authentication Layer",
    "confidence": 0.83,
    "reasons": [
      "Located inside Authentication Layer",
      "Python module",
      "Matches intent concepts: auth, jwt, login"
    ]
  },
  "candidate_targets": [
    {
      "file": "auth.py",
      "score": 85,
      "reasons": ["Located inside Authentication Layer", "Matches intent concepts: auth, jwt"],
      "subsystem": "Authentication Layer"
    }
  ],
  "subsystems": [
    {
      "name": "Authentication Layer",
      "description": "User credential stores, sessions, JWT token interceptors, and password cryptography.",
      "files": ["auth.py", "jwt.py"],
      "confidence": 0.98
    }
  ],
  "companion_files": [
    {
      "file": "jwt.py",
      "confidence": 0.85,
      "reason": "Imported by auth.py"
    }
  ],
  "risks": [],
  "verification": [
    "Assert password hashes are salted and not exposed in `auth.py`.",
    "Verify JWT middleware intercepts unauthorized requests.",
    "Run test suite command: `pytest tests/test_auth.py`"
  ],
  "confidence": 0.87,
  "evidence": [
    {
      "status": "available",
      "confidence": 0.87,
      "evidence_type": "intent",
      "evidence": ["Goal matching concepts: auth, jwt, login pointing to target auth.py."]
    }
  ]
}
```

---

### 3. Change Impact API
**Endpoint:** `POST /api/change_impact/<analysis_id>`

**Purpose:** Determines the static and temporal blast radius of editing a specific module.

#### Request Payload
```json
{
  "file": "core/memory.py"
}
```

#### Response Example
```json
{
  "status": "available",
  "direct_dependencies": ["utils.py"],
  "reverse_dependencies": ["main.py", "orchestrator.py"],
  "cochange_dependencies": [
    {
      "file": "orchestrator.py",
      "probability": 0.67
    }
  ],
  "subsystem": "Memory Layer",
  "risk_score": 34,
  "confidence": 0.91,
  "evidence": [
    {
      "status": "available",
      "confidence": 0.91,
      "evidence_type": "dependency",
      "evidence": [
        "File core/memory.py imports 1 modules and is imported by 2 modules.",
        "Temporal analysis indicates 1 git co-change couplings."
      ]
    }
  ]
}
```

---

### 4. Ownership API
**Endpoint:** `POST /api/ownership/<analysis_id>`

**Purpose:** Resolves subsystem boundary context and related entry points/routes.

#### Request Payload
```json
{
  "file": "auth.py"
}
```

#### Response Example
```json
{
  "status": "available",
  "subsystem": "Authentication Layer",
  "related_files": ["jwt.py"],
  "entry_points": ["main.py"],
  "routes": [
    {
      "path": "/api/login",
      "method": "POST",
      "handler": "auth.py:login"
    }
  ],
  "confidence": 0.87
}
```

---

## Azure AI Foundry Integration Mapping

AURA 4.0 is structured to easily integrate as custom tools in **Azure AI Foundry** or semantic plugins in **Semantic Kernel**:

1. **`get_repository_brief` Tool**:
   - Maps to a global info retriever tool used during the initialization of an Agent's session to retrieve general project shape.
2. **`get_agent_context` Tool**:
   - Maps to the primary intent-mapping planner. An AI Agent triggers this tool whenever it plans a code change to verify its target files and fetch companion files.
3. **`get_change_impact` Tool**:
   - Maps to a safety gate tool to check dependency blast radius and calculate a risk score before editing sensitive modules.
4. **`get_ownership` Tool**:
   - Maps to a subsystem navigator tool, allowing the agent to understand layer boundaries and list relevant entry points.

### Integration Assets
We have compiled ready-to-use integration components to accelerate embedding AURA 4.0 into your AI workflows:
- **OpenAPI 3.0 Specification:** [docs/openapi.json](file:///d:/hackathon/docs/openapi.json) — Import this spec directly into the Azure AI Foundry portal to register AURA 4.0 as a REST-based Custom Tool.
- **Azure AI Projects SDK Tool Wrapper:** [integration/foundry_agent.py](file:///d:/hackathon/integration/foundry_agent.py) — Python wrapper script showcasing client-side ToolSet integration via the Azure AI Projects SDK.
- **Microsoft Semantic Kernel Plugin:** [integration/semantic_kernel_plugin.py](file:///d:/hackathon/integration/semantic_kernel_plugin.py) — Implementation of AURA 4.0 APIs as decorated native plugin functions for the Semantic Kernel Python SDK.

