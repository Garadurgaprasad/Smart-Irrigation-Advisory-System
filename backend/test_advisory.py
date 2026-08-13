"""
test_advisory.py — Unit Tests for Advisory Engine & Analytics
═════════════════════════════════════════════════════════════
Run with: python -m pytest test_advisory.py -v
"""

import pytest
import pandas as pd
from advisory_engine import get_recommendation, lookup_crop_rule, evaluate_batch
from analytics import compute_water_usage_trend, compute_adherence, compute_moisture_trend


# ═══════════════════════════════════════════════════════════════════════
# ADVISORY ENGINE TESTS
# ═══════════════════════════════════════════════════════════════════════

class TestAdvisoryEngine:
    """Tests for the rule-based irrigation advisory engine."""

    @pytest.fixture
    def rice_vegetative_rule(self):
        return {
            "crop_type": "Rice",
            "growth_stage": "Vegetative",
            "water_requirement_mm_per_day": 10.0,
            "moisture_threshold_percent": 55.0,
        }

    def test_wait_when_moisture_above_threshold(self, rice_vegetative_rule):
        """Should recommend WAIT when soil is moist enough."""
        rec = get_recommendation(
            moisture_percent=60.0,
            crop_stage_rule=rice_vegetative_rule,
            rain_probability_percent=20,
            expected_rainfall_mm=0,
        )
        assert rec["recommendation"] == "wait"
        assert rec["amount_mm"] == 0
        assert rec["confidence_score"] > 0

    def test_wait_when_moisture_at_threshold(self, rice_vegetative_rule):
        """Should recommend WAIT when moisture equals threshold exactly."""
        rec = get_recommendation(
            moisture_percent=55.0,
            crop_stage_rule=rice_vegetative_rule,
            rain_probability_percent=10,
            expected_rainfall_mm=0,
        )
        assert rec["recommendation"] == "wait"

    def test_irrigate_when_moisture_below_threshold(self, rice_vegetative_rule):
        """Should recommend IRRIGATE when soil is dry."""
        rec = get_recommendation(
            moisture_percent=30.0,
            crop_stage_rule=rice_vegetative_rule,
            rain_probability_percent=10,
            expected_rainfall_mm=0,
        )
        assert rec["recommendation"] == "irrigate"
        assert rec["amount_mm"] > 0
        assert rec["total_litres"] > 0

    def test_wait_when_high_rain_covers_need(self, rice_vegetative_rule):
        """Should recommend WAIT when heavy rain is forecast."""
        rec = get_recommendation(
            moisture_percent=40.0,
            crop_stage_rule=rice_vegetative_rule,
            rain_probability_percent=75,
            expected_rainfall_mm=8.0,  # 80% of 10mm daily need
        )
        assert rec["recommendation"] == "wait"
        assert "rain" in rec["reason"].lower()

    def test_irrigate_adjusted_for_partial_rain(self, rice_vegetative_rule):
        """Should reduce irrigation amount when partial rain is expected."""
        rec_no_rain = get_recommendation(
            moisture_percent=35.0,
            crop_stage_rule=rice_vegetative_rule,
            rain_probability_percent=10,
            expected_rainfall_mm=0,
        )
        rec_some_rain = get_recommendation(
            moisture_percent=35.0,
            crop_stage_rule=rice_vegetative_rule,
            rain_probability_percent=50,
            expected_rainfall_mm=3.0,
        )
        assert rec_some_rain["amount_mm"] <= rec_no_rain["amount_mm"]

    def test_deficit_factor_increases_with_dryness(self, rice_vegetative_rule):
        """Drier soil should produce higher deficit factor."""
        rec_dry = get_recommendation(20.0, rice_vegetative_rule, 10, 0)
        rec_moist = get_recommendation(45.0, rice_vegetative_rule, 10, 0)
        assert rec_dry["deficit_factor"] > rec_moist["deficit_factor"]

    def test_confidence_score_range(self, rice_vegetative_rule):
        """Confidence score should be between 0 and 100."""
        rec = get_recommendation(35.0, rice_vegetative_rule, 30, 2.0)
        assert 0 <= rec["confidence_score"] <= 100

    def test_total_litres_scales_with_area(self, rice_vegetative_rule):
        """Larger fields should get proportionally more total litres."""
        rec_small = get_recommendation(30.0, rice_vegetative_rule, 10, 0, field_area_acres=1.0)
        rec_large = get_recommendation(30.0, rice_vegetative_rule, 10, 0, field_area_acres=3.0)
        assert rec_large["total_litres"] > rec_small["total_litres"]


