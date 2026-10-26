# Báo cáo Khoảng trống Dữ liệu (Research Gaps)

- **Dự án:** `affiliate-agent-kit`
- **Thời điểm lập:** 2026-10-26 14:29:05
- **Mục đích:** Liệt kê minh bạch những thông tin chưa thể xác minh trên kênh mới và kế hoạch thu thập dữ liệu thực nghiệm.

---

## 1. Những Dữ liệu Hiện Chưa Có (UNKNOWN)

| Dữ liệu | Trạng thái | Lý do chưa có | Cách khắc phục trong Giai đoạn 2 & 3 |
|---|---|---|---|
| **CTR vào Giỏ hàng thực tế của kênh** | `UNKNOWN` | Kênh chưa đăng video nào, chưa có hành vi người xem thật | Chạy thử 6 video đầu tiên và đo lường qua TikTok Creator Analytics |
| **CVR (Tỷ lệ chuyển đổi sau khi click)** | `UNKNOWN` | Chưa có dữ liệu checkout thực tế từ link affiliate | Theo dõi báo cáo hoa hồng TikTok Shop định kỳ (7-14 ngày) |
| **Tỷ lệ giữ chân 3s (3s Retention Rate)** | `UNKNOWN` | Thuật toán phân phối TikTok cần video thực tế để xếp hạng | Thử nghiệm 2 dạng hook đối lập (Visual sốc vs Nỗi đau bực mình) |
| **Quyền gắn link giỏ hàng chính xác** | `PENDING_VERIFY` | Chính sách TikTok Shop VN yêu cầu điều kiện tài khoản | Kiểm tra tab TikTok Shop Creator Center trên điện thoại của bạn |
| **Tỷ lệ hoàn hàng / Hủy đơn thực tế** | `ESTIMATED_5-8%` | Chỉ quan sát được đánh giá sao của shop, chưa có số đơn hủy | Chỉ hợp tác với gian hàng có đánh giá >= 4.7* và tỷ lệ phản hồi > 90% |

---

## 2. Kế hoạch Đóng Khoảng trống Dữ liệu (Sprint 2)

1. **Sau khi đăng 6 video thử nghiệm (2 video/ngách):**
   - Xuất file báo cáo TikTok Creator Analytics (hoặc nhập thủ công qua lệnh `python cli.py log-metrics`).
   - Cập nhật các trường `UNKNOWN` thành số liệu thực tế của kênh.
2. **Kích hoạt Growth Intelligence Engine:**
   - Phân loại video theo 4 trạng thái: Low Views / Improve Clicks / Improve Conversions / Scalable.
   - Quyết định STOP / ITERATE / SCALE dựa trên số liệu thực tế, không dựa trên cảm tính.
