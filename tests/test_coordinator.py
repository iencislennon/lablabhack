from backend.band.coordinator import BandCoordinator
from backend.schemas import (
    EnergyPayload, FarmerPayload, LogisticsPayload, MarketPayload,
    PriceRecommendation, RegulatorPayload, SubsidyPlan,
)


def farmer(deficit=10.0):
    return FarmerPayload(crop_forecast=[], risk_flags=[], deficit_regions=[],
                         deficit_pct=deficit, climate_risk_score=0.4)


def logistics(risk=0.5):
    return LogisticsPayload(route_plan=[], loss_estimate_pct=5, bottlenecks=[],
                            storage_capacity_available_tons=100, logistics_risk_score=risk)


def energy(alert="none"):
    return EnergyPayload(energy_price_usd_kwh=0.1, energy_price_trend="stable", grid_load_pct=50,
                         shortage_alert=alert, renewable_share_pct=20,
                         impact_on_food_production="none", energy_risk_score=0.2)


def market(stock_days=30, cut_price=False, speculation=False):
    recs = [PriceRecommendation(commodity="wheat", current_price_usd=100,
                                recommended_price_usd=90 if cut_price else 110, rationale="x")]
    return MarketPayload(price_recommendations=recs, demand_signal="normal", demand_trend="stable",
                         stock_level_days=stock_days, inflation_risk="low",
                         speculation_detected=speculation, market_risk_score=0.3)


def regulator(reserves=False, subsidies=False):
    plan = [SubsidyPlan(target="wheat_farmers", amount_usd_million=1, duration_months=3, rationale="x")] if subsidies else []
    return RegulatorPayload(policy_recommendation="p", subsidy_plan=plan, import_trigger=False,
                            price_controls=False, emergency_reserves_release=reserves,
                            confidence_score=0.8, escalate_to_human=False)


def test_no_conflicts_when_signals_agree():
    c = BandCoordinator()
    c.receive("farmer", farmer(10)); c.receive("logistics", logistics(0.5))
    c.receive("energy", energy("none")); c.receive("market", market())
    assert c.detect_conflicts() == []


def test_farmer_deficit_vs_low_logistics_risk():
    c = BandCoordinator()
    c.receive("farmer", farmer(35)); c.receive("logistics", logistics(0.1))
    assert len(c.detect_conflicts()) == 1


def test_price_cut_during_critical_stock():
    c = BandCoordinator()
    c.receive("market", market(stock_days=7, cut_price=True))
    conflicts = c.detect_conflicts()
    assert len(conflicts) == 1 and "wheat" in conflicts[0]


def test_critical_energy_without_reserve_release():
    c = BandCoordinator()
    c.receive("energy", energy("critical")); c.receive("regulator", regulator(reserves=False))
    assert len(c.detect_conflicts()) == 1


def test_speculation_with_subsidies():
    c = BandCoordinator()
    c.receive("market", market(speculation=True)); c.receive("regulator", regulator(subsidies=True))
    assert len(c.detect_conflicts()) == 1


def test_thresholds_are_strict():
    c = BandCoordinator()
    c.receive("farmer", farmer(30)); c.receive("logistics", logistics(0.3))
    c.receive("market", market(stock_days=14, cut_price=True))
    assert c.detect_conflicts() == []


def test_ready_only_when_four_agents_published():
    c = BandCoordinator()
    c.receive("farmer", farmer()); c.receive("logistics", logistics()); c.receive("energy", energy())
    assert not c.is_ready_for_regulator()
    c.receive("market", market())
    assert c.is_ready_for_regulator()


def test_audit_trail_records_every_publication():
    c = BandCoordinator()
    c.receive("farmer", farmer()); c.receive("energy", energy())
    report = c.generate_audit_report()
    assert [e["agent"] for e in report["audit_trail"]] == ["farmer", "energy"]
    assert report["final_decision"] is None and report["escalated"] is False
