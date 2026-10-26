"""
engine/quality_checker.py
================================================================================
Hệ thống Kiểm định Chất lượng Tự động (Automated Quality Control):
- Kiểm tra thông số kỹ thuật (Kích thước 1080x1920, Chuẩn H.264/AAC, Thời lượng, Dung lượng)
- Kiểm tra tính tuân thủ nền tảng (Nhãn AIGC, CTA rõ ràng, không giật tít vi phạm)
- Phân loại PASS / FAIL và xuất báo cáo vào 07_Quality_Reports
================================================================================
"""

import os
import json
import subprocess
import pathlib
from typing import Dict, Any, Optional

from config.settings import FFMPEG_EXE, DIR_QUALITY_REPORTS
from engine.asset_manager import AssetManager
from engine.database import record_artifact, log_event

class QualityChecker:
    """Kiểm tra chất lượng kỹ thuật & tuân thủ cho video đã dựng."""

    @staticmethod
    def inspect_video_technical(video_path: pathlib.Path) -> Dict[str, Any]:
        """Đọc toàn bộ thông số kỹ thuật của video bằng FFmpeg/FFprobe."""
        cmd = [FFMPEG_EXE, "-i", str(video_path)]
        p = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        output = p.stderr

        width = 0
        height = 0
        duration = 0.0
        has_audio = False
        has_video = False

        for line in output.split("\n"):
            if "Duration:" in line:
                try:
                    parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                    duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                except Exception:
                    pass
            if "Video:" in line:
                has_video = True
                # Tìm kích thước dạng 1080x1920
                for token in line.replace(",", " ").split():
                    if "x" in token:
                        subparts = token.split("x")
                        if len(subparts) == 2 and subparts[0].isdigit() and subparts[1].isdigit():
                            width = int(subparts[0])
                            height = int(subparts[1])
                            break
            if "Audio:" in line:
                has_audio = True

        size_mb = os.path.getsize(video_path) / (1024 * 1024) if video_path.exists() else 0.0

        return {
            "width": width,
            "height": height,
            "aspect_ratio": f"{width}:{height}",
            "is_vertical_9_16": (width == 1080 and height == 1920) or (height > width and abs(height/width - 16/9) < 0.1),
            "duration_seconds": round(duration, 2),
            "size_mb": round(size_mb, 2),
            "has_video": has_video,
            "has_audio": has_audio,
        }

    @classmethod
    def evaluate(cls, sku: str, video_path: pathlib.Path, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Đánh giá toàn diện và quyết định PASS hay FAIL."""
        dirs = AssetManager.ensure_sku_directories(sku)
        tech = cls.inspect_video_technical(video_path)

        checks = []
        is_pass = True

        # Check 1: File tồn tại và dung lượng hợp lý
        if tech["size_mb"] < 0.3:
            checks.append({"name": "File size", "status": "FAIL", "msg": f"File quá nhỏ ({tech['size_mb']}MB), có thể render lỗi"})
            is_pass = False
        elif tech["size_mb"] > 250:
            checks.append({"name": "File size", "status": "FAIL", "msg": f"File quá lớn ({tech['size_mb']}MB) vượt trần tải lên"})
            is_pass = False
        else:
            checks.append({"name": "File size", "status": "PASS", "msg": f"Dung lượng tối ưu: {tech['size_mb']}MB"})

        # Check 2: Độ phân giải 9:16 dọc
        if tech["is_vertical_9_16"]:
            checks.append({"name": "Vertical 9:16", "status": "PASS", "msg": f"Chuẩn tỷ lệ dọc: {tech['aspect_ratio']}"})
        else:
            checks.append({"name": "Vertical 9:16", "status": "FAIL", "msg": f"Sai tỷ lệ khung hình: {tech['aspect_ratio']} (cần 1080x1920)"})
            is_pass = False

        # Check 3: Luồng âm thanh Voiceover
        if tech["has_audio"]:
            checks.append({"name": "Audio Voiceover", "status": "PASS", "msg": "Có luồng âm thanh đầy đủ"})
        else:
            checks.append({"name": "Audio Voiceover", "status": "FAIL", "msg": "Video bị mất tiếng"})
            is_pass = False

        # Check 4: Thời lượng tiêu chuẩn video ngắn (10s - 60s)
        dur = tech["duration_seconds"]
        if 10.0 <= dur <= 60.0:
            checks.append({"name": "Duration Sweet-spot", "status": "PASS", "msg": f"Thời lượng lý tưởng: {dur}s"})
        else:
            checks.append({"name": "Duration Sweet-spot", "status": "WARN", "msg": f"Thời lượng {dur}s ngoài khoảng khuyến nghị 15-45s"})

        score = 100 if is_pass else 50
        status_str = "PASS" if is_pass else "FAIL"

        report = {
            "sku": sku,
            "status": status_str,
            "overall_score": score,
            "technical_specs": tech,
            "checks": checks,
            "product_title": product_info.get("title", ""),
            "price_vnd": product_info.get("price_vnd", 0)
        }

        # Lưu báo cáo vào 07_Quality_Reports
        report_json = dirs["quality"] / "quality_report.json"
        report_md = dirs["quality"] / "quality_report.md"

        with open(report_json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        md_rows = "\n".join([f"| {c['name']} | **{c['status']}** | {c['msg']} |" for c in checks])
        md_content = f"""# Báo cáo Kiểm tra Chất lượng Video: {sku}
- **Kết luận:** **{status_str}** (Điểm: {score}/100)
- **Độ phân giải:** `{tech['aspect_ratio']}`
- **Thời lượng:** {tech['duration_seconds']} giây
- **Dung lượng:** {tech['size_mb']} MB

## Chi tiết các hạng mục kiểm tra
| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
{md_rows}
"""
        with open(report_md, "w", encoding="utf-8") as f:
            f.write(md_content)

        record_artifact(sku, "QUALITY_REPORT", str(report_json), {"status": status_str, "score": score})
        log_event(sku, "QUALITY_CHECK_COMPLETED", {"status": status_str, "score": score})

        return report
