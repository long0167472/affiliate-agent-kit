# Affiliate Agent Kit

Bộ thiết kế cho hệ affiliate TikTok Shop và Shopee Video của một developer: các role skill chuyên sâu, hợp đồng dữ liệu, nhật ký học hằng ngày, và kiến trúc controller chạy nền. **Đây là bộ nguồn để xây hệ thống, chưa phải một agent đang tự đăng video hay tiêu tiền.**

## Trong thư mục

| Đường dẫn | Nội dung |
|---|---|
| [`skills/`](skills/INDEX.md) | 7 skill: product intelligence, creative strategist, video producer, publisher, growth analyst, reviewer, orchestrator. Mỗi skill có `references/` riêng để cài độc lập. |
| [`docs/affiliate-controller-architecture.md`](docs/affiliate-controller-architecture.md) | Service chạy nền, queue bền vững, recovery, OAuth ChatGPT và ranh giới quyền nền tảng. |
| [`docs/production-tools.md`](docs/production-tools.md) | Quyết định công cụ video khi đã có ChatGPT Plus và Google AI Pro. |
| [`docs/affiliate-video-production-decision.md`](docs/affiliate-video-production-decision.md) | Pipeline dựng từ footage thật và điểm dừng `NEEDS_SHOT`. |
| [`docs/affiliate-account-decision.md`](docs/affiliate-account-decision.md) | Tách đời tư và lộ trình tài khoản mới. |
| [`docs/concat-reference-analysis.md`](docs/concat-reference-analysis.md) | Điều học từ nhật ký ConCat và cách đọc đúng số lãi. |
| [`scripts/install-skills.ps1`](scripts/install-skills.ps1) | Cài bản sao các skill từ repo vào Codex trên Windows. |
| [`scripts/install-skills-antigravity.ps1`](scripts/install-skills-antigravity.ps1) | Cài bản sao các skill từ repo vào Antigravity (`.agents/skills/` và `~/.gemini/config/skills/`). |

## Bắt đầu

1. Đọc [quyết định công cụ](docs/production-tools.md) và [kiến trúc controller](docs/affiliate-controller-architecture.md).
2. Cài đặt skill tương ứng với công cụ bạn dùng:
   - Dành cho **Codex**: chạy `powershell -File .\scripts\install-skills.ps1` (hoặc `pwsh`). Thêm `-Force` khi cần ghi đè.
   - Dành cho **Antigravity**: chạy `powershell -ExecutionPolicy Bypass -File .\scripts\install-skills-antigravity.ps1 -Force`. Script sẽ thiết lập cả workspace skills (`.agents/skills/`) và global skills (`~/.gemini/config/skills/`).
3. Xây controller theo thứ tự trong tài liệu: queue/journal và chế độ giả lập trước; sau đó mới kết nối tài khoản, asset, renderer, publisher và số liệu.
4. Trước khi cấp quyền đăng, xác minh **trên tài khoản thật** quyền gắn sản phẩm và khả năng đọc lại bài đã đăng. Đăng video thường không chứng minh đăng được video affiliate có SKU.

## Ranh giới hiện tại

- Chưa có source code controller, connector TikTok/Shopee, renderer, OAuth SIWC hay lịch chạy đã cấu hình.
- Không lưu token, API key, ảnh đơn hàng có thông tin người mua hoặc footage không có quyền sử dụng trong repo.
- Số liệu/điều kiện nền tảng và giá công cụ được ghi theo ngày nghiên cứu; kiểm tra lại khi triển khai.

Nguồn tham khảo chính nằm ngay trong từng tài liệu và `skills/references/`. Repo đã được khởi tạo trên nhánh `main`; thêm remote của bạn để đẩy lên Git. Không có thông tin đăng nhập hoặc dữ liệu vận hành thật.
