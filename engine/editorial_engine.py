"""
engine/editorial_engine.py
================================================================================
AUDIENCE INTELLIGENCE & EDITORIAL STRATEGY ENGINE
Chuyển đổi từ mô hình "Kênh quảng cáo sản phẩm" sang "Kênh giải quyết vấn đề":
- Định vị kênh: Chuyên gia giải quyết vấn đề + Bóc tách mua sắm thông minh (A + C)
- Quy trình: Audience -> Pain -> Content Strategy -> Solution -> Product -> Affiliate
- Phân bổ 30 Video: 50% Giá trị (0 bán hàng) + 30% Niềm tin/So sánh + 20% Có Affiliate
- Quyền quyết định "KHÔNG BÁN HÀNG" khi vấn đề giải quyết được miễn phí
- Phong cách hình ảnh: Faceless Educational Content (Hình họa thông tin, không giả review)
================================================================================
"""

import os
import sys
import json
import csv
import pathlib
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Đảm bảo in tiếng Việt không lỗi encoding trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config.settings import BASE_DIR
from engine.database import (
    upsert_audience_persona,
    get_audience_persona,
    list_audience_personas,
    save_editorial_plan,
    list_editorial_plan,
    log_event
)

DOCS_SPRINT1_DIR = BASE_DIR / "docs" / "sprint1"
DOCS_SPRINT1_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. HỒ SƠ CHÂN DUNG KHÁN GIẢ MỤC TIÊU (AUDIENCE INTELLIGENCE)
# ─────────────────────────────────────────────────────────────────────────────

