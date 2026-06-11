import re
import os

class IntentMapper:
    """Translates engineering goals into repository concepts and target subsystems."""

    CONCEPT_MAP = {
        "jwt": ["auth", "jwt", "login", "token", "middleware", "identity", "session", "authentication", "authorization"],
        "auth": ["auth", "jwt", "login", "token", "middleware", "identity", "session", "authentication", "authorization"],
        "login": ["auth", "jwt", "login", "token", "middleware", "identity", "session", "authentication", "authorization"],
        "authentication": ["auth", "jwt", "login", "token", "middleware", "identity", "session", "authentication", "authorization"],
        
        "ui": ["ui", "frontend", "react", "tsx", "editor", "sidebar", "settings", "theme", "max ide", "widgets"],
        "frontend": ["ui", "frontend", "react", "tsx", "editor", "sidebar", "settings", "theme", "max ide", "widgets"],
        "ide": ["ui", "frontend", "react", "tsx", "editor", "sidebar", "settings", "theme", "max ide", "widgets"],
        "editor": ["ui", "frontend", "react", "tsx", "editor", "sidebar", "settings", "theme", "max ide", "widgets"],
        "sidebar": ["ui", "frontend", "react", "tsx", "editor", "sidebar", "settings", "theme", "max ide", "widgets"],
        
        "postgres": ["database", "postgres", "sql", "repository", "orm", "storage", "query", "cosmos"],
        "postgresql": ["database", "postgres", "sql", "repository", "orm", "storage", "query", "cosmos"],
        "cosmos": ["database", "postgres", "sql", "repository", "orm", "storage", "query", "cosmos"],
        "database": ["database", "postgres", "sql", "repository", "orm", "storage", "query", "cosmos"],
        "db": ["database", "postgres", "sql", "repository", "orm", "storage", "query", "cosmos"],
        
        "microservice": ["user", "service", "api", "boundary", "database", "repository", "authentication", "microservice"],
        "split": ["user", "service", "api", "boundary", "database", "repository", "authentication", "microservice"]
    }

    def __init__(self):
        pass

    def map_intent(self, goal: str) -> dict:
        if not goal:
            return {
                "status": "unavailable",
                "reason": "Goal prompt is empty."
            }

        goal_lower = goal.lower()
        concepts = set()

        # Match predefined maps
        for keyword, mapped_concepts in self.CONCEPT_MAP.items():
            if keyword in goal_lower:
                concepts.update(mapped_concepts)

        # Extract words from the prompt
        words = re.findall(r'\b\w+\b', goal_lower)
        stopwords = {"add", "change", "replace", "with", "into", "a", "an", "the", "to", "for", "in", "of", "on", "and", "or"}
        for word in words:
            if word not in stopwords and len(word) > 1:
                concepts.add(word)

        if not concepts:
            return {
                "status": "unavailable",
                "reason": f"No matching intent concepts resolved for goal: '{goal}'"
            }

        # Calculate a reasonable dynamic confidence
        direct_matches = sum(1 for kw in self.CONCEPT_MAP if kw in goal_lower)
        confidence = min(0.70 + (direct_matches * 0.08), 0.98)

        return {
            "status": "available",
            "confidence": round(confidence, 2),
            "concepts": sorted(list(concepts))
        }

    def map_target_subsystems(self, concepts: list) -> list:
        targets = []
        concept_set = set(concepts)
        if concept_set & {"ui", "frontend", "react", "tsx", "editor", "sidebar", "settings", "theme", "max ide", "widgets"}:
            targets.extend(["IDE Layer", "UI Layer"])
        if concept_set & {"auth", "jwt", "login", "token", "middleware", "identity", "session", "authentication", "authorization"}:
            targets.append("Authentication Layer")
        if concept_set & {"database", "postgres", "sql", "repository", "orm", "storage", "query", "cosmos"}:
            targets.append("Database Layer")
        if concept_set & {"tts", "stt", "voice", "speech", "audio", "sound", "sounddevice", "listener", "listening"}:
            targets.append("Voice Layer")
        if concept_set & {"scheduler", "cron", "alarm", "timer", "schedule"}:
            targets.append("Scheduling Layer")
        if concept_set & {"llm", "gpt", "openai", "claude", "prompt", "ai_command", "predictor", "learner", "agent", "intelligence"}:
            targets.append("LLM Layer")
        if concept_set & {"research", "diagnostic", "lab"}:
            targets.append("Research Layer")
        return targets if targets else ["Core Runtime Layer"]

    def calculate_intent_score(self, file_path: str, concepts: list, subsystem: str, file_fact: dict, target_subsystems: list) -> tuple:
        """Computes the Intent Match Score for a file based on concepts, subsystems, and metrics."""
        path_relevance = 0.0
        keyword_relevance = 0.0
        dependency_relevance = 0.0
        subsystem_relevance = 0.0
        responsibility_score = 0.0

        path_lower = file_path.lower()
        name_lower = os.path.basename(file_path).lower()
        concepts_matched = [c for c in concepts if c in path_lower or c in name_lower]

        if concepts:
            # 1. Path Relevance (max 25)
            path_matches = sum(1 for c in concepts if c in path_lower)
            path_relevance = min(25.0, 25.0 * (path_matches / max(1, len(concepts) - 2)))
            if "max_ide" in path_lower or "void-main" in path_lower:
                if any(c in ["ui", "editor", "ide", "sidebar"] for c in concepts):
                    path_relevance = max(path_relevance, 22.0)

            # 2. Keyword Relevance (max 25)
            keyword_matches = sum(1 for c in concepts if c in name_lower)
            keyword_relevance = min(25.0, 25.0 * (keyword_matches / max(1, len(concepts) - 4)))

            # 3. Subsystem Relevance (max 20)
            if subsystem in target_subsystems:
                subsystem_relevance = 20.0

            # 4. Dependency Relevance (max 20)
            imports_count = file_fact.get("import_count", 0)
            imported_by_count = file_fact.get("imported_by_count", 0)
            if imports_count > 0 or imported_by_count > 0:
                dependency_relevance = 15.0
                if subsystem in target_subsystems:
                    dependency_relevance += 5.0
            
            # 5. File Responsibility Score (max 10)
            fn_cnt = file_fact.get("function_count", 0)
            class_cnt = file_fact.get("class_count", 0)
            responsibility_score = 10.0 * (min(fn_cnt + class_cnt * 2 + imported_by_count, 15) / 15.0)

        total_score = int(path_relevance + keyword_relevance + dependency_relevance + subsystem_relevance + responsibility_score)
        total_score = max(min(total_score, 100), 5)

        # Generate reasons
        reasons = []
        if subsystem_relevance > 0:
            reasons.append(f"Located inside {subsystem}")
        if ext := os.path.splitext(file_path)[1]:
            if ext in (".tsx", ".jsx"):
                reasons.append("React TSX component")
            elif ext == ".py":
                reasons.append("Python module")
        if any(c in name_lower for c in ["ui", "panel", "window", "view", "sidebar", "widget"]):
            reasons.append("Contains UI rendering logic")
        if file_fact.get("imported_by_count", 0) > 2:
            reasons.append("Referenced by core system components")
        
        # Add dynamic reasoning from matched concepts
        if concepts_matched:
            reasons.append(f"Matches intent concepts: {', '.join(concepts_matched[:3])}")

        if not reasons:
            reasons.append("File path matched concepts in goal request.")

        return total_score, reasons
