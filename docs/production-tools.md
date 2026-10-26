# Chọn công cụ sản xuất video khi đã có Google AI Pro

**Rà soát ngày 26/10/2026.** Quyết định cho MVP: dùng ChatGPT Plus cho nghiên cứu, kịch bản và reviewer; dùng Google AI Pro **qua Flow** để thử vài cảnh tạo sinh bằng credit sẵn có; dựng bản video affiliate cuối cùng bằng footage thật và renderer local. Chưa mở billing Gemini API chỉ vì đã có gói Pro.

## Khả năng của từng công cụ

| Công cụ | Có thể dùng ngay | Vai trò trong hệ chạy nền | Chi phí/quyền cần kiểm tra |
|---|---|---|---|
| ChatGPT Plus + Codex | Lập concept, hook, storyboard, phân tích và review. CLI hiện đăng nhập; controller vẫn phải thử một job thực. | LLM worker theo từng job hữu hạn. | OAuth/CLI quota và quyền tool; không là API tạo video. [Giới hạn OAuth OpenAI](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations). |
| Google AI Pro + Flow | Thử các cảnh bằng Veo 3.1/Gemini Omni qua UI, tải asset được duyệt về thư viện. | Nhánh thử nghiệm có người vận hành; **không giả định có Flow API tự động**. | [Google Flow Help](https://support.google.com/flow/answer/16526234) ghi Pro có thêm 1.000 credit/tháng; giá theo mỗi generation, có thể có nhiều generation trong một request. Kiểm tra số credit và model trong chính tài khoản trước khi chạy. |
| Remotion | Cắt clip, dựng 9:16, chữ, phụ đề, nhạc, nhiều biến thể hook và xuất file tự động. | Renderer mặc định của pipeline. | [Docs render](https://www.remotion.dev/docs/render); [free license](https://www.remotion.dev/docs/license/faq) hiện áp dụng cho cá nhân/nhóm tối đa ba người, kể cả automation thương mại. |
| Gemini API: Omni Flash/Veo | Gọi video generation/edit bằng code sau khi mở Google AI Studio/Cloud Billing. | Provider tùy chọn khi cần **tự động hóa generation** và đã chứng minh hiệu quả. | Flow credit không trả cho API; cần Cloud Billing riêng. Google AI Pro có thể kèm **$10 Google Cloud credit/tháng** nếu liên kết gói với Google Developer Profile và đủ điều kiện ([Google One](https://support.google.com/googleone/answer/14534406), [Developer Program FAQ](https://developers.google.com/profile/help/faq)). Kiểm tra credit có áp dụng cho Gemini API và điều kiện prepay trước khi dùng. [Giá API hiện hành](https://ai.google.dev/gemini-api/docs/pricing) cần tính theo video được duyệt, không chỉ giá một lần gọi. |

## Phép thử trước khi mua thêm

1. Chọn **một SKU thật** có hoa hồng, asset hợp lệ và cảnh sử dụng rõ ràng. Tạo 2–3 video bằng cùng footage thật với hook khác nhau; Remotion dựng và reviewer kiểm tra. Đây là baseline không tốn phí tạo video AI.
2. Dùng credit Flow hiện có để thử **một cảnh bổ trợ** (ví dụ tình huống vấn đề hoặc bối cảnh). Tải asset, ghi prompt, model, credit, số lần tạo, quyền sử dụng và lỗi trong manifest. Không dùng clip AI làm bằng chứng công dụng hay mô phỏng sai đúng SKU.
3. So sánh **chi phí trên video hoàn chỉnh được reviewer duyệt**, thời gian làm, retention/click và cuối cùng hoa hồng xác nhận. Nếu cần Gemini API, liên kết Google AI Pro với Google Developer Profile, xác nhận $10 Cloud credit trong billing và kiểm tra điều kiện prepay. Chỉ mở API khi cảnh AI cải thiện một khâu đo được và cần đưa vào pipeline tự chạy thường xuyên.

Google [liệt kê Việt Nam là vùng dùng Flow](https://support.google.com/flow/answer/16353544), nhưng tính năng có thể khác theo vùng/tài khoản. [Credit Flow](https://support.google.com/flow/answer/16526234) hiện ghi Veo 3.1 Lite 10 credit, Fast 20 credit và Quality 100 credit mỗi generation cho người dùng không phải Ultra; đây là mức tham khảo tại ngày rà soát, không phải định mức cố định cho từng video thành phẩm.

## Khuyến nghị triển khai

`ProductBrief → CreativePlan → footage/asset library → Remotion render → reviewer → PublishRecord` là đường chính. `Flow experiment` là nhánh chọn lọc; `GeminiVideoProvider` chỉ là adapter tùy chọn sau capability và economics test. Tách nhà cung cấp AI khỏi renderer và journal để một gói hết credit, lỗi hoặc đổi giá không làm dừng cả hệ thống.

Điểm chưa tự động được bằng công cụ nào: sản phẩm mới thiếu footage chứng minh thật. Khi đó `aff-video-producer` trả `NEEDS_SHOT` với shot list ngắn cho người dùng quay không lộ mặt hoặc xin asset hợp lệ từ seller. Không đăng video thuyết phục bằng hình sản phẩm được AI tưởng tượng.