class TestLookupCropRule:
    """Tests for crop rule lookup from the built-in table."""

    def test_lookup_existing_rule(self):
        rule = lookup_crop_rule("Rice", "Vegetative")
        assert rule is not None
        assert rule["crop_type"] == "Rice"
        assert rule["water_requirement_mm_per_day"] == 10.0

    def test_lookup_case_insensitive(self):
        rule = lookup_crop_rule("rice", "vegetative")
        assert rule is not None

    def test_lookup_nonexistent_returns_none(self):
        rule = lookup_crop_rule("Banana", "Unknown")
        assert rule is None

    def test_all_crops_have_four_stages(self):
        crops = ["Rice", "Maize", "Chili", "Cotton", "Sugarcane"]
        stages = ["Germination", "Vegetative", "Flowering", "Maturity"]
        for crop in crops:
            for stage in stages:
                rule = lookup_crop_rule(crop, stage)
                assert rule is not None, f"Missing rule for {crop}/{stage}"


class TestBatchEvaluation:
    """Tests for batch advisory evaluation."""

    def test_batch_returns_dataframe(self):
        readings = [
            {"crop_type": "Rice", "growth_stage": "Vegetative", "moisture_percent": 35,
             "rain_probability_percent": 20, "expected_rainfall_mm": 0, "area_acres": 2},
            {"crop_type": "Maize", "growth_stage": "Flowering", "moisture_percent": 60,
             "rain_probability_percent": 10, "expected_rainfall_mm": 0, "area_acres": 1},
        ]
        result = evaluate_batch(readings)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_batch_empty_input(self):
        result = evaluate_batch([])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# ═══════════════════════════════════════════════════════════════════════
# ANALYTICS TESTS
# ═══════════════════════════════════════════════════════════════════════

class TestWaterUsageTrend:
    """Tests for Pandas-powered water usage aggregation."""

    def test_daily_aggregation(self):
        logs = [
            {"date": "2024-06-01T08:00:00", "actual_amount_mm": 5.0},
            {"date": "2024-06-01T14:00:00", "actual_amount_mm": 3.0},
            {"date": "2024-06-02T09:00:00", "actual_amount_mm": 7.0},
        ]
        trend = compute_water_usage_trend(logs, period="daily")
        assert len(trend) == 2
        assert trend[0]["total_mm"] == 8.0  # Jun 1: 5 + 3

    def test_empty_logs(self):
        assert compute_water_usage_trend([]) == []

    def test_missing_columns(self):
        assert compute_water_usage_trend([{"foo": "bar"}]) == []


class TestAdherence:
    """Tests for recommendation adherence scoring."""

    def test_perfect_adherence(self):
        logs = [
            {"recommendation": "irrigate", "action_taken": "irrigated", "recommended_amount_mm": 10, "actual_amount_mm": 10},
            {"recommendation": "wait", "action_taken": "skipped", "recommended_amount_mm": 0, "actual_amount_mm": 0},
        ]
        result = compute_adherence(logs)
        assert result["adherence_percent"] == 100.0

    def test_zero_adherence(self):
        logs = [
            {"recommendation": "irrigate", "action_taken": "skipped", "recommended_amount_mm": 10, "actual_amount_mm": 0},
            {"recommendation": "wait", "action_taken": "irrigated", "recommended_amount_mm": 0, "actual_amount_mm": 8},
        ]
        result = compute_adherence(logs)
        assert result["adherence_percent"] == 0.0

    def test_empty_logs(self):
        result = compute_adherence([])
        assert result["adherence_percent"] == 0.0
        assert result["total_logs"] == 0


