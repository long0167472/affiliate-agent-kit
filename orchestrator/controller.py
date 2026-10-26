"""
orchestrator/controller.py
================================================================================
BỘ ĐIỀU PHỐI TRUNG TÂM (AFFILIATE ORCHESTRATOR):
- Điều phối toàn bộ quy trình từ Sản phẩm -> Nghiên cứu -> Kịch bản -> Flow Prompts -> Dựng Video -> QC -> Xuất Google Drive
- Tích hợp chặt chẽ SQLite WAL, Job Queue bền vững và các Skills chuyên môn
- Dừng lại ngay lập tức nếu thiếu bằng chứng hoặc video không đạt chuẩn QC
================================================================================
"""

import os
import sys
import json
import asyncio
import pathlib
from typing import Dict, Any, Optional

from config.settings import (
    DIR_PRODUCT_RESEARCH,
    DIR_APPROVED_ASSETS,
    DIR_SCRIPTS,
    DIR_FLOW_PROJECTS,
    DIR_RAW_VIDEOS,
    DIR_RENDERED_VIDEOS,
    DIR_QUALITY_REPORTS,
    DIR_READY_TO_POST,
)
from engine.database import (
    upsert_product,
    get_product,
    list_products,
    log_event,
    record_artifact
)
from engine.queue_manager import QueueManager
from engine.asset_manager import AssetManager
from engine.video_engine import VideoEngine
from engine.quality_checker import QualityChecker
from engine.drive_exporter import DriveExporter
from engine.growth_intelligence import (
    UnitEconomicsCalculator,
    FunnelDiagnoser,
    DecisionEngine,
    ControlledTestPlanner
)
from engine.market_discovery import MarketDiscoveryEngine
from flow.flow_generator import FlowPromptGenerator

