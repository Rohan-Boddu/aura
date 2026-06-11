# project code base/blast_radius_engine.py
import json
import os


def load_matrix(file_name):
    """Loads a JSON matrix safely if it exists."""
    if not os.path.exists(file_name):
        return {}
    with open(file_name, "r") as f:
        return json.load(f)


def calculate_blast_radius(target_file, static_graph, temporal_matrix, w_s=0.4, w_t=0.6):
    """Fuses static and temporal metrics to trace downstream impact."""
    impacted_nodes = {}
    
    # 1. Evaluate Direct Static Dependencies
    static_deps = static_graph.get(target_file, [])
    for dep in static_deps:
        if dep not in impacted_nodes:
            impacted_nodes[dep] = {"static_score": 1.0, "temporal_score": 0.0, "reason": "Direct Import"}

    # 2. Evaluate Temporal/Logical Co-Changes
    temporal_deps = temporal_matrix.get(target_file, {})
    for dep, probability in temporal_deps.items():
        if dep in impacted_nodes:
            impacted_nodes[dep]["temporal_score"] = probability
            if probability > 0.7:
                impacted_nodes[dep]["reason"] = "Tight Coupler (Import & Git)"
        else:
            # Capturing the 'Shadow Dependencies' (Not explicitly imported, but historically linked)
            impacted_nodes[dep] = {"static_score": 0.0, "temporal_score": probability, "reason": "Shadow Coupling (Git History)"}

    # 3. Compute Composite Impact Score per Node and System Aggregates
    total_impact_accumulator = 0
    detailed_report = []

    for node, metrics in impacted_nodes.items():
        # Formula: Weighted sum of static link and temporal history probability
        composite_score = (metrics["static_score"] * w_s) + (metrics["temporal_score"] * w_t)
        normalized_score = min(int(composite_score * 100), 100)
        total_impact_accumulator += normalized_score
        
        detailed_report.append({
            "file": node,
            "impact_weight": normalized_score,
            "relationship": metrics["reason"]
        })

    # Calculate Global System Impact (0 - 100 scale based on scope)
    num_affected = len(impacted_nodes)
    if num_affected == 0:
        system_impact_score = 0
    else:
        system_impact_score = min(int((total_impact_accumulator / num_affected) * (1 + (num_affected * 0.05))), 100)

    return {
        "target_simulated": target_file,
        "global_impact_score": system_impact_score,
        "total_modules_affected": num_affected,
        "affected_nodes": sorted(detailed_report, key=lambda x: x["impact_weight"], reverse=True)
    }


if __name__ == "__main__":
    print("[*] Fusing Data Matrices to Calculate Blast Radius Metrics...")
    
    # Load inputs generated from Day 1 & Day 2 scripts
    static_data = load_matrix("ast_static_matrix.json")
    temporal_data = load_matrix("chronos_git_matrix.json")
    
    # Simulate a user targeting "auth.py" for modification
    test_target = "auth.py"
    
    if not static_data or not temporal_data:
        print("[!] Missing source matrices. Creating fallback live calculations...")
        # Self-contained fallback simulation if standalone run occurs
        static_data = {"auth.py": ["database.py", "jwt.py"], "database.py": ["user_repo.py"]}
        temporal_data = {"auth.py": {"billing.py": 0.82, "session.py": 0.64, "jwt.py": 0.95}}

    analysis_payload = calculate_blast_radius(test_target, static_data, temporal_data)
    
    print("\n[+] SUCCESS: Blast Radius Calculations Generated Successfully:\n")
    print(json.dumps(analysis_payload, indent=2))
    
    with open("blast_radius_payload.json", "w") as f:
        json.dump(analysis_payload, f, indent=2)