class TestMoistureTrend:
    """Tests for moisture trend analysis."""

    def test_trend_calculation(self):
        readings = [
            {"moisture_percent": 40, "timestamp": "2024-06-01T08:00:00"},
            {"moisture_percent": 45, "timestamp": "2024-06-02T08:00:00"},
            {"moisture_percent": 50, "timestamp": "2024-06-03T08:00:00"},
            {"moisture_percent": 55, "timestamp": "2024-06-04T08:00:00"},
        ]
        result = compute_moisture_trend(readings)
        assert result["stats"]["trend"] == "rising"
        assert result["stats"]["min"] == 40.0
        assert result["stats"]["max"] == 55.0

    def test_empty_readings(self):
        result = compute_moisture_trend([])
        assert result["readings"] == []


# ═══════════════════════════════════════════════════════════════════════
# ADVANCED AGRONOMIC ENGINE TESTS
# ═══════════════════════════════════════════════════════════════════════

class TestAdvancedAgronomics:
    """Tests for FAO-56 Kc, ET0, Effective Rain, Pump Run-time & 7-Day Schedule."""

    def test_et0_calculation(self):
        from advisory_engine import calculate_et0
        et0_hot = calculate_et0(temperature_c=38.0, humidity_percent=40.0, wind_speed_kmh=15.0)
        et0_cool = calculate_et0(temperature_c=22.0, humidity_percent=75.0, wind_speed_kmh=5.0)
        assert et0_hot > et0_cool
        assert 1.5 <= et0_hot <= 12.0
        assert 1.5 <= et0_cool <= 12.0

    def test_effective_rainfall_low_prob(self):
        from advisory_engine import calculate_effective_rainfall
        peff = calculate_effective_rainfall(rain_probability_percent=15, expected_rainfall_mm=10.0)
        assert peff == 0.0

    def test_effective_rainfall_high_prob(self):
        from advisory_engine import calculate_effective_rainfall
        peff = calculate_effective_rainfall(rain_probability_percent=80, expected_rainfall_mm=20.0)
        assert peff > 0.0
        assert peff <= 20.0

    def test_pump_runtime_calculation(self):
        from advisory_engine import calculate_pump_runtime
        res_zero = calculate_pump_runtime(0)
        assert res_zero["total_minutes"] == 0
        assert res_zero["hours"] == 0

        # 5 HP pump (~900 L/min) -> 54,000 Litres should take ~60 min (1 hour)
        res_54k = calculate_pump_runtime(54000, pump_hp=5.0)
        assert 50 <= res_54k["total_minutes"] <= 70
        assert res_54k["energy_kwh"] > 0

    def test_7day_schedule_generation(self):
        from advisory_engine import generate_7day_schedule
        schedule = generate_7day_schedule(
            crop_type="Rice",
            growth_stage="Vegetative",
            initial_moisture_pct=35.0,
            soil_type="Clay Loam",
            irrigation_method="Drip",
            field_area_acres=2.0,
            pump_hp=5.0,
        )
        assert len(schedule) == 7
        assert schedule[0]["day"] == 1
        assert "projected_moisture_pct" in schedule[0]
        assert "action" in schedule[0]

    def test_soil_and_irrigation_constants(self):
        from advisory_engine import SOIL_CHARACTERISTICS, IRRIGATION_METHODS
        assert "Clay Loam" in SOIL_CHARACTERISTICS
        assert "Sandy Loam" in SOIL_CHARACTERISTICS
        assert "Drip" in IRRIGATION_METHODS
        assert IRRIGATION_METHODS["Drip"]["efficiency"] == 0.90
        assert IRRIGATION_METHODS["Flood"]["efficiency"] == 0.50

    def test_multilingual_bulletin_structure(self):
        rule = lookup_crop_rule("Chili", "Flowering")
        rec = get_recommendation(
            moisture_percent=30.0,
            crop_stage_rule=rule,
            rain_probability_percent=10,
            expected_rainfall_mm=0,
            field_area_acres=1.5,
            irrigation_method="Drip",
        )
        assert "bulletins" in rec
        assert "en" in rec["bulletins"]
        assert "hi" in rec["bulletins"]
        assert "te" in rec["bulletins"]
        assert "Chili" in rec["bulletins"]["en"]


# ═══════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
