"""
engine/drive_exporter.py
================================================================================
Xuất bản tự động ra Google Drive Desktop (Tầng 08_Ready_To_Post):
- Đóng gói đầy đủ: video_final.mp4, caption.txt, product_links.txt, product_info.json, quality_report.json
- Phân loại theo ngày và SKU: 08_Ready_To_Post/YYYY-MM-DD/SKU/
- Kèm hướng dẫn nhanh POST_INSTRUCTIONS.md chứa sẵn LINK SẢN PHẨM để bạn gắn vào video trong 5 giây
================================================================================
"""

import os
import json
import shutil
import datetime
import pathlib
from typing import Dict, Any, Optional

from config.settings import DIR_READY_TO_POST
from engine.database import record_artifact, log_event, upsert_product

class DriveExporter:
    """Đóng gói và xuất sản phẩm hoàn chỉnh ra Google Drive Desktop."""

    @staticmethod
    def export_package(
        sku: str,
        video_path: pathlib.Path,
        caption_text: str,
        product_info: Dict[str, Any],
        quality_report: Dict[str, Any]
    ) -> pathlib.Path:
        """Đóng gói và xuất ra thư mục 08_Ready_To_Post trên Google Drive."""
        today_str = datetime.date.today().isoformat()
        target_dir = DIR_READY_TO_POST / today_str / sku
        target_dir.mkdir(parents=True, exist_ok=True)

        title = product_info.get("title", "")
        tiktok_url = product_info.get("tiktok_url") or f"https://shop.tiktok.com/view/product/search?q={title.replace(' ', '+')}"
        shopee_url = product_info.get("shopee_url") or f"https://shopee.vn/search?keyword={title.replace(' ', '+')}"
        product_id = product_info.get("product_id") or sku

        # 1. Sao chép Video thành phẩm
        final_video_name = "video_final.mp4"
        dest_video = target_dir / final_video_name
        shutil.copy2(str(video_path), str(dest_video))

        # 2. Tạo caption.txt
        caption_file = target_dir / "caption.txt"
        with open(caption_file, "w", encoding="utf-8") as f:
            f.write(caption_text.strip() + "\n")

        # 3. Tạo product_links.txt (RẤT TIỆN LỢI ĐỂ BẠN CLICK HOẶC COPY GẮN GIỎ HÀNG)
        links_file = target_dir / "product_links.txt"
        links_content = f"""LIÊN KẾT SẢN PHẨM ĐỂ GẮN VÀO VIDEO
================================================================================
Sản phẩm: {title}
Mã SKU:   {sku}
Hoa hồng: {product_info.get('commission_rate', 0)*100:.1f}% (~ {product_info.get('commission_vnd', 0):,.0f} đ/đơn)

1. TỪ KHÓA TÌM TRONG GIỎ HÀNG TIKTOK (Copy dán vào thanh tìm kiếm giỏ hàng):
   {title}

2. LINK SẢN PHẨM TRÊN TIKTOK SHOP:
   {tiktok_url}

3. LINK SẢN PHẨM TRÊN SHOPEE (Nếu đăng Shopee Video):
   {shopee_url}
================================================================================
"""
        with open(links_file, "w", encoding="utf-8") as f:
            f.write(links_content)

        # 4. Tạo product_info.json
        info_file = target_dir / "product_info.json"
        clean_info = {
            "sku": sku,
            "title": title,
            "price_vnd": product_info.get("price_vnd", 0),
            "commission_rate": product_info.get("commission_rate", 0),
            "commission_vnd": product_info.get("commission_vnd", 0),
            "tiktok_product_url": tiktok_url,
            "shopee_product_url": shopee_url,
            "product_search_keyword": title,
            "target_platform": "TikTok Shop & Shopee Video",
            "evidence_grade": product_info.get("evidence_grade", "B"),
            "exported_at": datetime.datetime.now().isoformat()
        }
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(clean_info, f, ensure_ascii=False, indent=2)

        # 5. Lưu quality_report.json
        report_file = target_dir / "quality_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)

        # 6. Tạo hướng dẫn đăng bài nhanh cho bạn (POST_INSTRUCTIONS.md)
        instr_file = target_dir / "POST_INSTRUCTIONS.md"
        instr_content = f"""# HƯỚNG DẪN ĐĂNG BÀI NHANH (TIKTOK SHOP / SHOPEE VIDEO)

**Sản phẩm:** {title}  
**Mã SKU:** `{sku}`  
**Tệp video:** `{final_video_name}`  

---

### 🔗 LINK SẢN PHẨM ĐỂ GẮN VÀO BÀI ĐĂNG (BẮT BUỘC):
- **Link TikTok Shop:** [{tiktok_url}]({tiktok_url})
- **Link Shopee:** [{shopee_url}]({shopee_url})
- **Từ khóa tìm trong kho Affiliate:** `{title}`

---

### CÁC BƯỚC BẠN THỰC HIỆN TRÊN ĐIỆN THOẠI / MÁY TÍNH (1 PHÚT):
1. **Mở TikTok App / TikTok Studio** (hoặc ứng dụng Shopee Video).
2. **Tải lên video:** Chọn file `{final_video_name}` trong thư mục này.
3. **Dán Caption:** Mở file `caption.txt`, copy toàn bộ nội dung và dán vào phần mô tả video.
4. **Gắn giỏ hàng (QUAN TRỌNG ĐỂ CÓ HOA HỒNG):**
   - Bấm **Thêm liên kết (Add Link) -> Sản phẩm (Product)**.
   - Dán từ khóa `{title}` vào ô tìm kiếm hoặc dán link sản phẩm.
   - Chọn đúng shop chính hãng có mức hoa hồng **{product_info.get('commission_rate', 0)*100:.1f}%**.
5. **Bật nhãn công bố AI (AIGC):**
   - Vào mục **Cài đặt khác (More options)**.
   - Bật công tắc **"Nội dung do AI tạo" (AI-generated content)** để kênh an toàn 100%, không lo vi phạm chính sách quét của TikTok.
6. **Bấm Đăng (Post):** Hoàn thành!
"""
        with open(instr_file, "w", encoding="utf-8") as f:
            f.write(instr_content)

        # Cập nhật trạng thái sản phẩm
        upsert_product(
            sku=sku,
            title=title,
            price_vnd=product_info.get("price_vnd", 0),
            commission_rate=product_info.get("commission_rate", 0),
            status="READY_TO_POST"
        )

        record_artifact(sku, "PUBLISH_PACKAGE", str(target_dir))
        log_event(sku, "EXPORTED_TO_GOOGLE_DRIVE", {"path": str(target_dir)})

        return target_dir
