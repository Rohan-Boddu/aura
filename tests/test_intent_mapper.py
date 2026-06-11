"""Tests using real data from the engines (no mocks)."""
from core.intent_mapper import IntentMapper


class TestIntentMapperReal:
    def test_map_intent_on_real_auth_goal(self):
        mapper = IntentMapper()
        result = mapper.map_intent("Add JWT authentication to the login flow")

        assert result["status"] == "available"
        assert "concepts" in result
        concepts = result["concepts"]
        assert any(c in concepts for c in ["auth", "jwt", "authentication", "login", "token"])

    def test_map_intent_produces_real_confidence(self):
        mapper = IntentMapper()
        result = mapper.map_intent("Improve database query performance in user lookups")
        assert result["status"] == "available"
        assert result["confidence"] > 0.5

    def test_map_target_subsystems_works_with_real_concepts(self):
        mapper = IntentMapper()
        concepts = ["auth", "jwt"]
        # We don't have pre-built subsystems here, but the method should still run
        targets = mapper.map_target_subsystems(concepts)
        assert isinstance(targets, list)
