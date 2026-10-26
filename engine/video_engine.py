"""
engine/video_engine.py
================================================================================
Local Video Engine:
- Dựng video dọc 9:16 (1080x1920) chuẩn TikTok Shop & Shopee Video
- Tự động sinh giọng đọc AI tự nhiên (Edge-TTS) tiếng Việt
- Layout chuyên nghiệp: Nền mờ nghệ thuật + ảnh/footage trung tâm + Header Badge giật tít + Subtitle tương phản cao + CTA giỏ hàng + Nhãn minh họa AI
- Tự động đo thời lượng chính xác và ghép nối các phân cảnh
================================================================================
"""

import os
import sys
import asyncio
import subprocess
import pathlib
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts

from config.settings import (
    FFMPEG_EXE,
    FONT_BOLD,
    FONT_REGULAR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    DIR_RENDERED_VIDEOS,
    DEFAULT_VOICE
)
from engine.asset_manager import AssetManager
from engine.database import record_artifact, log_event

class VideoEngine:
    """Động cơ kết xuất video affiliate cục bộ."""

    @staticmethod
    async def generate_voiceovers(sku: str, scenes: List[Dict[str, Any]], voice: str = DEFAULT_VOICE) -> List[pathlib.Path]:
        """Tạo các tệp âm thanh giọng đọc AI tiếng Việt theo từng phân cảnh."""
        dirs = AssetManager.ensure_sku_directories(sku)
        audio_dir = dirs["assets"] / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        audio_paths = []
        for idx, scene in enumerate(scenes, 1):
            audio_file = audio_dir / f"scene_{idx}_{scene.get('id', idx)}.mp3"
            text = scene.get("voiceover", "")
            if not text:
                text = scene.get("subtitle", "Sản phẩm chính hãng chất lượng cao.")
            
            # Tăng tốc độ giọng nói +6% để giữ nhịp sôi nổi của video ngắn
            communicate = edge_tts.Communicate(text, voice, rate="+6%")
            await communicate.save(str(audio_file))
            audio_paths.append(audio_file)
            scene["audio_path"] = str(audio_file)

        return audio_paths

    @staticmethod
    def get_audio_duration(audio_path: pathlib.Path) -> float:
        """Đo thời lượng chính xác của audio bằng FFmpeg."""
        cmd = [FFMPEG_EXE, "-i", str(audio_path)]
        p = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        for line in p.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return 4.0

    @staticmethod
    def render_vertical_frame(
        raw_img_path: pathlib.Path,
        output_frame_path: pathlib.Path,
        title_badge: str,
        badge_color: tuple,
        subtitle: str,
        price_tag: Optional[str] = None
    ) -> pathlib.Path:
        """Tạo khung hình 1080x1920 (9:16) thẩm mỹ cao."""
        width, height = VIDEO_WIDTH, VIDEO_HEIGHT
        canvas = Image.new('RGB', (width, height), color=(15, 23, 42))

        with Image.open(raw_img_path).convert('RGB') as src:
            # 1. Nền mờ nghệ thuật
            bg_scale = max(width / src.width, height / src.height)
            bg_w, bg_h = int(src.width * bg_scale), int(src.height * bg_scale)
            bg = src.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
            bg_crop_x = (bg_w - width) // 2
            bg_crop_y = (bg_h - height) // 2
            bg = bg.crop((bg_crop_x, bg_crop_y, bg_crop_x + width, bg_crop_y + height))

            dark_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 130))
            canvas.paste(bg, (0, 0))
            canvas.paste(dark_overlay, (0, 0), dark_overlay)

            # 2. Ảnh sản phẩm trung tâm (880x880)
            fg_size = 900
            fg = src.resize((fg_size, fg_size), Image.Resampling.LANCZOS)
            mask = Image.new('L', (fg_size, fg_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, fg_size, fg_size], radius=36, fill=255)

            fg_x = (width - fg_size) // 2
            fg_y = (height - fg_size) // 2 - 20
            canvas.paste(fg, (fg_x, fg_y), mask)

            draw = ImageDraw.Draw(canvas, 'RGBA')
            draw.rounded_rectangle(
                [fg_x - 3, fg_y - 3, fg_x + fg_size + 3, fg_y + fg_size + 3],
                radius=38,
                outline=(255, 255, 255, 200),
                width=6
            )

        # 3. Header Giật tít (Hook Badge)
        font_badge = ImageFont.truetype(FONT_BOLD, 44)
        badge_w = 940
        badge_h = 100
        badge_x = (width - badge_w) // 2
        badge_y = 240

        draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=24, fill=badge_color)
        draw.text((width // 2, badge_y + badge_h // 2), title_badge, fill=(255, 255, 255), anchor="mm", font=font_badge)

        # Tag giá nếu có
        if price_tag:
            font_price = ImageFont.truetype(FONT_BOLD, 32)
            draw.rounded_rectangle([fg_x + 20, fg_y + 20, fg_x + 240, fg_y + 80], radius=16, fill=(234, 88, 12, 230))
            draw.text((fg_x + 130, fg_y + 50), price_tag, fill=(255, 255, 255), anchor="mm", font=font_price)

        # 4. Phụ đề tóm tắt nổi bật
        font_sub = ImageFont.truetype(FONT_BOLD, 38)
        sub_w = 960
        sub_h = 110
        sub_x = (width - sub_w) // 2
        sub_y = fg_y + fg_size + 50

        draw.rounded_rectangle([sub_x, sub_y, sub_x + sub_w, sub_y + sub_h], radius=20, fill=(0, 0, 0, 200), outline=(255, 255, 255, 120), width=2)
        draw.text((width // 2, sub_y + sub_h // 2), subtitle, fill=(253, 224, 71), anchor="mm", font=font_sub)

        # 5. Kêu gọi hành động (CTA)
        cta_font = ImageFont.truetype(FONT_BOLD, 36)
        draw.text((width // 2, height - 220), "👉 BẤM VÀO GIỎ HÀNG GÓC TRÁI BÊN DƯỚI 👈", fill=(255, 255, 255), anchor="mm", font=cta_font)

        # 6. Nhãn tuân thủ AI (AIGC Label)
        font_small = ImageFont.truetype(FONT_REGULAR, 24)
        draw.text((width // 2, height - 120), "Nội dung minh họa AI • Đã gắn giỏ hàng chính hãng", fill=(148, 163, 184), anchor="mm", font=font_small)

        canvas.save(output_frame_path, quality=95)
        return output_frame_path

    @staticmethod
    def build_scene_clip(frame_path: pathlib.Path, audio_path: pathlib.Path, duration: float, output_clip: pathlib.Path) -> bool:
        """Ghép ảnh tĩnh và âm thanh thành 1 video clip chuyển động 9:16."""
        clip_duration = duration + 0.3
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1",
            "-i", str(frame_path),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(clip_duration),
            "-vf", "scale=1080:1920",
            "-shortest",
            str(output_clip)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        return res.returncode == 0

    @staticmethod
    def concat_clips(clip_paths: List[pathlib.Path], final_output_path: pathlib.Path) -> bool:
        """Ghép toàn bộ các đoạn phân cảnh thành video hoàn chỉnh."""
        concat_txt = final_output_path.parent / f"concat_{final_output_path.stem}.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for cp in clip_paths:
                safe_path = str(cp.resolve()).replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt),
            "-c", "copy",
            str(final_output_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        if concat_txt.exists():
            concat_txt.unlink()
        return res.returncode == 0

    @classmethod
    async def render_product_video(cls, sku: str, script_data: Dict[str, Any]) -> Optional[pathlib.Path]:
        """Quy trình toàn diện dựng video cho SKU từ kịch bản và tư liệu."""
        dirs = AssetManager.ensure_sku_directories(sku)
        scenes = script_data.get("scenes", [])
        if not scenes:
            return None

        # 1. Sinh Voiceover
        await cls.generate_voiceovers(sku, scenes)

        # 2. Xử lý Frame & Clips
        clips = []
        for idx, scene in enumerate(scenes, 1):
            dur = cls.get_audio_duration(pathlib.Path(scene["audio_path"]))
            img_path = pathlib.Path(scene.get("image_path", ""))
            
            # Fallback nếu scene chưa có ảnh riêng thì lấy ảnh đầu tiên trong approved assets
            if not img_path.exists():
                approved = list(dirs["assets"].glob("*.jpg")) + list(dirs["assets"].glob("*.png"))
                if approved:
                    img_path = approved[min(idx - 1, len(approved) - 1)]
                else:
                    return None

            frame_path = dirs["assets"] / f"frame_scene_{idx}.jpg"
            badge_color = scene.get("badge_color", (220, 38, 38))
            if isinstance(badge_color, list):
                badge_color = tuple(badge_color)

            cls.render_vertical_frame(
                raw_img_path=img_path,
                output_frame_path=frame_path,
                title_badge=scene.get("title_badge", "SIÊU PHẨM HOT"),
                badge_color=badge_color,
                subtitle=scene.get("subtitle", ""),
                price_tag=script_data.get("price_tag")
            )

            clip_path = dirs["rendered"] / f"clip_{idx}.mp4"
            if cls.build_scene_clip(frame_path, pathlib.Path(scene["audio_path"]), dur, clip_path):
                clips.append(clip_path)

        # 3. Ghép video thành phẩm vào 06_Rendered_Videos
        final_mp4 = dirs["rendered"] / f"{sku}_rendered_final.mp4"
        if cls.concat_clips(clips, final_mp4):
            record_artifact(sku, "RENDERED_VIDEO", str(final_mp4))
            log_event(sku, "VIDEO_RENDERED", {"output": str(final_mp4)})
            return final_mp4
        return None
