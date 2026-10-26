# Dựng video affiliate với ChatGPT Plus

**Quyết định ban đầu — 23/10/2026:** tận dụng ChatGPT Plus cho nghiên cứu, ý tưởng, kịch bản, storyboard và review; dựng video tự động bằng footage có quyền sử dụng và renderer local. **Cập nhật 26/10/2026:** người dùng đã có Google AI Pro; dùng credit Flow để thử cảnh bổ trợ theo [quyết định công cụ mới](production-tools.md), chưa cần mở Gemini API trả tiền cho MVP.

## Vì sao

- [OpenAI đã công bố](https://developers.openai.com/api/docs/deprecations) **Sora 2 API và Videos API** ngừng ngày **24/09/2026**. Đây là thông tin về API; kết hợp với giới hạn OAuth bên dưới, hiện không có đường tạo video tự động bằng ChatGPT Plus phù hợp để làm backend cho controller.
- [Sign in with ChatGPT qua OAuth](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations) dùng được cho một số yêu cầu LLM đủ điều kiện, nhưng hiện không có hosted image generation, native computer use hay video generation trên đường này. Đăng nhập Plus không tự cấp quyền cho các dịch vụ media API khác.
- Với affiliate, cảnh sản phẩm **thật** đang dùng giải quyết vấn đề tốt hơn một clip AI đẹp nhưng không chứng minh đúng SKU. Video AI có thể dùng làm cảnh mở hoặc bối cảnh khi phù hợp; không thay cho bằng chứng sản phẩm.

## Pipeline đề xuất

1. Product role chọn SKU, kiểm tra hoa hồng, quyền dùng ảnh/clip, và xác định cảnh nào cần tự quay. Nếu thiếu bằng chứng, trả một shot list ngắn cho người dùng hoặc lấy asset được người bán cho phép.
2. ChatGPT Plus/LLM tạo 2–3 concept, first frame, lời thoại, storyboard và giả thuyết A/B. Reviewer độc lập kiểm tra tính hấp dẫn và claim.
3. Renderer local cắt footage thật, thêm chữ/phụ đề, voice/audio có quyền, hình minh họa, CTA và biến thể hook; xuất 9:16, ảnh frame đầu, manifest nguồn và chi phí. [Remotion](https://www.remotion.dev/docs/render) là lựa chọn hợp với developer React; [giấy phép miễn phí cho cá nhân/nhóm tối đa ba người](https://www.remotion.dev/docs/license/faq) hiện cho phép tự động hóa thương mại. FFmpeg là backend thay thế/giai đoạn đầu tùy cách dựng.
4. Video reviewer xem bản export ở cỡ điện thoại, cả bật và tắt tiếng; đối chiếu cảnh chứng minh với SKU thật. Sau khi đăng, analyst gắn phiên bản video với retention, click, hoa hồng và chi phí để chọn hook tiếp theo.

**Nút thắt vận hành:** renderer chỉ chạy hoàn toàn tự động khi đã có footage/ảnh của đúng SKU với quyền sử dụng rõ ràng. Với sản phẩm mới chưa có cảnh chứng minh, pipeline trả `NEEDS_SHOT`: một danh sách cảnh ngắn để người dùng quay không lộ mặt hoặc xin người bán asset hợp lệ. Agent không bù chỗ thiếu bằng cảnh sản phẩm tưởng tượng.

## Khi nào mới cần dịch vụ video AI riêng

Chỉ thêm `GenerativeVideoProvider` khi một thử nghiệm cụ thể cần cảnh không thể tự quay/không có asset hợp lệ, và mẫu đầu ra qua được review về độ thật, quyền sử dụng, **chi phí trên một video hoàn chỉnh được duyệt** và tác động tới hoa hồng xác nhận. Đặt trần tiền theo lần render; provider này là tùy chọn, có thể thay thế mà không đổi storyboard, journal hoặc renderer. Không dựa vào video tạo sinh để mô phỏng công dụng chưa được kiểm chứng.

**Nguồn lực tối thiểu:** điện thoại quay tay/sản phẩm hoặc footage được cấp quyền, một bộ template dựng local, tài khoản ChatGPT Plus đang có. Chi phí phát sinh đầu tiên có khả năng là mẫu sản phẩm, footage/voice có quyền và thời gian tạo asset; không cần mua thêm một gói “AI video” trước khi chứng minh video đầu có tín hiệu bán hàng.
