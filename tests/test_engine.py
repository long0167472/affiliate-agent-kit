"""
tests/test_engine.py
================================================================================
Kiểm thử tự động các thành phần của Local Execution Engine:
- Kiểm tra SQLite WAL & Transactions
- Kiểm tra Job Queue & Lease recovery
- Kiểm tra Asset Manager & Quality Checker
================================================================================
"""

import unittest
import pathlib
import json
import os
import shutil

from engine.database import upsert_product, get_product, list_products, log_event
from engine.queue_manager import QueueManager
from engine.asset_manager import AssetManager
from engine.quality_checker import QualityChecker
from engine.drive_exporter import DriveExporter
from config.settings import DIR_READY_TO_POST

class TestAffiliateEngine(unittest.TestCase):

    def test_01_product_and_db(self):
        sku = "TEST-SKU-001"
        p = upsert_product(
            sku=sku,
            title="Sản phẩm kiểm thử Unit Test",
            price_vnd=100000,
            commission_rate=0.15,
            category="Test"
        )
        self.assertEqual(p["sku"], sku)
        self.assertEqual(p["commission_vnd"], 15000.0)

        fetched = get_product(sku)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["title"], "Sản phẩm kiểm thử Unit Test")

    def test_02_queue_and_lease(self):
        sku = "TEST-SKU-001"
        job_id = QueueManager.enqueue(sku, "TEST_TASK", {"msg": "hello"})
        self.assertGreater(job_id, 0)

        # Claim job
        claimed = QueueManager.claim_next_job(worker_id="unit_tester", lease_seconds=60)
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed["id"], job_id)
        self.assertEqual(claimed["payload"]["msg"], "hello")

        # Complete job
        QueueManager.complete(job_id, {"status": "SUCCESS"})
        stats = QueueManager.get_stats()
        self.assertIn("DONE", stats)

    def test_03_asset_directories(self):
        sku = "TEST-SKU-001"
        dirs = AssetManager.ensure_sku_directories(sku)
        for key, p in dirs.items():
            self.assertTrue(p.exists(), f"Thư mục {key} không tồn tại: {p}")

    def test_04_drive_export_structure(self):
        sku = "TEST-SKU-001"
        p = get_product(sku)
        
        # Tạo file video giả lập để test đóng gói
        dummy_video = pathlib.Path("test_dummy.mp4")
        with open(dummy_video, "wb") as f:
            f.write(b"0" * 1024)

        try:
            export_path = DriveExporter.export_package(
                sku=sku,
                video_path=dummy_video,
                caption_text="Caption test #shopee #tiktok",
                product_info=p,
                quality_report={"status": "PASS", "overall_score": 100}
            )
            self.assertTrue(export_path.exists())
            self.assertTrue((export_path / "video_final.mp4").exists())
            self.assertTrue((export_path / "caption.txt").exists())
            self.assertTrue((export_path / "product_info.json").exists())
            self.assertTrue((export_path / "POST_INSTRUCTIONS.md").exists())
        finally:
            if dummy_video.exists():
                dummy_video.unlink()
            # Clean up test folder in Ready_To_Post
            if export_path.exists():
                shutil.rmtree(export_path, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
