import os

class SubsystemEngine:
    """Groups codebase files into engineering subsystems and clusters dependencies."""

    SUBSYSTEM_DEFS = {
        "IDE Layer": {
            "description": "Integrated Development Environment widgets, sidebar components, and editor modules.",
            "keywords": ["max_ide", "void", "mde", "editor", "code_analyzer"]
        },
        "UI Layer": {
            "description": "User Interface rendering layouts, windows, desktop icons, panels, and CSS styles.",
            "keywords": ["static", "css", "html", "js", "panel", "window", "overlay", "view", "mr_r_", "ui"]
        },
        "Voice Layer": {
            "description": "Speech-to-text, text-to-speech, and audio playback drivers.",
            "keywords": ["tts", "stt", "voice", "speech", "audio", "sound", "sounddevice", "listener", "listening"]
        },
        "Research Layer": {
            "description": "System diagnostics, lab worksheets, and research workspace templates.",
            "keywords": ["research", "diagnostic", "lab"]
        },
        "Database Layer": {
            "description": "Database adapters, schemas, models, SQL engines, and local stores.",
            "keywords": ["db", "database", "sql", "postgres", "cosmos", "repository", "model", "orm", "storage", "query"]
        },
        "Authentication Layer": {
            "description": "User credential stores, sessions, JWT token interceptors, and password cryptography.",
            "keywords": ["auth", "login", "jwt", "session", "credential", "security", "secrets", "password"]
        },
        "Scheduling Layer": {
            "description": "Background task schedulers, timers, and automatic cron alert triggers.",
            "keywords": ["scheduler", "alarm", "cron", "timer", "schedule"]
        },
        "LLM Layer": {
            "description": "AI prompts, OpenAI/LMStudio client bridges, token optimizers, and command classifiers.",
            "keywords": ["llm", "gpt", "openai", "claude", "prompt", "ai_command", "predictor", "learner", "agent", "intelligence"]
        },
        "Core Runtime Layer": {
            "description": "Global application entry points, process handlers, utility libs, and environment loaders.",
            "keywords": []
        }
    }

    def __init__(self, file_facts, static_matrix, scan_result):
        self.file_facts = file_facts or {}
        self.static_matrix = static_matrix or {}
        self.scan_result = scan_result
        self.reverse_deps = {}
        for src, dests in self.static_matrix.items():
            for dest in dests:
                self.reverse_deps.setdefault(dest, []).append(src)

        # 1. Base classification using heuristics
        self.file_assignments = self._classify_heuristically()

        # 2. Refine assignments using dependency clustering propagation
        self._refine_via_clustering()

    def _classify_heuristically(self):
        assignments = {}
        database_files = self.scan_result.database_files if self.scan_result else []
        routes = self.scan_result.routes if self.scan_result else []
        route_handlers = {r["handler"].split(":")[0] for r in routes if ":" in r.get("handler", "")}

        for path, facts in self.file_facts.items():
            scores = {name: 0 for name in self.SUBSYSTEM_DEFS}
            path_lower = path.lower()
            name_lower = os.path.basename(path).lower()
            ext_lower = os.path.splitext(path)[1].lower()

            # Rule 1: check path folder matching
            if "static/tools/max_ide" in path_lower or "void-main" in path_lower:
                scores["IDE Layer"] += 12
            elif "static/" in path_lower or "templates/" in path_lower:
                scores["UI Layer"] += 8
            elif "stt/" in path_lower or "tts/" in path_lower:
                scores["Voice Layer"] += 8
            elif "research_lab" in path_lower:
                scores["Research Layer"] += 8

            # Rule 2: keyword matching
            for subsystem, defs in self.SUBSYSTEM_DEFS.items():
                if subsystem == "Core Runtime Layer":
                    continue
                for kw in defs["keywords"]:
                    if kw in name_lower:
                        scores[subsystem] += 6
                    elif kw in path_lower:
                        scores[subsystem] += 3

            # Rule 3: extensions
            if ext_lower in (".tsx", ".jsx"):
                if "max_ide" in path_lower or "void" in path_lower:
                    scores["IDE Layer"] += 6
                else:
                    scores["UI Layer"] += 5
            elif ext_lower in (".css", ".html"):
                scores["UI Layer"] += 6

            # Rule 4: DB ownership
            if path in database_files:
                scores["Database Layer"] += 12

            # Rule 5: Route handlers
            if path in route_handlers:
                # Route handlers in web apps are usually UI-facing controllers or core APIs
                scores["UI Layer"] += 3

            # Pick highest score
            best_subsystem = "Core Runtime Layer"
            best_score = 0
            for subsystem, score in scores.items():
                if score > best_score:
                    best_score = score
                    best_subsystem = subsystem

            assignments[path] = {
                "subsystem": best_subsystem,
                "score": best_score
            }

        return assignments

    def _refine_via_clustering(self):
        """Propagates subsystems down the import tree to cluster weakly classified files."""
        for _ in range(2): # run twice to propagate transitions
            for path in list(self.file_facts.keys()):
                curr = self.file_assignments.get(path, {"subsystem": "Core Runtime Layer", "score": 0})
                
                # Refine if assigned to fallback Core Layer or has very weak heuristic score (< 4)
                if curr["subsystem"] == "Core Runtime Layer" or curr["score"] < 4:
                    neighbors = []
                    # Get imports
                    neighbors.extend(self.static_matrix.get(path, []))
                    # Get imported by
                    neighbors.extend(self.reverse_deps.get(path, []))

                    # Count neighbor subsystems
                    counts = {}
                    for n in neighbors:
                        if n in self.file_assignments:
                            sub = self.file_assignments[n]["subsystem"]
                            if sub != "Core Runtime Layer":
                                counts[sub] = counts.get(sub, 0) + 1

                    if counts:
                        # Find majority subsystem
                        majority = max(counts, key=counts.get)
                        # Re-assign if neighbor support is strong
                        if counts[majority] >= 2 or len(neighbors) == 1:
                            self.file_assignments[path] = {
                                "subsystem": majority,
                                "score": 4 # marked as propagated
                            }

    def get_subsystem_files(self):
        sub_files = {name: [] for name in self.SUBSYSTEM_DEFS}
        for path, info in self.file_assignments.items():
            sub_files[info["subsystem"]].append(path)
        return sub_files

    def get_subsystem_summary(self):
        summary = []
        sub_files = self.get_subsystem_files()
        
        # Calculate dynamic confidence for subsystem resolution based on coverage
        total_files = len(self.file_assignments)
        
        for name, files in sub_files.items():
            if not files:
                continue
            
            # Subsystem confidence is determined by ratio of files assigned with positive score
            scored_files = sum(1 for f in files if self.file_assignments[f]["score"] > 0)
            conf = round(scored_files / len(files), 2) if files else 0.5
            conf = max(min(conf, 0.98), 0.6)

            summary.append({
                "name": name,
                "description": self.SUBSYSTEM_DEFS[name]["description"],
                "files": sorted(files),
                "confidence": conf
            })
        return sorted(summary, key=lambda x: len(x["files"]), reverse=True)