PRIMARY_PERSONAS = [
    {
        "id": "persona_rental_living",
        "name": "Người trẻ ở trọ & Tối ưu không gian nhỏ (15–25m²)",
        "archetype": "SMART_CONSUMER_AND_PROBLEM_SOLVER",
        "core_demographic": "Sinh viên, nhân viên văn phòng mới đi làm, độ tuổi 20-30 tại Hà Nội & TP.HCM.",
        "lifestyle_context": "Sống trong phòng trọ hoặc căn hộ dịch vụ nhỏ (15-25m²), thường xuyên đối mặt với tình trạng chật chội, bừa bộn, thiếu ánh sáng và ngân sách chi tiêu hạn hẹp. Ngại khoan đục tường vì chủ nhà phạt cọc.",
        "reasons_to_follow": "Kênh này giúp mình sống tiện nghi, sạch sẽ và ngăn nắp trong không gian hẹp mà không tốn quá nhiều tiền. Đặc biệt là bóc tách giúp mình tránh mua phải những món đồ vô dụng trên mạng.",
        "primary_pains": [
            "Phòng 15m² nhìn đâu cũng thấy đồ, càng mua đồ đựng thì phòng càng chật",
            "Bàn làm việc vừa để laptop, vừa để đồ ăn, dây điện lòng thòng dưới chân",
            "Chủ nhà cấm khoan tường, mua móc dán 10k thì rơi vỡ đồ, hỏng tường",
            "Quần áo phơi trong phòng lâu khô, ẩm mốc và có mùi khó chịu",
            "Xem review TikTok mua cả đống đồ về dùng được 2 hôm vứt xó vì chất lượng tệ"
        ],
        "free_solutions": [
            "Nguyên tắc '1 vào 1 ra' (One in, one out) để kiểm soát đồ đạc phòng nhỏ",
            "Cách phân vùng công năng: ngủ - làm việc - nấu ăn bằng cách bố trí lại tủ kệ sẵn có",
            "Mẹo đi dây điện an toàn bằng dây thun và kẹp bướm văn phòng 0 đồng",
            "Bí quyết tạo đối lưu thông gió phòng trọ khép kín giảm 3 độ C mùa hè"
        ],
        "monetization_opportunities": [
            "Kệ treo không khoan tường chịu lực thật (đã qua kiểm chứng)",
            "Hộp lưu trữ gấp gọn thông minh tận dụng gầm giường / nóc tủ",
            "Khay quản lý dây điện và ổ cắm an toàn chống cháy nổ",
            "Đèn led góc bàn làm việc bảo vệ mắt, không chiếm diện tích"
        ]
    },
    {
        "id": "persona_desk_worker",
        "name": "Dân văn phòng & Freelancer ngồi máy tính 8–10 tiếng",
        "archetype": "SMART_CONSUMER_AND_PROBLEM_SOLVER",
        "core_demographic": "Lập trình viên, designer, marketer, kế toán làm việc tại nhà (Hybrid / Remote).",
        "lifestyle_context": "Ngồi lì một chỗ trước màn hình, hay bị đau mỏi vai gáy, mỏi mắt, bàn làm việc bừa bãi làm giảm khả năng tập trung.",
        "reasons_to_follow": "Giúp nâng cao hiệu suất làm việc, sửa tư thế ngồi tránh thoái hóa đốt sống cổ, và tư vấn đồ setup công thái học chuẩn chỉ, đáng từng xu.",
        "primary_pains": [
            "Mới 3h chiều đã mỏi rã rời cổ và thắt lưng vì ngồi sai tư thế",
            "Bàn làm việc bừa bộn khiến não bộ bị phân tâm, giảm 50% hiệu suất làm việc",
            "Màn hình máy tính quá thấp, gù lưng cúi mặt khi gõ phím",
            "Ánh sáng đèn phòng chói vào màn hình làm mỏi mắt và đau đầu"
        ],
        "free_solutions": [
            "Quy tắc 20-20-20 bảo vệ mắt khỏi ánh sáng xanh",
            "Tư thế ngồi 90-90 chuẩn công thái học không tốn tiền mua ghế công thái học đắt đỏ",
            "Bài tập giãn cơ 3 phút ngay trên ghế văn phòng"
        ],
        "monetization_opportunities": [
            "Giá đỡ laptop chỉnh góc nâng tầm mắt",
            "Đèn treo màn hình chống chói bảo vệ mắt",
            "Kẹp giữ dây cáp chống rối và thảm da trải bàn"
        ]
    }
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. MA TRẬN 30 VIDEO BIÊN TẬP CHIẾN LƯỢC (THE 30-VIDEO EDITORIAL MATRIX)
# Tỷ lệ: 50% Giá trị thuần (15 video) + 30% Xây dựng niềm tin (9 video) + 20% Có Affiliate (6 video)
# ─────────────────────────────────────────────────────────────────────────────

EDITORIAL_30_VIDEOS = [
    # ── NHÓM 1: 15 VIDEO GIẢI QUYẾT VẤN ĐỀ — HOÀN TOÀN KHÔNG BÁN HÀNG (VALUE-ONLY) ──
    {
        "video_number": 1,
        "content_type": "VALUE_ONLY",
        "title": "Phòng trọ 15m²: 5 lỗi bố trí phổ biến khiến căn phòng càng chật chội",
        "hook_angle": "Tại sao phòng bạn dọn mãi vẫn thấy chật? Có thể do bạn phạm phải lỗi số 2 này!",
        "core_pain_point": "Phòng nhỏ bố trí sai hướng chắn luồng di chuyển và tầm nhìn.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Bản vẽ 2D mặt bằng phòng trọ + Animation mũi tên luồng di chuyển (Faceless Infographic)"
    },
    {
        "video_number": 2,
        "content_type": "VALUE_ONLY",
        "title": "Tại sao phòng nhỏ càng mua nhiều hộp lưu trữ thì càng bừa bãi?",
        "hook_angle": "Nghịch lý phòng trọ: Càng mua khay kệ cất đồ, bạn càng có xu hướng tích rác!",
        "core_pain_point": "Ảo tưởng rằng mua đồ đựng sẽ làm phòng ngăn nắp mà không chịu thanh lọc đồ thừa.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "COMPLETION_RATE",
        "faceless_visual_style": "Biểu đồ trực quan so sánh thói quen 'Tích trữ' vs 'Nguyên tắc 1 vào 1 ra'"
    },
    {
        "video_number": 3,
        "content_type": "VALUE_ONLY",
        "title": "Bàn làm việc 1 mét: Quy tắc 'Bàn tay phải' giúp tập trung gấp đôi",
        "hook_angle": "Chỉ cần dịch 3 món đồ này sang bên trái, não bộ của bạn sẽ bớt mệt mỏi ngay lập tức.",
        "core_pain_point": "Tầm mắt bị xao nhãng bởi đồ đạc đặt sai vị trí.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Góc quay từ trên xuống (Top-down view) bàn làm việc và các vùng tập trung"
    },
    {
        "video_number": 4,
        "content_type": "VALUE_ONLY",
        "title": "Cách đi dây điện gầm bàn gọn gàng bằng vật dụng văn phòng 0 đồng",
        "hook_angle": "Dây sạc lòng thòng dưới chân vừa nguy hiểm vừa ngứa mắt? Đây là cách xử lý trong 2 phút!",
        "core_pain_point": "Búi dây điện rối nùi dưới gầm bàn hút bụi và dễ đá phải chập điện.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Thao tác tay cận cảnh luồn kẹp bướm và dây rút cố định vào chân bàn"
    },
    {
        "video_number": 5,
        "content_type": "VALUE_ONLY",
        "title": "Cách tạo đối lưu gió cho phòng trọ khép kín: Giảm 3 độ C mùa nóng",
        "hook_angle": "Bật quạt số to mà phòng vẫn hầm hập như lò bát quái? Đặt quạt theo góc này ngay!",
        "core_pain_point": "Phòng trọ một cửa không có gió tự nhiên, quạt thổi luẩn quẩn khí nóng.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Animation luồng khí nóng bay lên trần và hướng quạt hút gió tươi vào cửa"
    },
    {
        "video_number": 6,
        "content_type": "VALUE_ONLY",
        "title": "Quy tắc 3 chiếc hộp: Dọn sạch căn phòng bừa bãi chỉ trong 15 phút",
        "hook_angle": "Ngại dọn phòng vì nhìn đâu cũng không biết bắt đầu từ đâu? Hãy chuẩn bị 3 chiếc hộp này!",
        "core_pain_point": "Quá tải tinh thần khi phòng quá bừa bộn.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "COMPLETION_RATE",
        "faceless_visual_style": "Motion graphics 3 chiếc hộp: 'Giữ lại', 'Cho đi/Vứt', 'Chưa quyết định'"
    },
    {
        "video_number": 7,
        "content_type": "VALUE_ONLY",
        "title": "Tư thế ngồi 90-90 chuẩn công thái học: Không cần ghế chục triệu",
        "hook_angle": "Lưng bạn đau không phải vì ghế rẻ, mà vì bạn chưa biết mẹo kê đệm này!",
        "core_pain_point": "Thoái hóa đốt sống cổ và đau lưng do tư thế ngồi sai góc.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Mô phỏng bộ xương người ngồi với các góc 90 độ ở khuỷu tay và đầu gối"
    },
    {
        "video_number": 8,
        "content_type": "VALUE_ONLY",
        "title": "Cách phơi quần áo trong phòng trọ nhanh khô, không bị hôi mùi ẩm",
        "hook_angle": "Mùa mưa giặt đồ phơi trong phòng có mùi ẩm mốc khó chịu? Hãy thử mẹo khoảng cách này!",
        "core_pain_point": "Quần áo giặt phơi phòng trọ thiếu nắng bốc mùi chua.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Đồ họa so sánh khoảng cách phơi hình vòm (Arch hanging) hút gió nhanh gấp đôi"
    },
    {
        "video_number": 9,
        "content_type": "VALUE_ONLY",
        "title": "Quy tắc 'Tầm mắt và tầm tay': Xếp đồ nhà tắm thông minh",
        "hook_angle": "Tại sao nhà vệ sinh phòng trọ lúc nào cũng ướt nhẹp và ngập chai lọ?",
        "core_pain_point": "Chai dầu gội, sữa tắm để sàn bám cặn xà phòng vàng ố.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "COMPLETION_RATE",
        "faceless_visual_style": "Cảnh phân chia độ cao trong nhà tắm và quy tắc không đặt đồ xuống sàn"
    },
    {
        "video_number": 10,
        "content_type": "VALUE_ONLY",
        "title": "Bí quyết giữ bàn phím và tai nghe luôn sạch mà không cần tháo linh kiện",
        "hook_angle": "Soi đèn pin vào khe bàn phím với màng loa tai nghe của bạn xem, có khi phát ói đấy!",
        "core_pain_point": "Bụi bẩn và ráy tai bám két làm giảm âm lượng và kẹt phím.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Cận cảnh bàn chải lông mềm và tăm bông vệ sinh các kẽ hở đúng kỹ thuật"
    },
    {
        "video_number": 11,
        "content_type": "VALUE_ONLY",
        "title": "Cách bố trí ánh sáng phòng trọ để ngủ sâu hơn và đỡ mỏi mắt",
        "hook_angle": "Đèn tuýp trắng xóa giữa phòng chính là thủ phạm khiến bạn khó ngủ mỗi đêm!",
        "core_pain_point": "Ánh sáng trắng công suất lớn vào ban đêm ức chế Melatonin gây mất ngủ.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "COMPLETION_RATE",
        "faceless_visual_style": "So sánh quang phổ ánh sáng 6500K (trắng xanh) vs 3000K (vàng ấm thư giãn)"
    },
    {
        "video_number": 12,
        "content_type": "VALUE_ONLY",
        "title": "Mẹo tận dụng khoảng chết dưới gầm giường và sau cánh cửa",
        "hook_angle": "Phòng bạn không hề chật, chỉ là bạn đang lãng phí 3 khoảng không gian vàng này!",
        "core_pain_point": "Bỏ quên không gian thẳng đứng (vertical space).",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Animation căn phòng 3D làm nổi bật các góc tường chết và mặt sau cánh cửa"
    },
    {
        "video_number": 13,
        "content_type": "VALUE_ONLY",
        "title": "Checklist đồ dùng cần dọn sạch trước khi trả phòng để lấy lại 100% tiền cọc",
        "hook_angle": "Đừng để chủ nhà trừ tiền cọc vô lý chỉ vì những vết ố bẩn này trên tường và sàn!",
        "core_pain_point": "Mất tiền cọc phòng trọ vì hư hại tường hoặc bẩn sàn gạch.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Bảng checklist đồ họa + cách dùng baking soda tẩy sạch vết ố gạch men"
    },
    {
        "video_number": 14,
        "content_type": "VALUE_ONLY",
        "title": "Nguyên tắc quản lý dây sạc: Tại sao dây cáp của bạn cứ 3 tháng lại gãy cổ?",
        "hook_angle": "Thói quen cuộn dây sạc kiểu này đang âm thầm bẻ gãy lõi đồng bên trong mỗi ngày!",
        "core_pain_point": "Dây cáp sạc nhanh nhanh hỏng, chập chờn tiếp xúc.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "COMPLETION_RATE",
        "faceless_visual_style": "Hình ảnh tia X mô phỏng lõi đồng bị đứt gập khi cuộn dây góc nhọn"
    },
    {
        "video_number": 15,
        "content_type": "VALUE_ONLY",
        "title": "Cách thiết lập thói quen dọn dẹp '2 phút mỗi tối' để không bao giờ phải tổng vệ sinh",
        "hook_angle": "Chỉ đúng 120 giây trước khi đi ngủ, sáng hôm sau bước xuống giường phòng như khách sạn!",
        "core_pain_point": "Ngại dọn dẹp dồn ứ cả tuần mới dọn một lần mất cả buổi sáng chủ nhật.",
        "solution_type": "FREE_BEHAVIORAL",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "A_CONTENT_VALUE",
        "primary_metric": "SAVES_AND_FOLLOWS",
        "faceless_visual_style": "Đồng hồ đếm ngược 120s và 3 hành động: gập chăn, cất ly nước, cắm sạc"
    },

    # ── NHÓM 2: 9 VIDEO PHÂN TÍCH SAI LẦM & BÓC TÁCH MUA SẮM (BUILDING TRUST) ──
    {
        "video_number": 16,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "3 thứ tuyệt đối KHÔNG NÊN MUA khi mới chuyển vào phòng trọ",
        "hook_angle": "Rất nhiều người mất cả triệu đồng cho 3 món đồ này, mua về đúng 1 tháng là vứt xó!",
        "core_pain_point": "Mua sắm bốc đồng theo quảng cáo TikTok những món đồ cồng kềnh khó thanh lý.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Đóng dấu chữ X đỏ to đùng lên 3 món đồ: Tủ vải ọp ẹp, máy ép chậm mini rẻ tiền, rèm dán tường"
    },
    {
        "video_number": 17,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Kệ dán tường 30K và Kệ bắt vít 100K: Loại nào thực sự phù hợp với phòng trọ?",
        "hook_angle": "Đừng vội mua kệ dán tường nếu tường phòng bạn là loại sơn vôi cũ này!",
        "core_pain_point": "Kệ dán tường bóc ra tróc nguyên mảng vôi tường bị đền cọc.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Bảng so sánh 2 cột: Bề mặt phù hợp, trọng lượng tải tối đa, rủi ro tróc tường"
    },
    {
        "video_number": 18,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Bóc tách máy hút bụi mini 100K trên mạng: Hút được gì và KHÔNG HÚT ĐƯỢC GÌ?",
        "hook_angle": "Quảng cáo hút bay cả tảng đá? Đây là sự thật sau khi kiểm chứng thực tế!",
        "core_pain_point": "Quảng cáo nói quá công năng máy mini rẻ tiền gây thất vọng.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "So sánh 2 bài test: Hút tóc/vụn bánh (ĐẠT) vs Hút thảm dày/nước ngập (KHÔNG ĐẠT)"
    },
    {
        "video_number": 19,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Củ sạc 5W cũ và Củ sạc nhanh GaN 30W: Có đáng để nâng cấp không?",
        "hook_angle": "Cắm sạc qua đêm nóng ran máy? Sự khác biệt giữa củ sạc rẻ tiền và công nghệ GaN là gì?",
        "core_pain_point": "Sạc chậm mất 3 tiếng và củ sạc sinh nhiệt lớn nguy cơ cháy nổ.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Đồ thị thời gian sạc từ 0% lên 50% trong 25 phút vs nhiệt độ đo bằng súng nhiệt"
    },
    {
        "video_number": 20,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Có nên mua bàn nâng hạ điện tự động cho phòng trọ không?",
        "hook_angle": "Món đồ 5 triệu đồng này có thực sự cần thiết hay chỉ là trào lưu sống ảo?",
        "core_pain_point": "Đầu tư quá nhiều tiền vào bàn to cồng kềnh khi diện tích phòng không cho phép.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Phân tích 3 trường hợp nên mua vs giải pháp thay thế rẻ hơn gấp 10 lần (Giá đỡ nâng)"
    },
    {
        "video_number": 21,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Đèn hoàng hôn Sunset Lamp: Món đồ sống ảo hay rác công nghệ sau 1 tuần?",
        "hook_angle": "Ai cũng bảo mua về chill lắm, nhưng đây là 3 điểm phiền phức người bán không bao giờ nói!",
        "core_pain_point": "Đèn dùng cổng USB rẻ tiền tỏa nhiệt nóng và quầng sáng chỉ đẹp trong phòng tối om.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Cận cảnh góc cắm dây USB nóng và sự khác biệt giữa ảnh studio đã chỉnh màu vs thực tế"
    },
    {
        "video_number": 22,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Móc dán tường silicon trong suốt: Tại sao dán đúng cách thì treo được 5kg không rơi?",
        "hook_angle": "Treo khung ảnh rơi vỡ toang? 90% mọi người dán sai ngay từ bước lau bề mặt!",
        "core_pain_point": "Không biết kỹ thuật ép hết bọt khí và thời gian chờ 24h trước khi treo đồ nặng.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Hình ảnh cắt lớp vi mô keo dính bám vào gạch men và đồng hồ đếm ngược 24h"
    },
    {
        "video_number": 23,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Túi hút chân không đựng quần áo: Dùng loại hút tay hay hút máy?",
        "hook_angle": "Bơm tay mỏi rã rời hay máy hút nóng ran? So sánh độ bền của 2 loại sau 3 tháng sử dụng.",
        "core_pain_point": "Túi hút chân không giá rẻ bị xì hơi sau vài tuần làm quần áo phồng trở lại.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Test độ kín của van khóa đôi (Double zip) và lực nén thực tế của tủ quần áo"
    },
    {
        "video_number": 24,
        "content_type": "MISTAKE_ANALYSIS",
        "title": "Giá đỡ laptop nhôm 100K vs Giá đỡ nhựa 30K: Đắt hơn gấp 3 có đáng tiền?",
        "hook_angle": "Gõ phím rung bần bật như động đất? Lý do đừng bao giờ tiếc tiền cho khớp nối kim loại!",
        "core_pain_point": "Giá đỡ nhựa ọp ẹp rung lắc khi gõ phím làm mỏi tay và dễ đổ máy.",
        "solution_type": "OBJECTIVE_COMPARISON",
        "has_affiliate_link": False,
        "linked_sku": None,
        "target_kpi_pillar": "B_AUDIENCE_TRUST",
        "primary_metric": "RETENTION_TRUST",
        "faceless_visual_style": "Thước đo góc độ rung lắc khi gõ phím mạnh giữa khung hợp kim nhôm và khung nhựa ABS"
    },

    # ── NHÓM 3: 6 VIDEO GIỚI THIỆU GIẢI PHÁP PHÙ HỢP — CÓ GẮN LINK AFFILIATE (CONVERSION) ──
    {
        "video_number": 25,
        "content_type": "AFFILIATE_SOLUTION",
        "title": "Không có chỗ để đồ dưới bàn? 3 cách tận dụng khoảng trống (Kèm giá đỡ công thái học)",
        "hook_angle": "Màn hình thấp khiến bạn gù lưng mỏi cổ? 3 giải pháp nâng tầm mắt vừa gọn bàn vừa êm người!",
        "core_pain_point": "Bàn làm việc chật, màn hình đặt thấp làm thoái hóa đốt sống cổ.",
        "solution_type": "PRODUCT_RECOMMENDATION",
        "has_affiliate_link": True,
        "linked_sku": "SKU-DESK-STAND-001",
        "target_kpi_pillar": "C_REVENUE_CONVERSION",
        "primary_metric": "CTR_AND_ORDERS",
        "faceless_visual_style": "Cảnh nâng laptop lên 6 nấc, gầm giá đỡ nhét vừa vặn bàn phím rời khi không dùng"
    },
    {
        "video_number": 26,
        "content_type": "AFFILIATE_SOLUTION",
        "title": "Bàn làm việc thiếu sáng nhưng phòng chật không có chỗ đặt đèn? Giải pháp gắn màn hình!",
        "hook_angle": "Đèn bàn học chiếm nửa diện tích mặt bàn? Đây là chân ái của dân cày đêm phòng nhỏ!",
        "core_pain_point": "Thiếu ánh sáng làm việc ban đêm, đèn học truyền thống chiếm diện tích và gây chói màn hình.",
        "solution_type": "PRODUCT_RECOMMENDATION",
        "has_affiliate_link": True,
        "linked_sku": "SKU-DESK-LIGHTBAR-002",
        "target_kpi_pillar": "C_REVENUE_CONVERSION",
        "primary_metric": "CTR_AND_ORDERS",
        "faceless_visual_style": "Cảnh kẹp đèn lên viền màn hình không tốn 1cm² mặt bàn, bật đèn sáng rực bàn phím không chói mắt"
    },
    {
        "video_number": 27,
        "content_type": "AFFILIATE_SOLUTION",
        "title": "Bàn phím và ghế xe ô tô đầy vụn bánh? Thử lực hút lốc xoáy của máy mini cầm tay",
        "hook_angle": "Lấy khăn lau thì bất lực mà vác máy hút bụi gia đình to đùng thì ngại? Xem em này lướt 3 giây!",
        "core_pain_point": "Bụi mịn kẽ phím, lông thú cưng và tàn thuốc rơi vào ngóc ngách hẹp khó vệ sinh.",
        "solution_type": "PRODUCT_RECOMMENDATION",
        "has_affiliate_link": True,
        "linked_sku": "SKU-CAR-VACUUM-001",
        "target_kpi_pillar": "C_REVENUE_CONVERSION",
        "primary_metric": "CTR_AND_ORDERS",
        "faceless_visual_style": "Đầu hút dẹt lướt 1 đường qua khe ghế ô tô và bàn phím gom sạch bụi tức thì"
    },
    {
        "video_number": 28,
        "content_type": "AFFILIATE_SOLUTION",
        "title": "1 Củ sạc sạc được cả Laptop lẫn Điện thoại: Tạm biệt đống sạc nặng trịch khi đi làm",
        "hook_angle": "Balo lúc nào cũng nặng như đeo đá vì mang theo 3 củ sạc khác nhau? Nâng cấp lên củ sạc GaN này ngay!",
        "core_pain_point": "Đi làm, đi cà phê phải mang theo củ sạc laptop to đùng và nhiều củ sạc điện thoại vướng víu.",
        "solution_type": "PRODUCT_RECOMMENDATION",
        "has_affiliate_link": True,
        "linked_sku": "SKU-PHONE-GAN30W-001",
        "target_kpi_pillar": "C_REVENUE_CONVERSION",
        "primary_metric": "CTR_AND_ORDERS",
        "faceless_visual_style": "Cầm củ sạc GaN nhỏ bằng ngón tay so sánh với củ sạc laptop cồng kềnh, cắm sạc đồng thời"
    },
    {
        "video_number": 29,
        "content_type": "AFFILIATE_SOLUTION",
        "title": "Tai nghe bẩn bám ráy tai làm tịt âm lượng? Bộ dụng cụ 7 món cứu tinh đây rồi!",
        "hook_angle": "Mỗi lần mở hộp tai nghe trước mặt bạn bè mà ngại ngùng giấu đi? Xử lý trong đúng 30 giây!",
        "core_pain_point": "Màng loa tai nghe và chân sạc trong hộp đựng bị két bẩn làm giảm chất lượng âm thanh và sạc chập chờn.",
        "solution_type": "PRODUCT_RECOMMENDATION",
        "has_affiliate_link": True,
        "linked_sku": "SKU-CLEAN-KIT7IN1-001",
        "target_kpi_pillar": "C_REVENUE_CONVERSION",
        "primary_metric": "CTR_AND_ORDERS",
        "faceless_visual_style": "Đầu kim loại cạo rãnh tai nghe, đầu mút xốp lau sâu hộc sạc tai nghe sạch bong"
    },
    {
        "video_number": 30,
        "content_type": "AFFILIATE_SOLUTION",
        "title": "Áo len áo dạ mùa đông bị xù lông như đồ cũ? Máy cạo 6 lưỡi lướt 1 đường mịn bóng",
        "hook_angle": "Chiếc áo dạ 1 triệu mua năm ngoái năm nay xù lông nhìn như đồ cũ? Đừng vứt đi vội!",
        "core_pain_point": "Ma sát vải làm áo len, áo nỉ bị xù cụm lông nhìn cũ kỹ và mất thẩm mỹ.",
        "solution_type": "PRODUCT_RECOMMENDATION",
        "has_affiliate_link": True,
        "linked_sku": "SKU-HOME-LINT-001",
        "target_kpi_pillar": "C_REVENUE_CONVERSION",
        "primary_metric": "CTR_AND_ORDERS",
        "faceless_visual_style": "Cạo 1 nửa vạt áo xù lông để lộ ra ranh giới mịn màng rõ rệt trước và sau (Satisfying visual)"
    }
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. EDITORIAL STRATEGY ENGINE CLASS
# ─────────────────────────────────────────────────────────────────────────────

class EditorialStrategyEngine:
    """Điều phối chiến lược biên tập nội dung Audience-First."""

    @classmethod
    def initialize_editorial_system(cls) -> Dict[str, Any]:
        """Khởi tạo toàn bộ hồ sơ khán giả và kế hoạch biên tập 30 video."""
        print(f"\n{'='*70}")
        print("  [EDITORIAL STRATEGY] KHỞI TẠO HỆ THỐNG BIÊN TẬP NỘI DUNG AUDIENCE-FIRST")
        print("  Định vị: Kênh Chuyên Gia Giải Quyết Vấn Đề + Mua Sắm Thông Minh (A + C)")
        print("  Nguyên tắc: 50% Giá trị thuần • 30% Niềm tin • 20% Có Affiliate")
        print(f"{'='*70}\n")

        # 1. Lưu hồ sơ Personas vào DB
        for p in PRIMARY_PERSONAS:
            upsert_audience_persona(p)

        # 2. Lưu kế hoạch 30 video vào DB
        target_persona_id = "persona_rental_living"
        save_editorial_plan(EDITORIAL_30_VIDEOS, persona_id=target_persona_id)

        # 3. Xuất báo cáo tài liệu chiến lược
        cls.export_deliverables(target_persona_id)

        # Thống kê cơ cấu
        val_count = sum(1 for v in EDITORIAL_30_VIDEOS if v["content_type"] == "VALUE_ONLY")
        mis_count = sum(1 for v in EDITORIAL_30_VIDEOS if v["content_type"] == "MISTAKE_ANALYSIS")
        aff_count = sum(1 for v in EDITORIAL_30_VIDEOS if v["content_type"] == "AFFILIATE_SOLUTION")

        print(f"✅ Đã thiết lập kế hoạch biên tập 30 video cân bằng hoàn hảo:")
        print(f"  • Video Giá trị thuần (0 bán hàng): {val_count}/30 ({val_count/30*100:.0f}%) — Mục tiêu: Lưu lại & Follow")
        print(f"  • Video Bóc tách & So sánh:          {mis_count}/30 ({mis_count/30*100:.0f}%) — Mục tiêu: Xây dựng niềm tin")
        print(f"  • Video Có gắn Affiliate:           {aff_count}/30 ({aff_count/30*100:.0f}%) — Mục tiêu: Kiểm chứng chuyển đổi")
        print(f"📁 Đã xuất bản tài liệu chiến lược: docs/sprint1/editorial_strategy_30_videos.md\n")

        return {
            "persona_id": target_persona_id,
            "total_videos": len(EDITORIAL_30_VIDEOS),
            "value_only_count": val_count,
            "mistake_analysis_count": mis_count,
            "affiliate_count": aff_count
        }

    @classmethod
    def export_deliverables(cls, persona_id: str):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. audience_personas.json
        persona_path = DOCS_SPRINT1_DIR / "audience_personas.json"
        with open(persona_path, "w", encoding="utf-8") as f:
            json.dump(PRIMARY_PERSONAS, f, ensure_ascii=False, indent=2)

        # 2. editorial_strategy_30_videos.md
        md_path = DOCS_SPRINT1_DIR / "editorial_strategy_30_videos.md"
        content = f"""# Chiến Lược Biên Tập Nội Dung 30 Video Đầu Tiên (Editorial Strategy)

- **Dự án:** `affiliate-agent-kit`
- **Khán giả mục tiêu:** Người trẻ ở trọ & tối ưu không gian nhỏ (15–25m²)
- **Định vị kênh:** **Chuyên gia giải quyết vấn đề + Bóc tách mua sắm thông minh (A + C)**
- **Thời điểm lập:** {now_str}
- **Phong cách thị giác:** **Faceless Educational Content** (Infographic chuyển động, sơ đồ 2D, không người mẫu giả review)

---

## 🎯 1. Triết Lý Cốt Lõi: Tại Sao Người Xem Theo Dõi Kênh?

> **"Người xem không theo dõi kênh để xem quảng cáo kệ dán tường 30k.  
> Họ theo dõi vì kênh này giúp họ sống tiện nghi, ngăn nắp hơn trong căn phòng nhỏ mà không tốn nhiều tiền."**

Hệ thống AI được cài đặt **quyền quyết định "KHÔNG BÁN HÀNG"**: Nếu một vấn đề cuộc sống có thể giải quyết miễn phí (bằng nguyên tắc sắp xếp, tư thế, mẹo thủ công), AI bắt buộc hướng dẫn giải pháp miễn phí và không gắn bất kỳ link sản phẩm nào.

---

## ⚖️ 2. Cơ Cấu Tỷ Lệ 30 Video Thử Nghiệm

| Nhóm nội dung | Số lượng | Tỷ lệ | Vai trò đối với kênh | Trọng tâm KPI |
|---|---:|---:|---|---|
| **1. Giải quyết vấn đề (Không bán hàng)** | 15 video | **50%** | Thu hút đúng tệp khán giả, tạo lý do để bấm Follow | **Lượt lưu (Saves)**, Lượt chia sẻ, Xem hết |
| **2. Bóc tách sai lầm & So sánh giải pháp** | 9 video | **30%** | Xây dựng niềm tin chuyên gia, chỉ ra 3 thứ phí tiền | **Thời lượng xem**, Bình luận tranh luận |
| **3. Giới thiệu sản phẩm phù hợp (Affiliate)** | 6 video | **20%** | Đưa ra giải pháp bằng sản phẩm đã kiểm chứng | **Click giỏ hàng (CTR)**, Đơn hàng (CVR) |
| **Tổng cộng** | **30 video** | **100%** | | |

---

## 📋 3. Chi Tiết Danh Mục 30 Video Đầu Tiên

### Nhóm 1: 15 Video Giá Trị Thuần — 0 Bán Hàng (Value-Only)

"""
        for v in EDITORIAL_30_VIDEOS:
            if v["content_type"] == "VALUE_ONLY":
                content += f"#### #{v['video_number']:02d}: {v['title']}\n"
                content += f"- **Hook 3s:** *\"{v['hook_angle']}\"*\n"
                content += f"- **Nỗi đau:** {v['core_pain_point']}\n"
                content += f"- **Hình ảnh Faceless:** {v['faceless_visual_style']}\n"
                content += f"- **Mục tiêu KPI:** `{v['primary_metric']}` (Trụ cột {v['target_kpi_pillar']})\n\n"

        content += """---

### Nhóm 2: 9 Video Bóc Tách Sai Lầm & So Sánh Khách Quan (Building Trust)

"""
        for v in EDITORIAL_30_VIDEOS:
            if v["content_type"] == "MISTAKE_ANALYSIS":
                content += f"#### #{v['video_number']:02d}: {v['title']}\n"
                content += f"- **Hook 3s:** *\"{v['hook_angle']}\"*\n"
                content += f"- **Vấn đề bóc tách:** {v['core_pain_point']}\n"
                content += f"- **Hình ảnh Faceless:** {v['faceless_visual_style']}\n"
                content += f"- **Mục tiêu KPI:** `{v['primary_metric']}` (Trụ cột {v['target_kpi_pillar']})\n\n"

        content += """---

### Nhóm 3: 6 Video Giới Thiệu Giải Pháp Có Gắn Affiliate (Conversion Testing)

"""
        for v in EDITORIAL_30_VIDEOS:
            if v["content_type"] == "AFFILIATE_SOLUTION":
                content += f"#### #{v['video_number']:02d}: {v['title']}\n"
                content += f"- **Hook 3s:** *\"{v['hook_angle']}\"*\n"
                content += f"- **Sản phẩm gắn kèm:** `{v['linked_sku']}`\n"
                content += f"- **Hình ảnh Faceless:** {v['faceless_visual_style']}\n"
                content += f"- **Mục tiêu KPI:** `{v['primary_metric']}` (Trụ cột {v['target_kpi_pillar']})\n\n"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
