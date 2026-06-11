"""
AURA 4.0 — Semantic Kernel Python Plugin

This module illustrates how to register the AURA 4.0 Architecture Intelligence Layer
as a native plugin inside the Microsoft Semantic Kernel Python SDK.

Prerequisites:
    pip install semantic-kernel requests

Usage:
    Import the AuraPlugin class and register it using:
    kernel.add_plugin(plugin=AuraPlugin(), plugin_name="AuraPlugin")
"""

import os
import json
import requests
from semantic_kernel.functions.kernel_function_decorator import kernel_function

AURA_SERVER_URL = os.environ.get("AURA_SERVER_URL", "http://localhost:5000")

class AuraPlugin:
    """
    Semantic Kernel Plugin exposing AURA 4.0 Architecture Intelligence APIs to LLMs.
    """

    @kernel_function(
        name="get_repository_brief",
        description="Fetch a high-level summary of the repository including entry points, languages, active databases, subsystems, and confidence metrics."
    )
    def get_repository_brief(self, analysis_id: str) -> str:
        """
        Retrieves high-level summary metadata of a scanned workspace.
        """
        try:
            url = f"{AURA_SERVER_URL}/api/repository_brief/{analysis_id}"
            response = requests.get(url, timeout=10)
            return json.dumps(response.json())
        except Exception as e:
            return json.dumps({"status": "unavailable", "reason": f"Connection error: {str(e)}"})

    @kernel_function(
        name="get_agent_context",
        description="Fetch goal-aware target recommendations, companion edit files, and verification checklists for a specific coding goal."
    )
    def get_agent_context(self, analysis_id: str, goal: str) -> str:
        """
        Retrieves recommended files to edit and tests to run for a goal.
        """
        try:
            url = f"{AURA_SERVER_URL}/api/agent_context/{analysis_id}"
            response = requests.post(url, json={"goal": goal}, timeout=10)
            return json.dumps(response.json())
        except Exception as e:
            return json.dumps({"status": "unavailable", "reason": f"Connection error: {str(e)}"})

    @kernel_function(
        name="get_change_impact",
        description="Assess the blast radius and risk score of modifying a specific file, derived from static imports and temporal Git co-change frequency."
    )
    def get_change_impact(self, analysis_id: str, file_path: str) -> str:
        """
        Retrieves dependencies and blast radius metrics for a file.
        """
        try:
            url = f"{AURA_SERVER_URL}/api/change_impact/{analysis_id}"
            response = requests.post(url, json={"file": file_path}, timeout=10)
            return json.dumps(response.json())
        except Exception as e:
            return json.dumps({"status": "unavailable", "reason": f"Connection error: {str(e)}"})

    @kernel_function(
        name="get_ownership",
        description="Resolve ownership subsystems, entry points, and related REST endpoint routes associated with a file."
    )
    def get_ownership(self, analysis_id: str, file_path: str) -> str:
        """
        Retrieves routes and subsystems mapped to a file.
        """
        try:
            url = f"{AURA_SERVER_URL}/api/ownership/{analysis_id}"
            response = requests.post(url, json={"file": file_path}, timeout=10)
            return json.dumps(response.json())
        except Exception as e:
            return json.dumps({"status": "unavailable", "reason": f"Connection error: {str(e)}"})
