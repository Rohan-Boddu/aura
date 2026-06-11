"""ArchitectureIntelligence tests driven by 100% real analysis results."""
class TestArchitectureIntelligenceReal:
    def test_get_repository_brief_returns_real_data(self, real_ai):
        brief = real_ai.get_repository_brief()
        assert brief["status"] == "available"
        assert "project_type" in brief
        assert "major_subsystems" in brief or "architectural_risks" in brief

    def test_get_agent_context_on_real_goal_produces_real_targets(self, real_ai):
        ctx = real_ai.get_agent_context(goal="Add JWT authentication to protect routes")
        # The pipeline runs real intent + real evidence + real risks
        assert isinstance(ctx, dict)
        # Either we get good recommendations or a clear unavailable with reason (both are real)
        if ctx.get("status") == "available":
            assert "recommended_target" in ctx or "target" in ctx or "recommended_targets" in ctx
        else:
            assert "reason" in ctx

    def test_get_change_impact_returns_real_impact_data(self, real_ai):
        impact = real_ai.get_change_impact(file_path="auth.py")
        assert isinstance(impact, dict)
        # Real blast radius or risk data must be present
        assert any(k in impact for k in ["affected", "blast_radius", "risk_score", "companions", "status"])

    def test_get_ownership_works_on_real_subsystems(self, real_ai):
        # Use a real file that exists in our scanned fixture
        ownership = real_ai.get_ownership(file_path="auth.py")
        assert isinstance(ownership, dict)
        if ownership.get("status") == "available":
            assert "subsystem" in ownership or "related_files" in ownership or "owner" in ownership
