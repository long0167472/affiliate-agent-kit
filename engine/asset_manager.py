"""
engine/asset_manager.py
================================================================================
Quản lý tư liệu (Asset Manager):
- Tạo và đồng bộ cấu trúc thư mục cho từng SKU trên Google Drive Desktop
- Thu thập, kiểm tra tính toàn vẹn của ảnh sản phẩm và footage
- Ngăn chặn dựng video sai sự thật nếu thiếu tư liệu kiểm chứng
================================================================================
"""

import os
import json
import shutil
import urllib.request
import pathlib
from typing import Dict, Any, List, Optional
from PIL import Image

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
from engine.database import record_artifact, log_event

class AssetManager:
    """Quản lý tư liệu vật lý và phân loại theo SKU."""

    @staticmethod
    def ensure_sku_directories(sku: str) -> Dict[str, pathlib.Path]:
        """Tạo sẵn các thư mục con cho SKU trong toàn bộ 8 tầng Google Drive."""
        paths = {
            "research": DIR_PRODUCT_RESEARCH / sku,
            "assets": DIR_APPROVED_ASSETS / sku,
            "scripts": DIR_SCRIPTS / sku,
            "flow": DIR_FLOW_PROJECTS / sku,
            "raw_videos": DIR_RAW_VIDEOS / sku,
            "rendered": DIR_RENDERED_VIDEOS / sku,
            "quality": DIR_QUALITY_REPORTS / sku,
        }
        for p in paths.values():
            p.mkdir(parents=True, exist_ok=True)
        return paths

    @staticmethod
    def save_product_research(sku: str, research_data: Dict[str, Any]) -> pathlib.Path:
        """Lưu báo cáo nghiên cứu sản phẩm vào tầng 01_Product_Research."""
        dirs = AssetManager.ensure_sku_directories(sku)
        json_file = dirs["research"] / "product_research.json"
        md_file = dirs["research"] / "product_research.md"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(research_data, f, ensure_ascii=False, indent=2)

        # Tạo file markdown dễ đọc cho người dùng
        md_content = f"""# Báo cáo Nghiên cứu Sản phẩm: {research_data.get('title', sku)}
- **Mã SKU:** `{sku}`
- **Giá bán:** {research_data.get('price_vnd', 0):,.0f} đ
- **Tỷ lệ hoa hồng:** {research_data.get('commission_rate', 0)*100:.1f}% (~ {research_data.get('commission_vnd', 0):,.0f} đ/đơn)
- **Hạng độ tin cậy bằng chứng:** Grade {research_data.get('evidence_grade', 'B')}
- **Nền tảng nhắm tới:** {research_data.get('platform', 'TikTok Shop & Shopee Video')}

## Điểm đau của khách hàng (Pain Points)
{chr(10).join(f"- {p}" for p in research_data.get('pain_points', []))}

## Tính năng nổi bật & Bằng chứng thực tế
{chr(10).join(f"- {f}" for f in research_data.get('key_features', []))}

## Tuyên bố tiếp thị được phép (Allowed Claims)
{chr(10).join(f"- {c}" for c in research_data.get('allowed_claims', []))}

## Cảnh báo rủi ro & Không được nói quá (Disallowed Claims)
{chr(10).join(f"- {d}" for d in research_data.get('disallowed_claims', []))}
"""
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        record_artifact(sku, "PRODUCT_RESEARCH", str(json_file))
        return json_file

    @staticmethod
    def save_script(sku: str, script_data: Dict[str, Any]) -> pathlib.Path:
        """Lưu kịch bản vào tầng 03_Scripts."""
        dirs = AssetManager.ensure_sku_directories(sku)
        json_file = dirs["scripts"] / "creative_script.json"
        md_file = dirs["scripts"] / "creative_script.md"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)

        scenes = script_data.get("scenes", [])
        scenes_md = "\n\n".join([
            f"### Phân cảnh {idx+1}: {s.get('id', '')} ({s.get('duration_estimate', '4')}s)\n"
            f"- **Badge tiêu đề:** `{s.get('title_badge', '')}`\n"
            f"- **Phụ đề:** {s.get('subtitle', '')}\n"
            f"- **Lời thoại (Voiceover):** \"{s.get('voiceover', '')}\"\n"
            f"- **Mô tả hình ảnh:** {s.get('visual_description', '')}"
            for idx, s in enumerate(scenes)
        ])

        md_content = f"""# Kịch bản Video Affiliate: {script_data.get('angle_name', 'Góc tiếp cận chính')}
- **SKU:** `{sku}`
- **Góc tiếp cận (Angle):** {script_data.get('hook_angle', 'Pain Point -> Quick Relief')}
- **Thời lượng dự kiến:** {script_data.get('total_duration_estimate', '25-30')} giây

---
{scenes_md}
"""
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        record_artifact(sku, "SCRIPT_SET", str(json_file))
        return json_file

    @staticmethod
    def save_image_asset(sku: str, image_source: str, filename: str) -> Optional[pathlib.Path]:
        """Tải hoặc sao chép ảnh vào 02_Approved_Assets."""
        dirs = AssetManager.ensure_sku_directories(sku)
        target_path = dirs["assets"] / filename

        try:
            if image_source.startswith("http://") or image_source.startswith("https://"):
                req = urllib.request.Request(image_source, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    with open(target_path, "wb") as f:
                        f.write(resp.read())
            else:
                src_path = pathlib.Path(image_source)
                if src_path.exists():
                    shutil.copy2(str(src_path), str(target_path))
                else:
                    return None

            # Xác thực ảnh mở được
            with Image.open(target_path) as img:
                img.verify()

            record_artifact(sku, "APPROVED_IMAGE", str(target_path), {"filename": filename})
            return target_path
        except Exception as e:
            log_event(sku, "ASSET_DOWNLOAD_ERROR", {"file": filename, "error": str(e)})
            return None

    @staticmethod
    def verify_assets_ready(sku: str) -> Dict[str, Any]:
        """Kiểm tra xem tư liệu đã đủ để dựng video trung thực hay chưa."""
        dirs = AssetManager.ensure_sku_directories(sku)
        images = list(dirs["assets"].glob("*.jpg")) + list(dirs["assets"].glob("*.png"))
        raw_videos = list(dirs["raw_videos"].glob("*.mp4"))

        is_ready = (len(images) >= 3) or (len(raw_videos) >= 1)
        reason = "Đủ tư liệu hình ảnh/video để sản xuất." if is_ready else "Thiếu tư liệu. Cần tối thiểu 3 ảnh hoặc 1 video thật."

        return {
            "sku": sku,
            "images_count": len(images),
            "videos_count": len(raw_videos),
            "is_ready": is_ready,
            "message": reason,
            "image_paths": [str(p) for p in images],
            "video_paths": [str(p) for p in raw_videos]
        }
