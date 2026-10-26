"""
tests/test_growth_and_market.py
================================================================================
Kiểm thử tự động các chức năng của Growth Intelligence & Market Discovery:
- Kiểm tra tính toán kinh tế đơn vị & mô hình xác suất đơn hàng
- Kiểm tra chẩn đoán phễu TikTok Shop 2026 (4 trạng thái)
- Kiểm tra bộ quy tắc ra quyết định STOP / ITERATE / SCALE
- Kiểm tra quy trình nghiên cứu thị trường Sprint 1 (18 ngách & Top 3)
================================================================================
"""

import unittest
import math
import pathlib
import shutil
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from engine.growth_intelligence import (
    UnitEconomicsCalculator,
    FunnelDiagnoser,
    DecisionEngine,
    ControlledTestPlanner
)
from engine.market_discovery import MarketDiscoveryEngine, DOCS_SPRINT1_DIR
from engine.database import (
    upsert_video_metrics,
    get_video_metrics,
    list_niches,
    list_candidate_products
)

class TestGrowthAndMarket(unittest.TestCase):

    def test_01_reverse_profit_calculator(self):
        # 5 triệu đồng hoa hồng, giá 200k, hoa hồng 10% (20k/đơn)
        # CTR 1%, CVR 3% -> 0.0003 đơn/view
        res = UnitEconomicsCalculator.calculate_target_funnel(
            target_profit_vnd=5000000,
            price_vnd=200000,
            commission_rate=0.10,
            ctr=0.01,
            cvr=0.03
        )
        self.assertEqual(res["required_orders"], 250)
        self.assertEqual(res["required_views"], 833334)
        self.assertEqual(res["videos_needed"]["at_500_views"], 1667)
        self.assertEqual(res["videos_needed"]["at_10000_views"], 84)

    def test_02_probability_model(self):
        prob_1000 = UnitEconomicsCalculator.calculate_order_probabilities(1000, ctr=0.01, cvr=0.02)
        # Expected orders = 1000 * 0.0002 = 0.2 đơn
        self.assertAlmostEqual(prob_1000["expected_orders"], 0.2, places=2)
        self.assertAlmostEqual(prob_1000["prob_gte_1_percent"], 18.13, places=1)
        self.assertAlmostEqual(prob_1000["prob_gte_2_percent"], 1.75, places=1)

    def test_03_funnel_diagnostics_tiktok_2026(self):
        # 1. Low Views (< 500)
        diag1 = FunnelDiagnoser.diagnose(views=350, clicks=2, orders=0)
        self.assertEqual(diag1["state"], "LOW_VIEWS")
        self.assertEqual(diag1["decision"], "ITERATE")

        # 2. Improve Clicks (Views >= 500, CTR < 1%)
        diag2 = FunnelDiagnoser.diagnose(views=10000, clicks=15, orders=0)
        self.assertEqual(diag2["state"], "IMPROVE_CLICKS")
        self.assertEqual(diag2["decision"], "ITERATE")

        # 3. Improve Conversions (Clicks >= 20, CVR < 2%)
        diag3 = FunnelDiagnoser.diagnose(views=10000, clicks=300, orders=1)
        self.assertEqual(diag3["state"], "IMPROVE_CONVERSIONS")
        self.assertEqual(diag3["decision"], "ITERATE")

        # 4. Scale Winner
        diag4 = FunnelDiagnoser.diagnose(views=10000, clicks=200, orders=15)
        self.assertEqual(diag4["state"], "SCALE_WINNER")
        self.assertEqual(diag4["decision"], "SCALE")

    def test_04_controlled_test_matrix(self):
        matrix = ControlledTestPlanner.generate_3_angle_matrix("SKU-TEST-001", "Củ sạc GaN", 150000)
        self.assertEqual(len(matrix), 3)
        self.assertEqual(matrix[0]["angle_type"], "PAIN_POINT_RESCUE")
        self.assertEqual(matrix[1]["angle_type"], "SATISFYING_DEMO")
        self.assertEqual(matrix[2]["angle_type"], "PRICE_OFFER_SHOCK")

    def test_05_market_discovery_pipeline_and_deliverables(self):
        res = MarketDiscoveryEngine.run_market_discovery(persist_db=True)
        self.assertEqual(res["total_niches_analyzed"], 18)
        self.assertEqual(len(res["top_3_selected"]), 3)

        # Kiểm tra file đã xuất ra docs/sprint1
        self.assertTrue((DOCS_SPRINT1_DIR / "market_report.md").exists())
        self.assertTrue((DOCS_SPRINT1_DIR / "niche_ranking.csv").exists())
        self.assertTrue((DOCS_SPRINT1_DIR / "product_candidates.csv").exists())
        self.assertTrue((DOCS_SPRINT1_DIR / "evidence_registry.json").exists())
        self.assertTrue((DOCS_SPRINT1_DIR / "research_gaps.md").exists())
        self.assertTrue((DOCS_SPRINT1_DIR / "video_test_plan.md").exists())

        # Kiểm tra database đã lưu các ngách
        db_niches = list_niches()
        self.assertGreaterEqual(len(db_niches), 18)
        self.assertEqual(db_niches[0]["selected_status"], "TOP_3_SELECTED")

    def test_06_editorial_strategy_and_zero_selling_rule(self):
        from engine.editorial_engine import EditorialStrategyEngine
        from engine.database import list_editorial_plan, list_audience_personas

        res = EditorialStrategyEngine.initialize_editorial_system()
        self.assertEqual(res["total_videos"], 30)
        self.assertEqual(res["value_only_count"], 15)
        self.assertEqual(res["mistake_analysis_count"], 9)
        self.assertEqual(res["affiliate_count"], 6)

        # Kiểm tra database
        plan = list_editorial_plan()
        self.assertEqual(len(plan), 30)

        # Kiểm tra quy tắc 0 bán hàng cho 15 video Value-only
        value_videos = [v for v in plan if v["content_type"] == "VALUE_ONLY"]
        for v in value_videos:
            self.assertEqual(v["has_affiliate_link"], 0, f"Video {v['video_number']} vi phạm quy tắc không bán hàng!")
            self.assertIsNone(v["linked_sku"])

        # Kiểm tra personas
        personas = list_audience_personas()
        self.assertGreaterEqual(len(personas), 2)
        rental = next(p for p in personas if p["id"] == "persona_rental_living")
        self.assertEqual(rental["archetype"], "SMART_CONSUMER_AND_PROBLEM_SOLVER")
        self.assertGreaterEqual(len(rental["primary_pains"]), 3)

if __name__ == "__main__":
    unittest.main()
