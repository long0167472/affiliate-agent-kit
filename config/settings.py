"""
config/settings.py
================================================================================
Cấu hình trung tâm cho Affiliate Factory:
- Tự động nhận diện Google Drive Desktop (G:\\My Drive)
- Khởi tạo cấu trúc 8 thư mục tiêu chuẩn
- Đường dẫn FFmpeg, Fonts Windows, SQLite Database
================================================================================
"""

import os
import sys
import pathlib
import imageio_ffmpeg

# Thư mục gốc dự án
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database SQLite (WAL Mode)
DB_PATH = DATA_DIR / "affiliate_factory.db"

# Nhận diện Google Drive Desktop
def detect_google_drive_path() -> pathlib.Path:
    # 1. Biến môi trường tùy chỉnh
    custom_path = os.getenv("AFFILIATE_DRIVE_DIR")
    if custom_path and pathlib.Path(custom_path).exists():
        return pathlib.Path(custom_path)

    # 2. Ổ đĩa G:\ thông dụng của Google Drive Desktop trên Windows
    drive_g = pathlib.Path("G:/My Drive")
    if drive_g.exists():
        return drive_g

    # 3. Tìm trong thư mục User profile
    user_home = pathlib.Path.home()
    candidates = [
        user_home / "Google Drive" / "My Drive",
        user_home / "Google Drive",
        user_home / "OneDrive",
    ]
    for cand in candidates:
        if cand.exists():
            return cand

    # 4. Fallback về thư mục output cục bộ
    return BASE_DIR / "output" / "Google_Drive_Emulated"

GOOGLE_DRIVE_ROOT = detect_google_drive_path()
FACTORY_ROOT = GOOGLE_DRIVE_ROOT / "Affiliate Factory"

# Cấu trúc 8 thư mục tiêu chuẩn theo kiến trúc đề xuất
DIR_PRODUCT_RESEARCH  = FACTORY_ROOT / "01_Product_Research"
DIR_APPROVED_ASSETS   = FACTORY_ROOT / "02_Approved_Assets"
DIR_SCRIPTS           = FACTORY_ROOT / "03_Scripts"
DIR_FLOW_PROJECTS     = FACTORY_ROOT / "04_Flow_Projects"
DIR_RAW_VIDEOS        = FACTORY_ROOT / "05_Raw_Videos"
DIR_RENDERED_VIDEOS   = FACTORY_ROOT / "06_Rendered_Videos"
DIR_QUALITY_REPORTS   = FACTORY_ROOT / "07_Quality_Reports"
DIR_READY_TO_POST     = FACTORY_ROOT / "08_Ready_To_Post"

STANDARD_DIRS = [
    DIR_PRODUCT_RESEARCH,
    DIR_APPROVED_ASSETS,
    DIR_SCRIPTS,
    DIR_FLOW_PROJECTS,
    DIR_RAW_VIDEOS,
    DIR_RENDERED_VIDEOS,
    DIR_QUALITY_REPORTS,
    DIR_READY_TO_POST,
]

def init_directories():
    """Tự động tạo đầy đủ cây thư mục nếu chưa tồn tại."""
    for d in STANDARD_DIRS:
        d.mkdir(parents=True, exist_ok=True)

# Khởi tạo ngay khi nạp module
init_directories()

# Công cụ đa phương tiện & Fonts
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Font Windows mặc định hỗ trợ tiếng Việt đầy đủ dấu
FONT_BOLD = "C:\\Windows\\Fonts\\arialbd.ttf"
FONT_REGULAR = "C:\\Windows\\Fonts\\arial.ttf"
FONT_SEGOE_BOLD = "C:\\Windows\\Fonts\\seguisb.ttf"

# Cấu hình Video 9:16 chuẩn TikTok / Shopee
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
DEFAULT_VOICE = "vi-VN-HoaiMyNeural"  # Giọng nữ miền Nam truyền cảm, phổ biến video review
ALT_VOICE = "vi-VN-NamMinhNeural"     # Giọng nam miền Bắc năng động, giật tít
