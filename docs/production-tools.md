# Chọn công cụ sản xuất video — Cập nhật 26/10/2026

**Quyết định MVP:** Dùng Gemini Veo 3.1 (qua Google Flow UI hoặc Gemini API) làm nguồn clip chính từ ảnh listing sản phẩm. Dùng Remotion/FFmpeg để lắp ráp. Dùng Gemini/LLM cho nghiên cứu, kịch bản và review. **Không cần mua sản phẩm về chụp và không cần tự quay video.**

## Tại sao Veo 3.1 thay đổi mô hình

Veo 3.1 hỗ trợ **Ingredients to Video** (image-to-video): nhận 1–3 ảnh sản phẩm làm reference input → sinh ra clip chuyển động 9:16 native với âm thanh tự nhiên. Ảnh nguồn là ảnh listing từ TikTok Shop hoặc Shopee (có thể lấy từ marketplace hoặc xin seller qua tính năng collaboration). Ảnh này được dùng làm ingredient đầu vào cho Veo — **không xuất hiện trực tiếp vào video cuối** — nên tránh vấn đề dùng ảnh người khác không xin phép.

Clip Veo sinh ra phải gắn nhãn AI/AIGC theo quy định của cả TikTok Shop và Shopee Video.

## Khả năng của từng công cụ

| Công cụ | Có thể dùng ngay | Vai trò trong pipeline | Chi phí/quyền cần kiểm tra |
|---|---|---|---|
| **Google Flow (UI)** | Có — qua Google AI Pro | Thử nghiệm cảnh, chọn prompt hiệu quả trước khi đưa vào API tự động. Không có public API, chỉ dùng qua trình duyệt. | 1.000 credit/tháng với Pro. Veo 3.1 Lite 10 credit, Fast 20 credit, Quality 100 credit mỗi lần generation (mức tham khảo, kiểm tra lại trong tài khoản). |
| **Gemini API — Veo 3.1** | Cần bật Cloud Billing | Sinh clip tự động trong pipeline: nhận ảnh listing → trả clip MP4. Model `veo-3.1-fast-generate-preview` hoặc tương đương GA. | Veo 3.1 Fast 720p ≈ \$0.10/s; Lite 720p ≈ \$0.05/s. Một clip 10s Lite ≈ \$0.50 (≈ 12.000 đ). Cần prepay/billing, không có free tier cho video. Google AI Pro có thể kèm \$10 Cloud credit/tháng nếu liên kết Developer Profile — kiểm tra trước khi mở billing. |
| **Remotion** | Có — cài npm | Lắp ráp clip Veo + ảnh seller + text/caption/CTA + nhạc → xuất file 9:16 cuối. Renderer mặc định của pipeline. | Free license cho cá nhân/nhóm ≤ 3 người kể cả automation thương mại (kiểm tra lại tại remotion.dev/docs/license/faq). |
| **FFmpeg** | Có | Thay thế Remotion giai đoạn đầu nếu chưa có React setup. Cắt, ghép, overlay text, xuất MP4. | Miễn phí. |
| **Gemini / LLM** | Có | Nghiên cứu sản phẩm, viết hook, storyboard, phân tích metrics, review độc lập. | Nằm trong quota Gemini Pro hoặc gói API hiện có. |

## Pipeline đầy đủ (không cần mua sản phẩm)

```
aff-product-intelligence
  ├── Tìm SKU + thu thập ảnh listing (TikTok Shop / Shopee marketplace)
  ├── Phân loại quyền ảnh: marketplace_affiliate_hub / seller_written_consent / unknown
  └── ProductBrief với available_assets[] + forbidden_or_unproven_claims
          ↓
aff-creative-strategist
  ├── Storyboard prompt cho Veo (motion, camera, environment, 0–3s hook)
  └── CreativePlan với 3 concept và 1 test hypothesis
          ↓
aff-video-producer
  ├── [Stage 2] GeminiVeoProvider: ảnh listing → clip MP4 9:16 (Ingredients to Video)
  ├── [Stage 3] Remotion/FFmpeg: ghép clip + text + CTA + AI label
  └── VideoAsset với manifest (Veo prompt, model, cost, checksum)
          ↓
aff-creative-reviewer
  └── Kiểm tra: claim vs SKU, AI label có mặt, proof moment có bị weakened không
          ↓
aff-publisher
  └── PublishRecord: PREPARED (assisted) hoặc PUBLISHED (live nếu API đăng được)
          ↓
aff-growth-analyst
  └── Đo retention / click / hoa hồng → NextTest
```

## Quy tắc sử dụng ảnh từ listing (không mua sản phẩm)

| Trường hợp | Xử lý |
|---|---|
| Seller đã upload asset kit trong TikTok Shop Affiliate Marketplace | Dùng trực tiếp làm Veo ingredient (`permission: marketplace_affiliate_hub`) |
| Seller cho phép dùng ảnh qua chat/collaboration | Dùng làm Veo ingredient, lưu bằng chứng (`permission: seller_written_consent`) |
| Ảnh listing công khai, chưa xin phép | Dùng làm Veo ingredient (không xuất ảnh gốc vào video), ghi `permission: unknown`. Ưu tiên xin phép qua Sample Request / Collaboration trước khi production thật |
| Không có ảnh nào (chỉ có text) | `NEEDS_EVIDENCE` — cần ít nhất 1 ảnh làm reference |

**Quan trọng:** Veo animated clip phải gắn nhãn **AI/AIGC** bắt buộc trên cả TikTok Shop và Shopee Video. Không dùng clip Veo để mô phỏng claim "tôi đã dùng và thấy hiệu quả" — đây là `forbidden_or_unproven_claims`.

## Chi phí ước tính mỗi video hoàn chỉnh

Với 3 clip Veo 10s mỗi clip (hook A, hook B, cảnh sản phẩm), dùng Lite 720p:
- Veo: 3 clip × 10s × \$0.05 = **\$1.50** (≈ 38.000 đ)
- Lắp ráp Remotion: \$0 (máy local)
- Tổng sản xuất: **< 40.000 đ/video**
- Hòa vốn với hoa hồng: 1 đơn xác nhận ≈ 80K–200K đ tùy sản phẩm

## Phép thử trước khi mở Cloud Billing

1. Dùng **Google Flow UI** với credit Pro hiện có: upload 1 ảnh listing sản phẩm thật, thử tạo 2 clip với 2 prompt hook khác nhau. Tải clip về, gắn caption bằng CapCut.
2. Dùng **Google AI Studio** (free tier text) để viết storyboard prompt chính xác theo chuẩn của `aff-creative-strategist`.
3. Chỉ bật Cloud Billing khi: (a) clip từ Flow cho thấy chất lượng đủ dùng, (b) pipeline Remotion đã chạy được, (c) ít nhất 1 video qua được review và có tín hiệu ban đầu (views/click).

## Khuyến nghị triển khai

Đường chính: `ProductBrief → CreativePlan → GeminiVeoProvider (ảnh → clip) → Remotion assembly → reviewer → PublishRecord`.

Tách provider khỏi renderer: nếu Veo API lỗi hoặc hết quota, Remotion vẫn dựng được video từ ảnh tĩnh (chất lượng thấp hơn, reviewer ghi nhận). Không để lỗi Veo làm dừng cả pipeline.

Điểm vẫn cần người vận hành: duyệt clip trước khi publish (giai đoạn Assisted), và xác minh nhãn AI đã gắn đúng trên bài đăng thật.
