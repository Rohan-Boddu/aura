#!/usr/bin/env python3
"""
WhatIf AI - Day 4: Prompt Layer & Keyword Mapper
Translates natural language user intents into target codebase seeds,
integrates with the Day 3 Blast Radius Engine, and formats the output 
for frontend consumption. Includes an interactive shell loop.
"""

import json
import os
import sys
import re

# Import the fusion logic from Day 3
try:
    from blast_radius_engine import calculate_blast_radius, load_matrix
except ImportError:
    # Fallback definitions if run in isolation
    def load_matrix(file_name):
        if not os.path.exists(file_name):
            return {}
        with open(file_name, "r") as f:
            return json.load(f)

    def calculate_blast_radius(target_file, static_graph, temporal_matrix, w_s=0.4, w_t=0.6):
        # Simplistic fallback placeholder
        return {
            "target_simulated": target_file,
            "global_impact_score": 50,
            "total_modules_affected": 1,
            "affected_nodes": [{"file": "unknown.py", "impact_weight": 50, "relationship": "Fallback"}]
        }

# Streamlined keyword translation matrix mapping user intents to target file seeds
CHANGE_MAP = {
    "database": "database.py",
    "postgres": "database.py",
    "postgresql": "database.py",
    "db": "database.py",
    "cosmos": "database.py",
    "cosmosdb": "database.py",
    
    "auth": "auth.py",
    "authentication": "auth.py",
    "login": "auth.py",
    "entra": "auth.py",
    "entraid": "auth.py",
    
    "jwt": "jwt.py",
    "token": "jwt.py",
    
    "billing": "billing.py",
    "payment": "billing.py",
    "stripe": "billing.py",
    
    "redis": "redis_cache.py",
    "cache": "redis_cache.py",
    
    "session": "session.py",
    
    "user": "user_repo.py",
    "user_repo": "user_repo.py",
    
    "utils": "utils.py",
    "logger": "utils.py"
}


def map_prompt_to_target(prompt_text):
    """
    Scans the input prompt for keywords defined in CHANGE_MAP.
    Returns the target filename if matched, otherwise None.
    """
    # Clean and tokenize input prompt
    normalized = re.sub(r'[^\w\s]', '', prompt_text.lower())
    words = normalized.split()
    
    # Check for direct keyword matches
    for word in words:
        if word in CHANGE_MAP:
            return CHANGE_MAP[word]
            
    # Substring fallback search (e.g. "entra-id" or "postgresql")
    for keyword, target in CHANGE_MAP.items():
        if keyword in normalized:
            return target
            
    return None


def save_simulation_js(report):
    """Writes the report as a JS file to both the current and parent directories for UI integration."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    js_content = f"const SIMULATION_DATA = {json.dumps(report, indent=2)};"
    
    # Target parent directory where dashboard_mockup.html is hosted
    parent_dir = os.path.dirname(base_dir)
    js_path_parent = os.path.join(parent_dir, "simulation_data.js")
    js_path_local = os.path.join(base_dir, "simulation_data.js")
    
    try:
        with open(js_path_parent, 'w', encoding='utf-8') as f:
            f.write(js_content)
        with open(js_path_local, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"[+] Telemetry exported to: {js_path_parent}")
    except Exception as e:
        print(f"[-] Failed to export UI telemetry: {e}", file=sys.stderr)


def execute_simulation(prompt_text, static_data, temporal_data):
    """
    Maps prompt to target, computes blast radius, and packages simulation payload.
    """
    target_file = map_prompt_to_target(prompt_text)
    
    if not target_file:
        return {
            "error": "No matching target file identified for the prompt.",
            "prompt_received": prompt_text,
            "suggestions": sorted(list(set(CHANGE_MAP.values())))
        }
        
    # Run the Day 3 fusion calculator
    blast_radius_payload = calculate_blast_radius(target_file, static_data, temporal_data)
    
    # Package into a structured frontend-ready simulation report
    report = {
        "user_query": prompt_text,
        "mapped_target": target_file,
        "simulation_timestamp": "2026-06-09T13:08:00Z", # Standardized demo time
        "metrics": {
            "global_impact_score": blast_radius_payload["global_impact_score"],
            "total_modules_affected": blast_radius_payload["total_modules_affected"],
            "risk_level": "CRITICAL" if blast_radius_payload["global_impact_score"] > 70 else 
                          "HIGH" if blast_radius_payload["global_impact_score"] > 40 else "MEDIUM"
        },
        "affected_nodes": blast_radius_payload["affected_nodes"]
    }
    
    # Day 5 option 1: Export telemetry to UI
    save_simulation_js(report)
    
    return report


def interactive_shell(static_data, temporal_data):
    """
    Runs a shell loop waiting for user prompt input queries.
    """
    print("=========================================================")
    print("        WhatIf AI: Chronos Prompt Mapping Shell v1.0     ")
    print("=========================================================")
    print("Type your change simulation prompt below (e.g. 'Remove Redis')")
    print("Type 'exit' or 'quit' to terminate the shell.")
    print("Available seed keywords: redis, postgres, auth, billing, jwt, user\n")
    
    while True:
        try:
            prompt = input("WhatIf prompt > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ['exit', 'quit']:
                print("[*] Exiting WhatIf Shell.")
                break
                
            report = execute_simulation(prompt, static_data, temporal_data)
            print("\nSimulation Report Matrix:")
            print(json.dumps(report, indent=2))
            print("-" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n[*] Exiting WhatIf Shell.")
            break
        except Exception as e:
            print(f"[-] Error processing query: {e}\n")


def main():
    # Load matrices (expecting them in same directory as script)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_data = load_matrix(os.path.join(base_dir, "ast_static_matrix.json"))
    temporal_data = load_matrix(os.path.join(base_dir, "chronos_git_matrix.json"))
    
    if not static_data or not temporal_data:
        print("[!] Warning: Missing matrix files in execution path. Loading in-memory demo data...")
        # Local mock fallback to make execution self-contained
        static_data = {
            "main.py": ["auth.py", "database.py", "billing.py"],
            "auth.py": ["database.py", "jwt.py", "utils.py"],
            "billing.py": ["database.py", "redis_cache.py", "utils.py"],
            "jwt.py": [],
            "database.py": [],
            "redis_cache.py": [],
            "utils.py": []
        }
        temporal_data = {
            "database.py": {"jwt.py": 0.33, "auth.py": 0.33, "user_repo.py": 0.67},
            "auth.py": {"database.py": 0.25, "jwt.py": 0.25, "billing.py": 0.5, "cache.py": 0.25},
            "billing.py": {"user_repo.py": 0.5, "auth.py": 0.5, "payment_gateway.py": 0.5},
            "redis_cache.py": {"billing.py": 0.45}
        }

    # If prompt passed as command line argument, process it directly and output JSON
    if len(sys.argv) > 1:
        single_prompt = " ".join(sys.argv[1:])
        # Check if the user specified "--simulate"
        if single_prompt.startswith("--"):
            # Skip if standard arg flags are passed, and fallback to interactive
            interactive_shell(static_data, temporal_data)
        else:
            report = execute_simulation(single_prompt, static_data, temporal_data)
            print(json.dumps(report, indent=2))
    else:
        # Launch interactive command prompt loop
        interactive_shell(static_data, temporal_data)


if __name__ == "__main__":
    main()
