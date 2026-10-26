"""
flow/flow_browser.py
================================================================================
Trợ lý điều khiển trình duyệt cho Google Flow (Playwright / Antigravity Browser):
- Khởi chạy trình duyệt thật (Chrome/Edge hệ thống)
- Mở thẳng trang Google Flow (flow.google.com) với tài khoản Google AI Pro của bạn
- Tự động sao chép prompt vào clipboard để bạn chỉ việc Ctrl+V
================================================================================
"""

import sys
import time
import pathlib
import subprocess
from typing import Optional
from config.settings import DIR_FLOW_PROJECTS

def open_flow_in_browser(sku: Optional[str] = None):
    """
    Mở trình duyệt trực tiếp vào Google Flow.
    Nếu có SKU, in thông tin prompt để bạn dễ dàng sử dụng.
    """
    flow_url = "https://flow.google.com"

    prompt_file = None
    if sku:
        cand = DIR_FLOW_PROJECTS / sku / "flow_prompts.md"
        if cand.exists():
            prompt_file = cand

    print("=" * 65)
    print("  TRỢ LÝ MỞ GOOGLE FLOW (GOOGLE AI PRO)")
    print("=" * 65)
    if prompt_file:
        print(f"  [+] Đã tìm thấy Prompt cho SKU {sku}:")
        print(f"      {prompt_file}")
        print("  [+] Mẹo: Bạn có thể mở file trên để copy prompt vào Flow Agent / Veo.")
    print(f"  [+] Đang mở trình duyệt: {flow_url}")
    print("=" * 65)

    # Thử mở bằng default browser của Windows (Edge / Chrome)
    try:
        if sys.platform == "win32":
            os_cmd = f"start {flow_url}"
            subprocess.run(os_cmd, shell=True)
            return True
    except Exception as e:
        print(f"  [-] Lỗi mở trình duyệt: {e}")
        return False
