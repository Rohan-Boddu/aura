import os
from typing import Dict, Any, List

def generate_architecture_explanation(scan_result, file_facts, health_scores, risks, coverages) -> str:
    """Compiles a detailed, evidence-grounded architecture review in markdown."""
    project_path = scan_result.project_path
    project_type = scan_result.project_type
    entry_points = scan_result.entry_points
    database_files = scan_result.database_files
    dependencies = scan_result.dependencies
    routes = scan_result.routes

    lines = [
        f"# AURA System Architecture Review: {os.path.basename(project_path) or 'Workspace'}",
        "",
        "AURA has completed a strict read-only structural analysis of the codebase.",
        "",
        "## 1. Workspace Evidence Coverage Summary",
        f"- **Overall Coverage:** {int(coverages.get('overall_coverage', 0) * 100)}%",
        f"- **AST Parser Coverage:** {int(coverages.get('ast_coverage', 0) * 100)}%",
        f"- **Dependency Resolution:** {int(coverages.get('dependency_coverage', 0) * 100)}%",
        f"- **Git Telemetry Coverage:** " + (f"{int(coverages['git_coverage'] * 100)}%" if coverages.get('git_coverage') is not None else "Not Available (Reason: No readable Git history)"),
        f"- **API Route Resolution:** " + (f"{int(coverages['route_coverage'] * 100)}%" if coverages.get('route_coverage') is not None else "Not Available (Reason: No routes mapped in workspace)"),
        "",
        "## 2. Detected System Profile",
        f"- **Architecture Type:** `{project_type}` Application Layout",
        f"- **Total Files Scanned:** {len(file_facts)}",
        f"- **Entry Points:** {', '.join([f'`{ep}`' for ep in entry_points]) or 'Not Available (Insufficient entry point evidence)'}",
        f"- **Databases Mapped:** {', '.join([f'`{db}`' for db in database_files]) or 'Not Available (Insufficient database evidence)'}",
        f"- **External Libraries:** {', '.join([f'`{d}`' for d in dependencies[:8]]) or 'None detected'}",
        "",
        "## 3. Detected Layers & Service Boundaries",
    ]

    # Dynamically extract packages / sub-directories from file paths
    dirs = set()
    for path in file_facts.keys():
        parts = path.split('/')
        if len(parts) > 1:
            dirs.add(parts[0])

    if dirs:
        lines.append("We have mapped the following functional modules/folders as structural boundaries:")
        for d in sorted(list(dirs)):
            lines.append(f"- **Layer `{d}/`**: Found {sum(1 for f in file_facts if f.startswith(d))} source files.")
    else:
        lines.append("Not Available: The codebase is a flat-hierarchy module layout.")

    lines.extend([
        "",
        "## 4. Repository Architectural Strengths",
    ])
    
    strengths = []
    if len(file_facts) > 10:
        strengths.append("- **Modular Design:** Workspace utilizes separate files for core concerns rather than a single monolith.")
    if coverages.get('ast_coverage', 0) > 0.9:
        strengths.append("- **High AST Parse Success:** 90%+ code files compiled cleanly without syntax issues.")
    if entry_points:
        strengths.append(f"- **Explicit Entrypoints:** Standard main/app hooks mapped: {', '.join(entry_points)}.")
    
    if strengths:
        lines.extend(strengths)
    else:
        lines.append("- Not Available: Insufficient structure to determine strengths.")

    lines.extend([
        "",
        "## 5. Detected Technical Debt & Weaknesses",
    ])

    if risks:
        for r in risks[:5]:
            lines.append(f"- **[{r['severity'].upper()}] {r['title']} in `{r['file']}`**:")
            ev_data = r['evidence']
            evidence_list = []
            if isinstance(ev_data, dict):
                if ev_data.get("status") == "available" and isinstance(ev_data.get("evidence"), list):
                    evidence_list = ev_data["evidence"]
            elif isinstance(ev_data, list):
                evidence_list = ev_data
            
            for e in evidence_list:
                lines.append(f"  - {e}")
    else:
        lines.append("- Not Available: No critical structural bottlenecks or test gaps detected.")

    lines.extend([
        "",
        "## 6. Repository-Specific Refactoring Recommendations",
    ])

    recommendations_count = 0
    for r in risks:
        if r["title"] == "Oversized Module / God Object" or r["title"] == "Monolithic Controller":
            lines.append(f"1. **Deconstruct `{r['file']}`:** Split functions/methods into smaller cohesive sibling modules.")
            recommendations_count += 1
        elif r["title"] == "Circular Dependency Loop":
            lines.append(f"2. **De-couple cycles on `{r['file']}`:** Extract shared variables/classes into a utilities script to resolve circular imports.")
            recommendations_count += 1
        elif r["title"] == "Direct Database Access in Views":
            lines.append(f"3. **Refactor Database Layer in `{r['file']}`:** Encapsulate queries inside database model repository helper views.")
            recommendations_count += 1

    if recommendations_count == 0:
        lines.append("- Not Available: General code looks healthy. Ensure standard unit test assertions cover new features.")

    return "\n".join(lines)


