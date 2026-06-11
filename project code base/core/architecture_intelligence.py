import os
import re
from core.intent_mapper import IntentMapper
from core.evidence_engine import EvidenceEngine
from core.risk_engine import RiskEngine
from core.subsystem_engine import SubsystemEngine

class ArchitectureIntelligence:
    """Orchestrates intent resolution, dependency discovery, risk assessment, and verification mapping for AI coding agents."""

    def __init__(self, session_data):
        self.session_data = session_data or {}
        self.file_facts = self.session_data.get("file_facts", {})
        self.scan_result = self.session_data.get("scan_result")
        self.static_matrix = self.session_data.get("static_matrix", {})
        self.temporal_matrix = self.session_data.get("temporal_matrix", {})
        self.risks_list = self.session_data.get("risks_list", [])
        self.subsystem_assignments = self.session_data.get("subsystem_assignments", {})
        self.subsystem_summary = self.session_data.get("subsystem_summary", [])
        self.confidence = self.session_data.get("confidence", 0.8)
        self.evidence_records = self.session_data.get("evidence_records", [])
        self.is_demo = self.session_data.get("is_demo", False)
        self.repo_path = self.session_data.get("repo_path", "")

    def get_repository_brief(self) -> dict:
        """Provides a concise architectural summary of the repository."""
        if not self.file_facts:
            return {
                "status": "unavailable",
                "reason": "Evidence not available."
            }

        project_type = self.scan_result.project_type if self.scan_result else "Python"
        entry_points = self.scan_result.entry_points if self.scan_result else []
        databases = self.scan_result.database_files if self.scan_result else []

        return {
            "status": "available",
            "project_type": project_type,
            "entry_points": entry_points,
            "major_subsystems": self.subsystem_summary,
            "databases": databases,
            "architectural_risks": self.risks_list,
            "confidence": self.confidence,
            "evidence": self.evidence_records
        }

    def get_agent_context(self, goal: str) -> dict:
        """Generates architecture-aware context for a specific engineering goal."""
        if not self.file_facts or not goal:
            return {
                "status": "unavailable",
                "reason": "Evidence not available."
            }

        # 1. Resolve Intent Concepts
        intent_mapper = IntentMapper()
        intent_res = intent_mapper.map_intent(goal)
        if intent_res.get("status") == "unavailable":
            return {
                "status": "unavailable",
                "reason": "Evidence not available."
            }

        concepts = intent_res.get("concepts", [])
        target_subsystems = intent_mapper.map_target_subsystems(concepts)

        # 2. Score Candidates
        candidate_targets = []
        for file_path, facts in self.file_facts.items():
            subsystem = self.subsystem_assignments.get(file_path, {}).get("subsystem", "Core Runtime Layer")
            score, reasons = intent_mapper.calculate_intent_score(file_path, concepts, subsystem, facts, target_subsystems)
            candidate_targets.append({
                "file": file_path,
                "score": score,
                "reasons": reasons,
                "subsystem": subsystem
            })

        candidate_targets.sort(key=lambda x: x["score"], reverse=True)
        if not candidate_targets or candidate_targets[0]["score"] < 10:
            return {
                "status": "unavailable",
                "reason": "Evidence not available."
            }

        recommended = candidate_targets[0]
        target_file = recommended["file"]

        # 3. Discover Companion Edits
        evidence_eng = EvidenceEngine(
            self.scan_result,
            self.static_matrix,
            self.temporal_matrix,
            self.repo_path,
            is_demo=self.is_demo
        )
        companion_files = evidence_eng.discover_companion_edits(target_file)

        # 4. Filter Associated Risks
        affected_files = [target_file] + [c["file"] for c in companion_files]
        associated_risks = [r for r in self.risks_list if r["file"] in affected_files]

        # 5. Formulate Verification Plan
        verification_checklist = []
        routes = self.scan_result.routes if self.scan_result else []
        affected_routes = []
        for r in routes:
            handler = r.get("handler", "")
            if ":" in handler:
                file_part = handler.split(":")[0]
                if file_part in affected_files:
                    affected_routes.append(r)

        # Identify tests
        test_files = [f for f in self.file_facts.keys() if "test" in f.lower()]
        affected_tests = []
        for f in affected_files:
            base = os.path.splitext(os.path.basename(f))[0]
            for t in test_files:
                if base in t.lower():
                    affected_tests.append(t)

        # Build checklist
        goal_lower = goal.lower()
        if "auth" in goal_lower or "jwt" in goal_lower or "login" in goal_lower:
            verification_checklist.append(f"Assert password hashes are salted and not exposed in `{target_file}`.")
            verification_checklist.append("Verify JWT middleware intercepts unauthorized requests.")
        elif "postgres" in goal_lower or "cosmos" in goal_lower or "database" in goal_lower or "db" in goal_lower:
            verification_checklist.append(f"Verify database connection pool initializes successfully from `{target_file}`.")
            verification_checklist.append("Bench-test partitioned document query latency.")
        else:
            verification_checklist.append(f"Verify static import trees before applying structural changes in `{target_file}`.")

        if affected_tests:
            for t in set(affected_tests):
                verification_checklist.append(f"Run test suite command: `pytest {t}`")
        else:
            verification_checklist.append("Run default regression test suite: `pytest` or `python -m unittest`")

        # Compile evidence reasons
        evidence = [
            {
                "status": "available",
                "confidence": self.confidence,
                "evidence_type": "intent",
                "evidence": [f"Goal matching concepts: {', '.join(concepts[:5])} pointing to target {target_file}."]
            }
        ]

        return {
            "status": "available",
            "goal": goal,
            "recommended_target": {
                "file": target_file,
                "subsystem": recommended["subsystem"],
                "confidence": round(self.confidence * 0.95, 2),
                "reasons": recommended["reasons"]
            },
            "candidate_targets": candidate_targets[:10],
            "subsystems": self.subsystem_summary,
            "companion_files": companion_files,
            "risks": associated_risks,
            "verification": verification_checklist,
            "confidence": self.confidence,
            "evidence": evidence
        }

    def get_change_impact(self, file_path: str) -> dict:
        """Determines the dependency blast radius and risk score of modifying a specific file."""
        if not self.file_facts or not file_path or file_path not in self.file_facts:
            return {
                "status": "unavailable",
                "reason": "Evidence not available."
            }

        # 1. Direct dependencies
        direct = self.static_matrix.get(file_path, [])

        # 2. Reverse dependencies
        reverse = []
        for src, dests in self.static_matrix.items():
            if file_path in dests and src not in reverse:
                reverse.append(src)

        # 3. Co-change dependencies
        cochange = []
        if self.session_data.get("git_evidence"):
            git_ev = self.session_data["git_evidence"]
            cochange_map = git_ev.get("co_change_frequency", {}).get(file_path, {})
            for other, prob in cochange_map.items():
                if prob > 0.0:
                    cochange.append({
                        "file": other,
                        "probability": prob
                    })

        # 4. Subsystem
        subsystem = self.subsystem_assignments.get(file_path, {}).get("subsystem", "Core Runtime Layer")

        # 5. Risk Score calculation
        facts = self.file_facts.get(file_path, {})
        import_cnt = facts.get("import_count", 0)
        imported_by_cnt = facts.get("imported_by_count", 0)
        fn_cnt = facts.get("function_count", 0)
        size = facts.get("size", 0)

        base_score = import_cnt * 4 + imported_by_cnt * 6 + fn_cnt * 2 + (size / 1024.0)
        related_risks = [r for r in self.risks_list if r["file"] == file_path]
        base_score += len(related_risks) * 20

        risk_score = min(int(base_score), 100)
        risk_score = max(risk_score, 10)

        # Compile evidence reasons
        evidence = [
            {
                "status": "available",
                "confidence": self.confidence,
                "evidence_type": "dependency",
                "evidence": [
                    f"File {file_path} imports {len(direct)} modules and is imported by {len(reverse)} modules.",
                    f"Temporal analysis indicates {len(cochange)} git co-change couplings."
                ]
            }
        ]

        return {
            "status": "available",
            "direct_dependencies": direct,
            "reverse_dependencies": reverse,
            "cochange_dependencies": cochange,
            "subsystem": subsystem,
            "risk_score": risk_score,
            "confidence": self.confidence,
            "evidence": evidence
        }

    def get_ownership(self, file_path: str) -> dict:
        """Determines the subsystem owner and related files/routes for a specific file."""
        if not self.file_facts or not file_path or file_path not in self.file_facts:
            return {
                "status": "unavailable",
                "reason": "Evidence not available."
            }

        subsystem = self.subsystem_assignments.get(file_path, {}).get("subsystem", "Core Runtime Layer")

        # Related files in the same subsystem
        related = [f for f, info in self.subsystem_assignments.items() if info["subsystem"] == subsystem and f != file_path]

        # Entry points connected to this subsystem
        entry_points = self.scan_result.entry_points if self.scan_result else []
        connected_entry_points = []
        for ep in entry_points:
            # If entry point is in subsystem or imports files from subsystem
            ep_sub = self.subsystem_assignments.get(ep, {}).get("subsystem", "")
            if ep_sub == subsystem:
                connected_entry_points.append(ep)
            else:
                # check imports
                imports = self.static_matrix.get(ep, [])
                if any(self.subsystem_assignments.get(imp, {}).get("subsystem") == subsystem for imp in imports):
                    connected_entry_points.append(ep)

        # Routes in this subsystem
        routes = self.scan_result.routes if self.scan_result else []
        connected_routes = []
        for r in routes:
            handler = r.get("handler", "")
            if ":" in handler:
                file_part = handler.split(":")[0]
                if file_part == file_path or self.subsystem_assignments.get(file_part, {}).get("subsystem") == subsystem:
                    connected_routes.append(r)

        return {
            "status": "available",
            "subsystem": subsystem,
            "related_files": sorted(related),
            "entry_points": sorted(list(set(connected_entry_points))),
            "routes": connected_routes,
            "confidence": self.confidence
        }
