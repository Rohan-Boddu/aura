const SIMULATION_DATA = {
  "user_query": "what if we swap custom auth",
  "mapped_target": "auth.py",
  "simulation_timestamp": "2026-06-09T13:08:00Z",
  "metrics": {
    "global_impact_score": 43,
    "total_modules_affected": 7,
    "risk_level": "HIGH"
  },
  "affected_nodes": [
    {
      "file": "database.py",
      "impact_weight": 55,
      "relationship": "Direct Import"
    },
    {
      "file": "jwt.py",
      "impact_weight": 55,
      "relationship": "Direct Import"
    },
    {
      "file": "utils.py",
      "impact_weight": 40,
      "relationship": "Direct Import"
    },
    {
      "file": "billing.py",
      "impact_weight": 30,
      "relationship": "Shadow Coupling (Git History)"
    },
    {
      "file": "user_repo.py",
      "impact_weight": 15,
      "relationship": "Shadow Coupling (Git History)"
    },
    {
      "file": "cache.py",
      "impact_weight": 15,
      "relationship": "Shadow Coupling (Git History)"
    },
    {
      "file": "session.py",
      "impact_weight": 15,
      "relationship": "Shadow Coupling (Git History)"
    }
  ]
};