"""
flow/flow_generator.py
================================================================================
Trình tạo Prompt chuyên sâu cho Google Flow / Veo:
- Tự động sinh Prompt chuẩn tiếng Anh cho Veo 3.1
- Khóa góc máy (Camera Angle), ánh sáng (Cinematic Lighting) và tham chiếu (Reference Image)
- Định dạng xuất bản vào tầng 04_Flow_Projects sẵn sàng dán vào Google Flow
================================================================================
"""

import json
import pathlib
from typing import Dict, Any, List

from config.settings import DIR_FLOW_PROJECTS
from engine.asset_manager import AssetManager
from engine.database import record_artifact, log_event

class FlowPromptGenerator:
    """Tạo bộ prompt và kịch bản cảnh cho Google Flow."""

    @classmethod
    def generate_flow_project(cls, sku: str, product_title: str, scenes: List[Dict[str, Any]]) -> pathlib.Path:
        """Tạo file markdown chứa toàn bộ prompt Veo cho từng phân cảnh."""
        dirs = AssetManager.ensure_sku_directories(sku)
        flow_dir = dirs["flow"]

        md_file = flow_dir / "flow_prompts.md"
        json_file = flow_dir / "flow_project.json"

        flow_scenes = []
        md_sections = []

        for idx, s in enumerate(scenes, 1):
            prompt_en = s.get("veo_prompt")
            if not prompt_en:
                # Tự động suy biến prompt nếu chưa có sẵn
                prompt_en = (
                    f"Close-up commercial shot of {product_title}. "
                    f"Action: {s.get('subtitle', 'demonstration in modern clean kitchen or room')}. "
                    "9:16 vertical video aspect ratio. Soft rim lighting, cinematic depth of field, 4k detail."
                )

            flow_scene = {
                "scene_number": idx,
                "id": s.get("id", f"scene_{idx}"),
                "title_badge": s.get("title_badge", ""),
                "veo_prompt": prompt_en,
                "settings": {
                    "aspect_ratio": "9:16 (Vertical)",
                    "model": "Veo 3.1 Fast",
                    "audio_generate": True
                },
                "reference_asset": s.get("reference_asset", "Ảnh sản phẩm chính (hero.jpg)")
            }
            flow_scenes.append(flow_scene)

            md_sections.append(f"""### CẢNH {idx}: {s.get('title_badge', f'Phân đoạn {idx}')}
- **Mục tiêu:** {s.get('subtitle', '')}
- **Cài đặt Flow:** Tỷ lệ `9:16`, Model `Veo 3.1 Fast`, Audio: `Bật`
- **Ảnh tham chiếu (Reference):** `{flow_scene['reference_asset']}`

**Prompt Veo (Copy & Paste vào Flow):**
```text
{prompt_en}
```
""")

        full_md = f"""# DỰ ÁN GOOGLE FLOW: {product_title}
- **Mã SKU:** `{sku}`
- **Công cụ:** Google Flow (flow.google.com) với Flow Agent / Veo
- **Thư mục chứa video đầu ra từ Flow:** `05_Raw_Videos/{sku}/`

---
{"".join(md_sections)}
"""
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(full_md)

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({"sku": sku, "title": product_title, "scenes": flow_scenes}, f, ensure_ascii=False, indent=2)

        record_artifact(sku, "FLOW_PROMPTS", str(md_file))
        log_event(sku, "FLOW_PROMPTS_GENERATED", {"path": str(md_file)})

        return md_file