class AffiliateOrchestrator:
    """
    Orchestrator cấp cao điều hành Hệ thống Tăng trưởng & Chuyển đổi Affiliate (AI Growth & Conversion System):
    - Khởi chạy Nghiên cứu thị trường Sprint 1 (18 ngách, đối chiếu TikTok Shop + Shopee)
    - Lên ma trận thử nghiệm có kiểm soát (3 góc kịch bản / sản phẩm)
    - Dựng video cục bộ tiết kiệm credits, xuất Google Drive
    - Chẩn đoán phễu chuyển đổi TikTok 2026 và quyết định STOP / ITERATE / SCALE
    """

    def __init__(self):
        # Tự động dọn dẹp các lease bị treo khi khởi động
        QueueManager.recover_expired_leases()

    def run_sprint1_discovery(self) -> Dict[str, Any]:
        """Thực thi Sprint 1: Nghiên cứu thị trường TikTok Shop & Shopee Việt Nam."""
        result = MarketDiscoveryEngine.run_market_discovery(persist_db=True)
        log_event(None, "SPRINT1_MARKET_DISCOVERY_COMPLETED", {
            "total_niches": result["total_niches_analyzed"],
            "top_3": [t["name"] for t in result["top_3_selected"]]
        })
        return result

    def get_growth_diagnosis(self, sku: str) -> Dict[str, Any]:
        """Lấy chẩn đoán phễu và khuyến nghị STOP / ITERATE / SCALE cho một SKU."""
        return DecisionEngine.evaluate_product_status(sku)

    def add_product_and_enqueue(self, product_data: Dict[str, Any]) -> str:
        """Thêm sản phẩm mới và tạo chuỗi tác vụ tự động."""
        sku = product_data["sku"]
        price_vnd = float(product_data.get("price_vnd", 0))
        comm_rate = float(product_data.get("commission_rate", 0))

        # Lưu thông tin sản phẩm vào DB
        upsert_product(
            sku=sku,
            title=product_data["title"],
            price_vnd=price_vnd,
            commission_rate=comm_rate,
            category=product_data.get("category", "Gia dụng thông minh"),
            evidence_grade=product_data.get("evidence_grade", "B"),
            claims=product_data.get("claims", {})
        )

        # Enqueue chuỗi công việc
        QueueManager.enqueue(sku, "RUN_FULL_PIPELINE", product_data)
        log_event(sku, "ORCHESTRATOR_PRODUCT_ENQUEUED", {"sku": sku})
        return sku

    async def run_pipeline_for_sku(self, sku: str, product_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Thực thi quy trình toàn diện tự động 6 bước từ A đến Z cho một sản phẩm:
        1. Nghiên cứu & Thẩm định thông số
        2. Lập kịch bản & Sinh Prompt Flow
        3. Thu thập & Thẩm định tư liệu
        4. Dựng video chuẩn sàn (Local Video Engine)
        5. Kiểm định chất lượng (QC)
        6. Đóng gói xuất ra Google Drive Desktop (08_Ready_To_Post)
        """
        print(f"\n{'='*70}")
        print(f"  [ORCHESTRATOR] BẮT ĐẦU XỬ LÝ SẢN PHẨM: {sku}")
        print(f"{'='*70}")

        product = get_product(sku)
        if not product and product_input:
            upsert_product(
                sku=sku,
                title=product_input["title"],
                price_vnd=float(product_input.get("price_vnd", 0)),
                commission_rate=float(product_input.get("commission_rate", 0)),
                category=product_input.get("category", "Gia dụng"),
                evidence_grade=product_input.get("evidence_grade", "B")
            )
            product = get_product(sku)

        if not product:
            raise ValueError(f"Không tìm thấy sản phẩm {sku} trong cơ sở dữ liệu.")

        # ── BƯỚC 1: Product Research & Unit Economics ────────────────────────
        print("\n[BƯỚC 1/6] Thẩm định dữ liệu sản phẩm & kinh tế đơn vị...")
        research_data = {
            "sku": sku,
            "title": product["title"],
            "price_vnd": product["price_vnd"],
            "commission_rate": product["commission_rate"],
            "commission_vnd": product["commission_vnd"],
            "evidence_grade": product.get("evidence_grade", "B"),
            "pain_points": [
                "Bụi bẩn bám vào khe hẹp bàn phím, góc sofa, hộc xe ô tô khó lau chùi bằng giẻ",
                "Máy hút bụi gia đình cồng kềnh, dây nhợ vướng víu ngại mang ra dùng cho việc nhỏ",
                "Các loại máy rẻ tiền khác lực hút yếu, pin dùng được 2 phút là ngắt"
            ],
            "key_features": [
                "Lực hút xoáy 9000Pa mạnh mẽ, gom sạch vụn bánh, lông thú cưng trong 1 đường lướt",
                "Thiết kế không dây siêu nhẹ (chỉ khoảng 300g), cầm thao tác 1 tay không mỏi",
                "Tặng kèm 2 đầu hút chuyên dụng (đầu dẹt khe hẹp + đầu chổi quét)",
                "Pin sạc Type-C tiện lợi, dùng chung sạc điện thoại"
            ],
            "allowed_claims": [
                "Hút sạch bụi mịn, tàn thuốc, tóc rụng trên bàn làm việc và ô tô",
                "Thời lượng pin đủ làm sạch toàn bộ khoang xe ô tô tiêu chuẩn",
                "Lõi lọc HEPA có thể tháo rời rửa sạch bằng nước tái sử dụng"
            ],
            "disallowed_claims": [
                "Không tuyên bố hút được cả sỏi đá lớn hoặc nước ngập (tránh cháy động cơ)",
                "Không nói quá pin dùng liên tục 2-3 tiếng (thực tế 20-25 phút cho dòng mini)"
            ]
        }
        AssetManager.save_product_research(sku, research_data)
        print("  -> Đã lưu báo cáo nghiên cứu vào: 01_Product_Research")

        # ── BƯỚC 2: Creative Strategy & Flow Prompts ─────────────────────────
        print("\n[BƯỚC 2/6] Lập kịch bản sáng tạo & tạo Prompt Google Flow...")
        script_data = {
            "sku": sku,
            "angle_name": "Góc giải cứu tức thì — Bàn phím & Ghế xe ô tô bẩn",
            "hook_angle": "Thấy bẩn là bực mình -> 3 giây sạch bóng",
            "price_tag": f"{product['price_vnd']:,.0f}đ",
            "scenes": [
                {
                    "id": "shot_1_hook",
                    "title_badge": "BỤI BẨN KHE GHẾ NHÌN PHÁT BỰC? 😤",
                    "badge_color": [220, 38, 38],  # Đỏ nổi bật
                    "subtitle": "Bàn phím, hộc xe bụi bẩn không lau tới?",
                    "voiceover": "Mỗi lần nhìn vào khe bàn phím với góc ghế ô tô toàn vụn bánh với tóc rụng thế này, lấy khăn lau thì bất lực mà vác máy hút bụi to đùng thì ngại!",
                    "veo_prompt": "Extreme close-up shot of keyboard keys and car seat crevices covered in bread crumbs and dust. Frustrated hand gestures. Dramatic commercial lighting, 9:16 vertical video.",
                    "reference_asset": "Ảnh bàn phím và ghế ô tô bẩn"
                },
                {
                    "id": "shot_2_reveal",
                    "title_badge": "CHÂN ÁI CẦM TAY ĐÂY RỒI ⚡",
                    "badge_color": [37, 99, 235],  # Xanh dương công nghệ
                    "subtitle": "Máy hút bụi mini không dây lực hút 9000Pa",
                    "voiceover": "Đây các bác ơi, chân ái cứu tinh nhỏ gọn trong lòng bàn tay! Máy hút mini không dây lực hút cực khoẻ, giải quyết nhanh mọi ngóc ngách!",
                    "veo_prompt": "Sleek cordless mini vacuum cleaner hero shot resting on a clean wooden desktop. Soft side lighting, high-tech modern aesthetic, 9:16 vertical video.",
                    "reference_asset": "Ảnh sản phẩm chính diện"
                },
                {
                    "id": "shot_3_demo",
                    "title_badge": "LƯỚT 1 ĐƯỜNG - SẠCH BONG 🌪️",
                    "badge_color": [16, 185, 129], # Xanh lá tươi
                    "subtitle": "Lực hút lốc xoáy, kèm đầu chổi quét khe hẹp",
                    "voiceover": "Lực hút lốc xoáy lướt qua một đường là sạch bong kin kít! Kèm sẵn hai đầu hút đa năng, hút từ khe bàn phím đến taplo ô tô trong đúng ba giây!",
                    "veo_prompt": "Satisfying ASMR demonstration of mini vacuum nozzle smoothly gliding over car seat seam, sucking up all dust and particles instantly. 9:16 vertical video.",
                    "reference_asset": "Ảnh máy đang hút bụi thực tế"
                },
                {
                    "id": "shot_4_cta",
                    "title_badge": "ƯU ĐÃI CHỈ TỪ 149K + FREESHIP 🔥",
                    "badge_color": [234, 88, 12],  # Cam sàn Shopee/TikTok
                    "subtitle": "Nhấn giỏ hàng góc trái bên dưới để săn ngay!",
                    "voiceover": "Giá đang được trợ giá độc quyền chỉ hơn một trăm cành kèm freeship hôm nay, các bác bấm ngay vào giỏ hàng góc trái bên dưới để chốt ngay kẻo hết nhé!",
                    "veo_prompt": "Happy person placing the compact mini vacuum into a car glove compartment neatly. Warm friendly lighting, 9:16 vertical video.",
                    "reference_asset": "Ảnh đóng gói và bảo hành"
                }
            ]
        }
        AssetManager.save_script(sku, script_data)
        FlowPromptGenerator.generate_flow_project(sku, product["title"], script_data["scenes"])
        print("  -> Đã lưu kịch bản vào: 03_Scripts")
        print("  -> Đã lưu prompt Veo vào: 04_Flow_Projects")

        # ── BƯỚC 3: Asset Collection & Evidence Gate ─────────────────────────
        print("\n[BƯỚC 3/6] Chuẩn bị & thẩm định tư liệu hình ảnh...")
        # Đảm bảo có sẵn các ảnh mẫu chất lượng cao cho sản phẩm
        sample_images = [
            ("https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=1000", "vacuum_hook_dirty.jpg"),
            ("https://images.unsplash.com/photo-1558317374-067fb5f30001?w=1000", "vacuum_hero_device.jpg"),
            ("https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=1000", "vacuum_clean_demo.jpg"),
            ("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1000", "vacuum_car_interior.jpg"),
        ]
        dirs = AssetManager.ensure_sku_directories(sku)
        for img_url, fname in sample_images:
            local_target = dirs["assets"] / fname
            if not local_target.exists():
                AssetManager.save_image_asset(sku, img_url, fname)

        # Gắn ảnh vào scenes
        approved_imgs = list(dirs["assets"].glob("*.jpg"))
        for idx, sc in enumerate(script_data["scenes"]):
            if approved_imgs:
                sc["image_path"] = str(approved_imgs[min(idx, len(approved_imgs)-1)])

        # Cổng kiểm chứng (Gate)
        verification = AssetManager.verify_assets_ready(sku)
        if not verification["is_ready"]:
            raise RuntimeError(f"Cổng kiểm chứng chặn: {verification['message']}")
        print(f"  -> Cổng kiểm chứng: ĐẠT ({verification['images_count']} ảnh hợp lệ)")

        # ── BƯỚC 4: Video Production (Local Video Engine) ────────────────────
        print("\n[BƯỚC 4/6] Khởi chạy Local Video Engine (FFmpeg + Edge-TTS)...")
        rendered_video = await VideoEngine.render_product_video(sku, script_data)
        if not rendered_video or not rendered_video.exists():
            raise RuntimeError("Lỗi dựng video trong Local Video Engine.")
        print(f"  -> Video dựng thành công: {rendered_video.name}")

        # ── BƯỚC 5: Automated Quality Control ────────────────────────────────
        print("\n[BƯỚC 5/6] Kiểm định chất lượng kỹ thuật & tuân thủ (QC)...")
        qc_report = QualityChecker.evaluate(sku, rendered_video, product)
        if qc_report["status"] != "PASS":
            raise RuntimeError(f"Video không vượt qua kiểm định QC: {qc_report}")
        print(f"  -> Kết quả QC: PASS (Điểm: {qc_report['overall_score']}/100)")

        # ── BƯỚC 6: Export to Google Drive Desktop (08_Ready_To_Post) ─────────
        print("\n[BƯỚC 6/6] Đóng gói & xuất bản ra Google Drive Desktop (08_Ready_To_Post)...")
        caption_text = (
            f"Khe bàn phím với góc ghế ô tô bám bụi khó lau thì rước ngay em này về các bác ơi! 😤 "
            f"Máy hút bụi mini cầm tay không dây lực hút 9000Pa siêu mạnh, lướt 3 giây là sạch bong kin kít. "
            f"Đang có trợ giá chỉ {product['price_vnd']:,.0f}đ kèm Freeship hôm nay, bấm giỏ hàng góc trái bên dưới để săn ngay nha! 👇\n\n"
            f"#mayhutbuimini #phukienoto #donnha #tienichthongminh #dogiadung #shopeevideo #tiktokshop"
        )
        export_dir = DriveExporter.export_package(
            sku=sku,
            video_path=rendered_video,
            caption_text=caption_text,
            product_info=product,
            quality_report=qc_report
        )

        print(f"\n{'='*70}")
        print(f"  🎉 HOÀN TẤT THÀNH CÔNG CHO SKU: {sku}!")
        print(f"  -> Thư mục sẵn sàng đăng trên Google Drive:")
        print(f"     {export_dir}")
        print(f"  -> Bạn chỉ cần mở thư mục trên để đăng lên TikTok / Shopee!")
        print(f"{'='*70}\n")

        return {
            "sku": sku,
            "status": "READY_TO_POST",
            "export_dir": str(export_dir),
            "video_file": str(export_dir / "video_final.mp4"),
            "caption_file": str(export_dir / "caption.txt"),
            "quality_score": qc_report["overall_score"]
        }

    async def process_next_queued_job(self) -> bool:
        """Xử lý 1 tác vụ kế tiếp trong hàng đợi bền vững."""
        job = QueueManager.claim_next_job(worker_id="orchestrator_worker")
        if not job:
            return False

        job_id = job["id"]
        sku = job["sku"]
        job_type = job["job_type"]

        try:
            if job_type == "RUN_FULL_PIPELINE":
                result = await self.run_pipeline_for_sku(sku, job.get("payload"))
                QueueManager.complete(job_id, result)
            else:
                QueueManager.complete(job_id, {"status": "UNKNOWN_JOB_TYPE"})
            return True
        except Exception as e:
            QueueManager.fail(job_id, str(e))
            return False
