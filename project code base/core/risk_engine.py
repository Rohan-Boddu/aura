import os

class RiskEngine:
    def __init__(self, evidence_engine):
        self.evidence_engine = evidence_engine
        self.scan_result = evidence_engine.scan_result
        self.static_matrix = evidence_engine.static_matrix
        self.file_facts = evidence_engine.file_facts
        self.knowledge = self.scan_result.knowledge if self.scan_result else {}

    def detect_risks(self):
        """Analyzes repository facts and dependencies to identify architecture risks."""
        risks = []

        # 1. Large Controllers / Oversized files
        for path, facts in self.file_facts.items():
            if facts["extension"] == ".py":
                # Check for god object criteria (>30KB or >20 functions)
                if facts["size"] > 30720 or facts["function_count"] > 20:
                    severity = "Critical" if facts["size"] > 80000 else "High"
                    evidence = [
                        f"File size is {round(facts['size'] / 1024.0, 1)} KB (threshold 30 KB)",
                        f"Contains {facts['function_count']} function/method scopes (threshold 20)",
                        f"Contains {facts['class_count']} class declarations"
                    ]
                    risks.append({
                        "title": "Monolithic Controller" if "controller" in path.lower() or "window" in path.lower() else "Oversized Module / God Object",
                        "file": path,
                        "severity": severity,
                        "evidence": {
                            "status": "available",
                            "confidence": 0.95,
                            "evidence_type": "complexity",
                            "evidence": evidence
                        },
                        "confidence": 0.95
                    })

        # 2. Circular Dependencies
        cycles = self._find_import_cycles()
        for cycle in cycles:
            path_str = " -> ".join(cycle)
            risks.append({
                "title": "Circular Dependency Loop",
                "file": cycle[0],
                "severity": "High",
                "evidence": {
                    "status": "available",
                    "confidence": 0.99,
                    "evidence_type": "dependency",
                    "evidence": [
                        f"AST import path forms a dependency loop: {path_str}",
                        "Causes class loader coupling and initialization order fragility"
                    ]
                },
                "confidence": 0.99
            })

        # 3. Deep Dependency Chains
        for path in self.file_facts.keys():
            depth = self._get_dependency_depth(path)
            if depth > 4:
                risks.append({
                    "title": "Deep Dependency Chain",
                    "file": path,
                    "severity": "Medium",
                    "evidence": {
                        "status": "available",
                        "confidence": 0.90,
                        "evidence_type": "dependency",
                        "evidence": [
                            f"Module static import path depth is {depth} levels deep (threshold 4)",
                            "Increases cognitive complexity and regression risk on sibling modifications"
                        ]
                    },
                    "confidence": 0.90
                })

        # 4. Route Concentration
        for path, facts in self.file_facts.items():
            if facts["route_count"] > 5:
                risks.append({
                    "title": "Route Concentration Bottleneck",
                    "file": path,
                    "severity": "High",
                    "evidence": {
                        "status": "available",
                        "confidence": 0.95,
                        "evidence_type": "route",
                        "evidence": [
                            f"Single module serves {facts['route_count']} API endpoints",
                            "Tightly couples routing logic, validation middleware, and data queries"
                        ]
                    },
                    "confidence": 0.95
                })

        # 5. Direct Database Access in Router Views
        for path, facts in self.file_facts.items():
            if facts["route_count"] > 0:
                # Check if this route file imports DB adapters directly or contains query string constants
                ast_info = self.knowledge.get(path, {})
                has_direct_db = False
                db_imports = []
                for cl in ast_info.get("classes", []):
                    for method in cl.get("methods", []):
                        if "cursor" in method.lower() or "execute" in method.lower() or "commit" in method.lower():
                            has_direct_db = True
                
                # Check imports in static_matrix
                deps = self.static_matrix.get(path, [])
                for d in deps:
                    if "database" in d.lower() or "db" in d.lower() or "sql" in d.lower():
                        db_imports.append(d)

                if has_direct_db or len(db_imports) > 1:
                    risks.append({
                        "title": "Direct Database Access in Views",
                        "file": path,
                        "severity": "High",
                        "evidence": {
                            "status": "available",
                            "confidence": 0.88,
                            "evidence_type": "database",
                            "evidence": [
                                f"File handles routes and makes direct database transactions/imports: {', '.join(db_imports) if db_imports else 'cursor commands'}",
                                "Bypasses database repository abstraction patterns"
                            ]
                        },
                        "confidence": 0.88
                    })

        # 6. Missing Tests
        source_files_without_tests = []
        for path, facts in self.file_facts.items():
            if facts["extension"] == ".py" and not "test" in path.lower() and not "setup" in path.lower():
                # Look for corresponding test file
                base_name = os.path.splitext(os.path.basename(path))[0]
                test_exists = False
                for other_path in self.file_facts.keys():
                    if "test" in other_path.lower() and base_name in other_path.lower():
                        test_exists = True
                        break
                if not test_exists and facts["size"] > 1000: # only flag files with actual contents
                    source_files_without_tests.append(path)

        # Cap missing tests risks to top 4 largest files to avoid spamming the report
        source_files_without_tests.sort(key=lambda x: self.file_facts[x]["size"], reverse=True)
        for path in source_files_without_tests[:4]:
            risks.append({
                "title": "Missing Unit Test Coverage",
                "file": path,
                "severity": "Medium",
                "evidence": {
                    "status": "available",
                    "confidence": 0.90,
                    "evidence_type": "test",
                    "evidence": [
                        f"No companion unit test module matched for source file {path}.",
                        "Increases regression vulnerability under downstream refactoring."
                    ]
                },
                "confidence": 0.90
            })

        return risks

    def _find_import_cycles(self):
        """Standard cycle detection DFS script."""
        cycles = []
        visited = {} # 0: unvisited, 1: visiting, 2: visited
        path = []

        def dfs(node):
            visited[node] = 1
            path.append(node)

            for neighbor in self.static_matrix.get(node, []):
                if neighbor not in visited or visited[neighbor] == 0:
                    dfs(neighbor)
                elif visited[neighbor] == 1:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:] + [neighbor])

            path.pop()
            visited[node] = 2

        for node in self.static_matrix.keys():
            if node not in visited:
                dfs(node)
        return cycles

    def _get_dependency_depth(self, start_node):
        """Computes max dependency depth starting from a file."""
        memo = {}
        
        def dfs(node, visiting):
            if node in memo:
                return memo[node]
            if node in visiting:
                return 0 # cycle boundary
            visiting.add(node)
            
            max_d = 0
            for neighbor in self.static_matrix.get(node, []):
                max_d = max(max_d, dfs(neighbor, visiting))
            
            visiting.remove(node)
            memo[node] = 1 + max_d
            return 1 + max_d

        return dfs(start_node, set())