def generate_plan_markdown(plan_data: Dict[str, Any], goal: str) -> str:
    """Creates the change plan markdown package with AURA Agent standard sections."""
    lines = [
        "## AURA Architecture Implementation Plan",
        "",
        "### Summary",
        f"AURA has analyzed the repository and resolved the change targets for the engineering goal: **{goal}**.",
        f"- **Primary Target File:** `{plan_data['mapped_target']}`",
        f"- **Architectural Reasoning:** {plan_data['reasoning']}",
        f"- **Confidence Score:** {int(plan_data['confidence'] * 100)}%",
        "",
        "### Scope of Companion Edits",
    ]

    files = plan_data.get("affected_files", [])
    if files:
        for f in files:
            action = "[MODIFY]"
            lines.append(f"- `{action}` `{f['file']}` (Reason: {f['reason']})")
    else:
        lines.append("- No files mapped for editing. Status: Not Available.")

    # Risk level calculation
    complexity = plan_data.get("complexity", "Low").upper()
    risks = plan_data.get("risks", [])
    risk_level = "LOW"
    if complexity == "HIGH" or len(risks) > 2:
        risk_level = "CRITICAL"
    elif complexity == "MEDIUM" or len(risks) > 0:
        risk_level = "HIGH"

    lines.extend([
        "",
        "### Risk Level",
        f"**{risk_level}** (Determined from system complexity and blast radius)",
        "",
        "### Safety Constraints",
        "- **READ-ONLY DIRECTIVE:** Never write to, modify, or delete files in reference repositories (`D:\\aura`, `D:\\max_got_a_face`).",
        "- Avoid manual structural refactoring without executing regression test pipelines.",
    ])

    # Safety constraints from risks
    if risks:
        for r in risks:
            ev_data = r.get('evidence')
            first_ev = ""
            if isinstance(ev_data, dict):
                if ev_data.get("status") == "available" and isinstance(ev_data.get("evidence"), list) and ev_data["evidence"]:
                    first_ev = ev_data["evidence"][0]
            elif isinstance(ev_data, list) and ev_data:
                first_ev = ev_data[0]
            lines.append(f"- **[CITED RISK]** `{r['file']}`: {r['title']} - {first_ev}")

    lines.extend([
        "",
        "### Recommended Companion Files",
    ])
    
    companion_files = [f['file'] for f in files if f['file'] != plan_data['mapped_target']]
    if companion_files:
        for cf in companion_files:
            lines.append(f"- `{cf}`")
    else:
        lines.append("- None (Change is localized to target file)")

    lines.extend([
        "",
        "### Verification Commands",
    ])
    
    # Generate verification commands based on project type
    target_ext = os.path.splitext(plan_data['mapped_target'])[1]
    if target_ext == ".py":
        lines.extend([
            "Run unit/integration tests to ensure no regressions:",
            "```powershell",
            f"python -m py_compile {plan_data['mapped_target']}",
            "pytest tests/",
            "```"
        ])
    else:
        lines.extend([
            "Compile and run unit tests:",
            "```powershell",
            "npm test",
            "```"
        ])

    lines.extend([
        "",
        "### Human Review Checklist",
    ])
    
    checklist = plan_data.get("verification_checklist", [])
    if checklist:
        for idx, item in enumerate(checklist, 1):
            lines.append(f"{idx}. `[ ]` {item}")
    else:
        lines.append("1. `[ ]` Verify application starts successfully after edits.")

    return "\n".join(lines)

