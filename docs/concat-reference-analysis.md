# ConCat: điều đáng học cho affiliate agent

**Quan sát ngày 23/10/2026.** Nguồn là ảnh người dùng gửi và [trang nhật ký ConCat](https://concat-48b.pages.dev/). Đây là thông tin trang tự công bố, chưa có đối soát độc lập từ Meta hay đơn hàng.

## Điều ConCat thể hiện tốt

- Có mục tiêu và mốc thời gian rõ: được giao vốn, có hạn cuối.
- Có vòng quyết định: chọn sản phẩm, dừng chiến dịch kém, tăng ngân sách chiến dịch tốt.
- Có nhật ký giờ, lý do, số liệu theo sản phẩm, tình trạng máy/agent và thời điểm chạy gần nhất.
- Công khai trạng thái chạy thử: quyết định được ghi nhưng chưa thực thi trên Facebook.

## Ranh giới của số liệu trong ảnh

| Số hiển thị | Phép tính hoặc ý nghĩa |
|---|---|
| ROAS 3,82 | 55.109.000đ doanh thu đơn đặt / 14.427.867đ chi quảng cáo ≈ 3,82 |
| “Lãi” 40.681.133đ | 55.109.000đ − 14.427.867đ; chưa phải lợi nhuận ròng |
| “Số dư” 60.681.133đ | 20.000.000đ vốn + khoản chênh trên |

Trang ghi doanh thu dựa trên **đơn đặt, chưa trừ hoàn/bom** và các quyết định lúc chụp **chưa bấm thật trên Facebook**. Vì thế ảnh chứng minh cách trình bày nhật ký và phép tính, không chứng minh agent đã tự chạy quảng cáo hoặc tạo 40,68 triệu đồng lợi nhuận thực.

## Đã lãi ròng chưa?

**Chưa thể kết luận.** 40.681.133đ là số còn lại tối đa để trả giá vốn hàng, phí sàn/thanh toán, giao hàng, hoàn/bom, nhân công, sản xuất nội dung, phần mềm và thuế. Nếu tổng các khoản này lớn hơn 40.681.133đ thì hoạt động lỗ; nhỏ hơn thì mới có lãi. ConCat chưa công bố đủ các khoản ấy hay doanh thu đã thu tiền.

- Doanh thu đơn đặt bình quân: khoảng **492.045đ/đơn** (55.109.000đ / 112).
- Quảng cáo bình quân: khoảng **128.820đ/đơn** (14.427.867đ / 112).
- Muốn hòa vốn **chỉ tính quảng cáo**, lãi gộp trước quảng cáo phải lớn hơn **26,18%** doanh thu đơn đặt (14.427.867đ / 55.109.000đ). Ngưỡng thật còn cao hơn khi trừ các chi phí khác và đơn không hoàn tất.
- Ví dụ nếu giá vốn chiếm 70% doanh thu đơn đặt, lãi gộp 30% là 16.532.700đ. Trừ quảng cáo còn **2.104.833đ**, vẫn chưa trừ các khoản còn lại; đây là tình huống giả định, không phải kết quả thực của ConCat.

Nếu sao chép mô hình **affiliate có chạy quảng cáo**, khoản thực thu là hoa hồng, không phải 55.109.000đ GMV. Với đúng GMV và mức chi quảng cáo trong ảnh, hoa hồng hiệu dụng cần vượt **26,18% GMV** chỉ để trả quảng cáo. Vì vậy không được suy ra khả năng sinh lãi của affiliate từ ROAS 3,82 của một cửa hàng bán hàng.

## Áp dụng vào hệ thống affiliate

1. Mỗi quyết định có `ActionRecord`: dữ liệu đầu vào, lý do, phương án, trạng thái `PROPOSED`/`SIMULATED`/`PREPARED`/`EXECUTED`/`VERIFIED`, kết quả sau đó. Hành động trên nền tảng cần ID nền tảng và đối soát; hành động nội bộ cần ID/phiên bản artifact và kiểm tra tồn tại. Nhật ký không được gọi quyết định là hành động nếu chưa có bằng chứng thực thi.
2. Dashboard có chế độ `simulation`/`assisted`/`live`, lần chạy gần nhất, lần đồng bộ dữ liệu gần nhất và cảnh báo dữ liệu cũ. Khi dữ liệu cũ, không hiển thị kết quả như thể vừa cập nhật.
3. Báo cáo tiền theo affiliate: GMV của đơn hàng, hoa hồng chờ, hoa hồng xác nhận, hoa hồng đã trả, hủy/hoàn, chi phí mẫu, chi phí sản xuất, chi phí quảng cáo. **GMV không phải doanh thu của creator.**
4. Bản MVP organic dùng vòng *tìm sản phẩm → video → đo giữ chân/click/hoa hồng → đổi giả thuyết*. Nếu về sau có ads, thêm giới hạn chi tiêu theo ngày/tổng, điều kiện tự dừng, chống gửi lệnh trùng và công tắc dừng.

Các thay đổi về ActionRecord, nhãn chế độ vận hành và đối soát affiliate đã được đưa vào `aff-orchestrator` và `aff-growth-analyst` trong bộ skill.
