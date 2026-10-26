"""
build_seller_footage_affiliate_video.py
================================================================================
TỰ ĐỘNG BIẾN FOOTAGE VIDEO THỰC TẾ CỦA SELLER THÀNH VIDEO AFFILIATE KOC TRIỆU VIEW
- Cắt các phân đoạn hành động đắt giá nhất từ video gốc (dập củ quả, đổi lưỡi, rửa sạch)
- Tự động dựng layout 9:16 dọc chuẩn TikTok/Shopee (Blurred background + video thật ở giữa)
- Sinh giọng đọc AI tiếng Việt tự nhiên (Edge-TTS) khớp chuẩn xác từng hành động
- Chèn banner giật tít, phụ đề động tương phản cao và lời kêu gọi giỏ hàng
- Xuất video .mp4 hoàn chỉnh 1080x1920 sắc nét 100%
================================================================================
"""

import os
import sys
import json
import subprocess
import pathlib
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
SOURCE_VIDEO = BASE_DIR / "assets" / "source_videos" / "fullstar_demo.mp4"
OVERLAY_DIR = BASE_DIR / "assets" / "overlays"
AUDIO_DIR = BASE_DIR / "assets" / "audio"
OUTPUT_DIR = BASE_DIR / "output"

for d in [OVERLAY_DIR, AUDIO_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FONT_BOLD = "C:\\Windows\\Fonts\\arialbd.ttf"
FONT_REGULAR = "C:\\Windows\\Fonts\\arial.ttf"

# 4 Phân đoạn cắt từ video thật của seller khớp với các audio đã sinh
SEGMENTS = [
    {
        "id": "seg_1_hook",
        "start": 0.5,
        "audio_file": AUDIO_DIR / "shot_1_hook.mp3",
        "title_badge": "THÁI HÀNH THẾ NÀY MÃI À? 😭",
        "badge_color": (220, 38, 38),  # Đỏ
        "subtitle": "Thái hành cay xè mắt, chuẩn bị cơm mất cả tiếng?",
    },
    {
        "id": "seg_2_parts",
        "start": 12.0,
        "audio_file": AUDIO_DIR / "shot_2_reveal.mp3",
        "title_badge": "CHÂN ÁI NHÀ BẾP ĐÂY RỒI ✨",
        "badge_color": (37, 99, 235),  # Xanh dương
        "subtitle": "Bộ cắt gọt 4-in-1, thay lưỡi dao cực dễ",
    },
    {
        "id": "seg_3_chopping",
        "start": 21.0,
        "audio_file": AUDIO_DIR / "shot_3_demo.mp3",
        "title_badge": "DẬP 1 PHÁT - ĐỀU TĂM TẮP 🥕",
        "badge_color": (16, 185, 129), # Xanh lá
        "subtitle": "Lưỡi Inox 420 dập nhẹ là ra hạt lựu trong 3 giây",
    },
    {
        "id": "seg_4_wash_cta",
        "start": 38.0,
        "audio_file": AUDIO_DIR / "shot_4_cta.mp3",
        "title_badge": "GIẢM 40% + FREESHIP HÔM NAY 🔥",
        "badge_color": (234, 88, 12),  # Cam sàn
        "subtitle": "Xả nước rửa cực sạch - Bấm giỏ hàng bên dưới!",
    }
]


def create_overlay_png(output_path, title_badge, badge_color, subtitle):
    """Tạo lớp đồ họa trong suốt 1080x1920 tinh gọn, hiện đại chuẩn TikTok/Shopee."""
    WIDTH, HEIGHT = 1080, 1920
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Header Hook nổi bật nhưng gọn gàng (y ≈ 280)
    badge_w = 860
    badge_h = 90
    badge_x = (WIDTH - badge_w) // 2
    badge_y = 260
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=20, fill=badge_color + (240,))
    font_badge = ImageFont.truetype(FONT_BOLD, 42)
    draw.text((WIDTH // 2, badge_y + badge_h // 2), title_badge, fill=(255, 255, 255, 255), anchor="mm", font=font_badge)

    # 2. Subtitle chữ to rõ nét viền đen ở 1/3 dưới màn hình (y ≈ 1400)
    font_sub = ImageFont.truetype(FONT_BOLD, 44)
    # Vẽ viền đen cho chữ nổi trên mọi nền video
    sub_x, sub_y = WIDTH // 2, 1420
    for offset_x in [-3, -2, -1, 0, 1, 2, 3]:
        for offset_y in [-3, -2, -1, 0, 1, 2, 3]:
            if offset_x != 0 or offset_y != 0:
                draw.text((sub_x + offset_x, sub_y + offset_y), subtitle, fill=(0, 0, 0, 240), anchor="mm", font=font_sub)
    draw.text((sub_x, sub_y), subtitle, fill=(253, 224, 71, 255), anchor="mm", font=font_sub) # Màu vàng rực

    # 3. Lời kêu gọi hành động giỏ hàng góc dưới (y ≈ 1680)
    cta_font = ImageFont.truetype(FONT_BOLD, 36)
    # Background nhẹ cho CTA
    cta_w, cta_h = 780, 70
    cta_x = (WIDTH - cta_w) // 2
    draw.rounded_rectangle([cta_x, 1650, cta_x + cta_w, 1650 + cta_h], radius=16, fill=(0, 0, 0, 160))
    draw.text((WIDTH // 2, 1685), "👉 BẤM GIỎ HÀNG GÓC TRÁI BÊN DƯỚI", fill=(255, 255, 255, 255), anchor="mm", font=cta_font)

    img.save(output_path, "PNG")


def get_audio_duration(audio_path):
    """Lấy thời lượng file audio chính xác."""
    cmd = [FFMPEG_EXE, "-i", str(audio_path)]
    p = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    for line in p.stderr.split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 7.0


def render_seller_segment(source_video, start_time, duration, overlay_png, audio_mp3, output_mp4):
    """
    Cắt video thật từ seller, scale TRÀN VIỀN 100% 1080x1920 (Full bleed 9:16)
    Không dùng hiệu ứng mờ 2 bên/trên dưới, mang lại trải nghiệm xem tự nhiên nhất.
    """
    filter_complex = (
        # Scale tràn viền lấp đầy 1080x1920 (crop chính giữa)
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[fullscreen_v];"
        # Đè lớp overlay chữ phụ đề lên
        "[fullscreen_v][1:v]overlay=0:0[final_v]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", str(source_video),
        "-i", str(overlay_png),
        "-i", str(audio_mp3),
        "-filter_complex", filter_complex,
        "-map", "[final_v]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_mp4)
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if res.returncode != 0:
        print(f"Lỗi render segment {output_mp4.name}: {res.stderr}")
        return False
    return True


def concat_segments(segment_paths, final_output_mp4):
    """Ghép nối các phân đoạn thành 1 video hoàn chỉnh."""
    concat_txt = OUTPUT_DIR / "concat_seller_list.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in segment_paths:
            safe_p = str(p.resolve()).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(final_output_mp4)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if concat_txt.exists():
        concat_txt.unlink()
    return res.returncode == 0


def main():
    print("=" * 70)
    print("  DỰNG VIDEO AFFILIATE TỪ FOOTAGE THỰC TẾ CỦA SELLER (CON ĐƯỜNG SỐ 2)")
    print("=" * 70)

    if not SOURCE_VIDEO.exists():
        print(f"LỖI: Không tìm thấy video nguồn tại {SOURCE_VIDEO}")
        return

    # 1. Xác nhận các file âm thanh có sẵn
    print("\n--- BƯỚC 1: Kiểm tra âm thanh thuyết minh AI ---")
    for seg in SEGMENTS:
        if not seg["audio_file"].exists():
            print(f"  [LỖI] Thiếu file audio: {seg['audio_file']}")
            return
        seg["duration"] = get_audio_duration(seg["audio_file"])
        print(f"  [OK] {seg['id']}: Thời lượng {seg['duration']:.1f}s")

    # 2. Tạo các lớp Overlay PNG
    print("\n--- BƯỚC 2: Thiết kế Banner, Phụ đề và CTA 9:16 ---")
    for idx, seg in enumerate(SEGMENTS, 1):
        overlay_path = OVERLAY_DIR / f"{seg['id']}_overlay.png"
        print(f"  [{idx}/4] Tạo overlay đồ họa cho: {seg['id']}...")
        create_overlay_png(overlay_path, seg['title_badge'], seg['badge_color'], seg['subtitle'])
        seg['overlay_path'] = overlay_path

    # 3. Cắt ghép từng phân đoạn video thật
    print("\n--- BƯỚC 3: Cắt đoạn đắt giá từ video thật + Ráp âm thanh & Banner ---")
    segment_outputs = []
    total_duration = 0

    for idx, seg in enumerate(SEGMENTS, 1):
        out_seg = OUTPUT_DIR / f"real_seg_{idx}_{seg['id']}.mp4"
        print(f"  [{idx}/4] Cắt & dựng phân cảnh thật: {seg['id']} (Bắt đầu {seg['start']}s, Dài {seg['duration']:.1f}s)...")
        ok = render_seller_segment(
            SOURCE_VIDEO,
            seg['start'],
            seg['duration'],
            seg['overlay_path'],
            seg['audio_file'],
            out_seg
        )
        if ok:
            segment_outputs.append(out_seg)
            total_duration += seg['duration']
        else:
            print(f"  [LỖI] Không thể dựng phân cảnh {seg['id']}")

    # 4. Xuất video hoàn chỉnh
    print("\n--- BƯỚC 4: Xuất bản Video KOC hoàn chỉnh ---")
    final_video = OUTPUT_DIR / "affiliate_REAL_DEMO_chopper.mp4"
    if concat_segments(segment_outputs, final_video):
        size_mb = os.path.getsize(final_video) / (1024 * 1024)
        print("\n" + "=" * 70)
        print("  🎉 XUẤT BẢN THÀNH CÔNG VIDEO AFFILIATE NGƯỜI THẬT VIỆC THẬT!")
        print(f"  -> File video thành phẩm: {final_video}")
        print(f"  -> Thời lượng video: {total_duration:.1f} giây")
        print(f"  -> Kích thước: {size_mb:.2f} MB")
        print(f"  -> Độ phân giải: 1080x1920 (Chuẩn dọc 9:16)")

        # Tự động đồng bộ sang Google Drive nếu máy đã cài Google Drive Desktop
        gdrive_folder = pathlib.Path("G:/My Drive/Affiliate_Videos")
        if gdrive_folder.parent.exists():
            gdrive_folder.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copyfile(final_video, gdrive_folder / final_video.name)
            print(f"  -> [TỰ ĐỘNG SYNC] Đã sao chép sang Google Drive: {gdrive_folder / final_video.name}")
        print("=" * 70)
    else:
        print("Lỗi ghép video.")


if __name__ == "__main__":
    main()
