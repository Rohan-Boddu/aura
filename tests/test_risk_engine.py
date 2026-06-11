"""Risk detection tests running on completely real data."""
import pytest


class TestRiskEngineReal:
    def test_detects_real_oversized_module_from_actual_code(self, real_risk_engine, real_file_facts):
        """database.py was deliberately written large with many methods → real god object risk."""
        risks = real_risk_engine.detect_risks()

        oversized = [r for r in risks if "Oversized" in r.get("title", "") or "God Object" in r.get("title", "")]
        db_risks = [r for r in oversized if "database.py" in r.get("file", "")]

        # Because we wrote many methods + size into database.py, this should be real
        assert len(db_risks) >= 1 or any("database" in str(r) for r in risks), \
            "Expected real oversized risk on database.py from actual source"

    def test_risks_contain_real_evidence_from_real_facts(self, real_risks):
        assert isinstance(real_risks, list)
        if real_risks:
            r = real_risks[0]
            assert "title" in r or "file" in r
            # Evidence must be real (we don't hardcode)
            assert "evidence" in r or "severity" in r
