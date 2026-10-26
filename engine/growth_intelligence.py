"""
engine/growth_intelligence.py
================================================================================
GROWTH INTELLIGENCE & CONVERSION ENGINE
Chuyển đổi từ mô hình "AI Video Factory" sang "AI Growth & Conversion System":
1. Tính ngược từ mục tiêu lợi nhuận (Reverse Engineering Unit Economics)
2. Mô hình xác suất chuyển đổi đơn hàng thực tế: Expected Orders = Views * CTR * CVR
3. Chẩn đoán phễu TikTok Shop 2026 (Low Views / Improve Clicks / Improve Conversions / Scalable)
4. Bộ quy tắc vận hành chiến lược: STOP / ITERATE / SCALE
5. Nhập & phân tích báo cáo TikTok Creator Analytics (CSV / JSON)
================================================================================
"""

import math
import json
import csv
import pathlib
from typing import Dict, Any, List, Optional, Tuple

from engine.database import (
    upsert_video_metrics,
    get_video_metrics,
    upsert_growth_experiment,
    get_sku_experiment,
    list_products,
    get_product,
    log_event
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. TÍNH TOÁN KINH TẾ ĐƠN VỊ & MÔ HÌNH XÁC SUẤT
# ─────────────────────────────────────────────────────────────────────────────

class UnitEconomicsCalculator:
    """Tính ngược từ mục tiêu lợi nhuận và mô phỏng xác suất tạo đơn hàng."""

    @staticmethod
    def calculate_target_funnel(
        target_profit_vnd: float,
        price_vnd: float,
        commission_rate: float,
        ctr: float = 0.01,
        cvr: float = 0.02
    ) -> Dict[str, Any]:
        """
        Tính số đơn và tổng lượt xem cần đạt để đạt mục tiêu lợi nhuận hoa hồng.
        Công thức:
          Hoa hồng / đơn = Giá * Tỷ lệ hoa hồng
          Số đơn cần = Target / Hoa hồng đơn
          Đơn kỳ vọng / view = CTR * CVR
          Views cần = Số đơn / (CTR * CVR)
        """
        commission_per_order = price_vnd * commission_rate
        if commission_per_order <= 0:
            raise ValueError("Hoa hồng mỗi đơn phải lớn hơn 0.")

        required_orders = math.ceil(target_profit_vnd / commission_per_order)
        orders_per_view = ctr * cvr
        if orders_per_view <= 0:
            raise ValueError("CTR và CVR phải lớn hơn 0.")

        required_views = math.ceil(required_orders / orders_per_view)

        # Tính số video cần nếu mỗi video đạt các mốc view khác nhau
        videos_at_200 = math.ceil(required_views / 200)
        videos_at_500 = math.ceil(required_views / 500)
        videos_at_1000 = math.ceil(required_views / 1000)
        videos_at_5000 = math.ceil(required_views / 5000)
        videos_at_10000 = math.ceil(required_views / 10000)

        return {
            "target_profit_vnd": target_profit_vnd,
            "price_vnd": price_vnd,
            "commission_rate": commission_rate,
            "commission_per_order_vnd": commission_per_order,
            "benchmark_ctr": ctr,
            "benchmark_cvr": cvr,
            "orders_per_view": orders_per_view,
            "required_orders": required_orders,
            "required_views": required_views,
            "gmv_equivalent_vnd": required_orders * price_vnd,
            "videos_needed": {
                "at_200_views": videos_at_200,
                "at_500_views": videos_at_500,
                "at_1000_views": videos_at_1000,
                "at_5000_views": videos_at_5000,
                "at_10000_views": videos_at_10000,
            }
        }

    @staticmethod
    def calculate_order_probabilities(views: int, ctr: float = 0.01, cvr: float = 0.02) -> Dict[str, Any]:
        """
        Tính xác suất có ít nhất 1 đơn và ít nhất 2 đơn từ số lượt xem cho trước.
        Mô hình Poisson / Nhị thức với p = CTR * CVR:
          Lambda = views * p
          P(X = 0) = e^(-lambda)
          P(X >= 1) = 1 - P(X = 0)
          P(X >= 2) = 1 - P(X = 0) - P(X = 1) = 1 - e^(-lambda) * (1 + lambda)
        """
        p = ctr * cvr
        expected_orders = views * p

        # Poisson distribution for views >= 200
        lam = expected_orders
        p0 = math.exp(-lam)
        p1 = lam * math.exp(-lam)

        prob_gte_1 = max(0.0, min(1.0, 1.0 - p0))
        prob_gte_2 = max(0.0, min(1.0, 1.0 - p0 - p1))

        return {
            "views": views,
            "ctr": ctr,
            "cvr": cvr,
            "expected_orders": round(expected_orders, 4),
            "prob_gte_1_percent": round(prob_gte_1 * 100.0, 2),
            "prob_gte_2_percent": round(prob_gte_2 * 100.0, 2)
        }

    @staticmethod
    def generate_probability_table() -> List[Dict[str, Any]]:
        """Tạo bảng xác suất chuẩn hóa theo bảng phân tích kinh doanh."""
        view_milestones = [200, 500, 1000, 3000, 5000, 10000]
        return [UnitEconomicsCalculator.calculate_order_probabilities(v) for v in view_milestones]


# ─────────────────────────────────────────────────────────────────────────────
# 2. CHẨN ĐOÁN PHỄU TIKTOK CREATOR ANALYTICS 2026
# ─────────────────────────────────────────────────────────────────────────────

class FunnelDiagnoser:
    """
    Chẩn đoán chính xác video đang thất bại ở công đoạn nào theo TikTok Shop:
    - LOW_VIEWS: Phân phối & Hook 3s thất bại
    - IMPROVE_CLICKS: Có view nhưng chưa tạo nhu cầu mua (Nội dung / CTA yếu)
    - IMPROVE_CONVERSIONS: Nhiều click nhưng ít đơn (Sản phẩm / Giá / Shop uy tín)
    - SCALE_WINNER: Tín hiệu mua hàng tích cực đáng để mở rộng
    """

    STATE_LOW_VIEWS = "LOW_VIEWS"
    STATE_IMPROVE_CLICKS = "IMPROVE_CLICKS"
    STATE_IMPROVE_CONVERSIONS = "IMPROVE_CONVERSIONS"
    STATE_SCALE_WINNER = "SCALE_WINNER"

    @classmethod
    def diagnose(
        cls,
        views: int,
        clicks: int,
        orders: int,
        min_view_threshold: int = 500,
        benchmark_ctr: float = 0.01,
        benchmark_cvr: float = 0.02
    ) -> Dict[str, Any]:
        ctr = (clicks / views) if views > 0 else 0.0
        cvr = (orders / clicks) if clicks > 0 else 0.0

        # 1. Ít view (< 500 views): Lỗi phân phối / Hook
        if views < min_view_threshold:
            state = cls.STATE_LOW_VIEWS
            decision = "ITERATE"
            issue = "Nội dung chưa được phân phối tốt (Low Views)"
            root_cause = "Hook 3 giây đầu chưa giữ chân người xem; tỷ lệ xem hết (completion rate) thấp hoặc âm thanh/hình ảnh chưa tạo tính giật gân tò mò."
            action = "Thử hook khác ngay: đổi 3 giây đầu sang góc visual tương phản mạnh, thay đổi nhịp cắt, hoặc sử dụng câu hỏi khơi gợi nỗi đau bức xúc."

        # 2. Nhiều view nhưng ít click (Views >= 500, CTR < 1%)
        elif ctr < benchmark_ctr:
            state = cls.STATE_IMPROVE_CLICKS
            decision = "ITERATE"
            issue = "Nhiều view nhưng ít click (Improve Clicks)"
            root_cause = "Nội dung mang tính giải trí/tò mò nhưng chưa tạo nhu cầu sở hữu sản phẩm. Lời kêu gọi hành động (CTA) mờ nhạt hoặc người xem không biết vì sao nên bấm vào giỏ hàng."
            action = "Thay đổi cách giới thiệu sản phẩm: nhấn mạnh lợi ích thiết thực, thêm badge giá trợ giá/freeship và hướng dẫn người xem bấm vào giỏ hàng góc trái."

        # 3. Nhiều click nhưng ít đơn (Clicks >= 20, CVR < 2%)
        elif orders == 0 or cvr < benchmark_cvr:
            state = cls.STATE_IMPROVE_CONVERSIONS
            decision = "ITERATE"
            issue = "Nhiều click nhưng ít đơn (Improve Conversions)"
            root_cause = "Khách hàng đã có nhu cầu vào xem nhưng trang bán hàng, mức giá, đánh giá của shop hoặc chính sách bảo hành chưa đủ thuyết phục."
            action = "Kiểm tra sản phẩm & giá: rà soát gian hàng seller (phải >= 4.5 sao), so sánh giá với các shop khác trên sàn, chọn SKU có quà tặng hoặc voucher đi kèm."

        # 4. Nhiều view, nhiều click, có đơn (Tín hiệu thành công)
        else:
            state = cls.STATE_SCALE_WINNER
            decision = "SCALE"
            issue = "Có tín hiệu chuyển đổi mạnh mẽ (Scale Winner)"
            root_cause = "Tổ hợp Sản phẩm × Góc tiếp cận × Đối tượng đang tạo ra lợi nhuận dương và chuyển đổi tốt."
            action = "Mở rộng quy mô (SCALE): Sản xuất thêm 3–5 phiên bản kịch bản cùng góc tiếp cận này, thử thêm sản phẩm bán kèm (cross-sell), chuẩn bị ngân sách nếu chạy quảng cáo Spark Ads."

        return {
            "views": views,
            "clicks": clicks,
            "orders": orders,
            "ctr_percent": round(ctr * 100, 2),
            "cvr_percent": round(cvr * 100, 2),
            "state": state,
            "decision": decision,
            "issue": issue,
            "root_cause": root_cause,
            "recommended_action": action
        }


# ─────────────────────────────────────────────────────────────────────────────
# 3. BỘ QUY TẮC QUYẾT ĐỊNH DANH MỤC: STOP / ITERATE / SCALE
# ─────────────────────────────────────────────────────────────────────────────

class DecisionEngine:
    """
    Quy tắc vận hành danh mục sản phẩm:
    - STOP: Nếu 1 sản phẩm đã thử qua nhiều góc nội dung (>= 3 video, >= 3.000 view) nhưng không tạo ra tín hiệu mua hàng -> Dừng đầu tư.
    - ITERATE: Nếu video có view nhưng CTR thấp, hoặc có click nhưng CVR thấp -> Thử đổi hook, kịch bản hoặc giá.
    - SCALE: Nếu một sản phẩm liên tục tạo đơn với hiệu quả tốt -> Tăng phiên bản nội dung & mở rộng sản phẩm liên quan.
    """

    @staticmethod
    def evaluate_product_status(sku: str) -> Dict[str, Any]:
        """Đánh giá toàn diện một SKU dựa trên lịch sử video đã đăng."""
        videos = get_video_metrics(sku=sku)
        product = get_product(sku)

        if not videos:
            return {
                "sku": sku,
                "status": "UNTESTED",
                "decision": "PLAN_TESTS",
                "message": "Sản phẩm chưa có dữ liệu video thực tế. Khuyến nghị tạo bộ 3 video thử nghiệm (3 góc khác nhau).",
                "total_views": 0,
                "total_clicks": 0,
                "total_orders": 0,
                "total_commission_vnd": 0.0,
                "videos_count": 0
            }

        total_views = sum(v["views"] for v in videos)
        total_clicks = sum(v["clicks"] for v in videos)
        total_orders = sum(v["orders"] for v in videos)
        total_comm = sum(v["commission_vnd"] for v in videos)
        overall_ctr = (total_clicks / total_views) if total_views > 0 else 0.0
        overall_cvr = (total_orders / total_clicks) if total_clicks > 0 else 0.0
        avg_rpm = (total_comm / total_views * 1000.0) if total_views > 0 else 0.0

        # Phân loại quyết định
        # 1. Điều kiện SCALE: Có >= 3 đơn hoặc có video tạo đơn đều đặn với RPM tốt
        if total_orders >= 3 or (total_orders >= 1 and overall_cvr >= 0.03):
            decision = "SCALE"
            reason = (
                f"Sản phẩm {sku} đã tạo {total_orders} đơn hàng thực tế với tổng hoa hồng {total_comm:,.0f}đ. "
                f"Tỷ lệ CVR đạt {overall_cvr*100:.1f}%. Đủ điều kiện mở rộng!"
            )
            action = "Sản xuất thêm 3-5 phiên bản kịch bản bổ sung, làm sâu thêm ngách người xem này."

        # 2. Điều kiện STOP: Đã thử >= 3 video, tổng view >= 3.000 nhưng 0 đơn hoặc CTR < 0.3%
        elif len(videos) >= 3 and total_views >= 3000 and total_orders == 0:
            decision = "STOP"
            reason = (
                f"Sản phẩm {sku} đã thử {len(videos)} góc nội dung qua {total_views:,} lượt xem nhưng 0 đơn hàng "
                f"(CTR tổng thể chỉ {overall_ctr*100:.2f}%). Tín hiệu thị trường kém."
            )
            action = "Tạm dừng sản xuất video cho sản phẩm này để tiết kiệm chi phí và tài nguyên. Chuyển sang SKU khác."

        # 3. Điều kiện ITERATE: Đang có dữ liệu, cần điều chỉnh hook hoặc CTA
        else:
            decision = "ITERATE"
            best_video = max(videos, key=lambda v: v["views"])
            reason = (
                f"Sản phẩm {sku} đã có {len(videos)} video thử nghiệm, tổng {total_views:,} view, {total_clicks} click, {total_orders} đơn. "
                f"Chưa đạt ngưỡng STOP nhưng cần tối ưu điểm nghẽn phễu."
            )
            diag = FunnelDiagnoser.diagnose(best_video["views"], best_video["clicks"], best_video["orders"])
            action = f"Tập trung cải thiện video có view cao nhất ({best_video['video_id']}): {diag['recommended_action']}"

        return {
            "sku": sku,
            "title": product.get("title", "") if product else "",
            "decision": decision,
            "reason": reason,
            "recommended_action": action,
            "videos_count": len(videos),
            "total_views": total_views,
            "total_clicks": total_clicks,
            "total_orders": total_orders,
            "total_commission_vnd": total_comm,
            "overall_ctr_percent": round(overall_ctr * 100, 2),
            "overall_cvr_percent": round(overall_cvr * 100, 2),
            "rpm_commission_vnd": round(avg_rpm, 0),
            "videos": videos
        }

    @staticmethod
    def get_portfolio_overview() -> List[Dict[str, Any]]:
        """Lấy báo cáo tổng hợp toàn bộ danh mục sản phẩm đang theo dõi."""
        products = list_products()
        overview = []
        for p in products:
            status = DecisionEngine.evaluate_product_status(p["sku"])
            overview.append(status)
        return overview


# ─────────────────────────────────────────────────────────────────────────────
# 4. NHẬP VÀ PHÂN TÍCH BÁO CÁO TIKTOK CREATOR ANALYTICS (CSV / DICT)
# ─────────────────────────────────────────────────────────────────────────────

class TikTokAnalyticsImporter:
    """
    Hỗ trợ nạp báo cáo TikTok Shop Creator Analytics định kỳ mà không bắt buộc dùng API:
    - Creator xuất file CSV/Excel từ TikTok Shop Seller/Creator Center
    - Hệ thống tự động phân loại, chẩn đoán và lưu trữ vào database bền vững
    """

    @staticmethod
    def ingest_record(
        video_id: str,
        sku: str,
        views: int,
        clicks: int,
        orders: int,
        gmv_vnd: float = 0.0,
        commission_vnd: float = 0.0,
        angle_id: Optional[str] = None,
        angle_name: Optional[str] = None,
        posted_at: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ghi nhận số liệu một video và tự động chẩn đoán."""
        diag = FunnelDiagnoser.diagnose(views, clicks, orders)

        metric_data = {
            "video_id": video_id,
            "sku": sku,
            "angle_id": angle_id,
            "angle_name": angle_name,
            "views": views,
            "clicks": clicks,
            "orders": orders,
            "gmv_vnd": gmv_vnd,
            "commission_vnd": commission_vnd,
            "diagnosis_state": diag["state"],
            "decision": diag["decision"],
            "notes": notes or f"{diag['issue']} | {diag['recommended_action']}",
            "posted_at": posted_at
        }
        return upsert_video_metrics(metric_data)

    @staticmethod
    def import_csv(file_path: str, default_sku: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Nhập file CSV xuất từ TikTok Shop.
        Định dạng hỗ trợ các cột:
          video_id, sku, views, clicks, orders, gmv, commission, angle_name
        """
        path = pathlib.Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

        results = []
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Chuẩn hóa tên cột linh hoạt
                v_id = row.get("video_id") or row.get("Video ID") or row.get("ID")
                v_sku = row.get("sku") or row.get("SKU") or default_sku
                if not v_id or not v_sku:
                    continue

                views = int(row.get("views") or row.get("Views") or row.get("Lượt xem") or 0)
                clicks = int(row.get("clicks") or row.get("Clicks") or row.get("Lượt nhấp") or 0)
                orders = int(row.get("orders") or row.get("Orders") or row.get("Đơn hàng") or 0)
                gmv = float(row.get("gmv") or row.get("GMV") or 0.0)
                comm = float(row.get("commission") or row.get("Commission") or row.get("Hoa hồng") or 0.0)
                angle_name = row.get("angle_name") or row.get("Kịch bản") or ""

                saved = TikTokAnalyticsImporter.ingest_record(
                    video_id=v_id,
                    sku=v_sku,
                    views=views,
                    clicks=clicks,
                    orders=orders,
                    gmv_vnd=gmv,
                    commission_vnd=comm,
                    angle_name=angle_name
                )
                results.append(saved)
        return results


# ─────────────────────────────────────────────────────────────────────────────
# 5. CHIẾN LƯỢC THỬ NGHIỆM CÓ KIỂM SOÁT (CONTROLLED TESTING MATRIX)
# ─────────────────────────────────────────────────────────────────────────────

class ControlledTestPlanner:
    """
    Tạo ma trận 3 góc tiếp cận thử nghiệm cho 1 sản phẩm:
    Thay vì sản xuất 100 video đại trà, chỉ làm 3 video thử nghiệm đại diện:
    1. Pain Point Hook (Nỗi đau thực tế -> Giải cứu nhanh)
    2. Satisfying Demo / ASMR Hook (Trực quan, đã mắt, test công năng thực tế)
    3. Price Shock / Value Deal Hook (So sánh giá đắt - rẻ, deal trợ giá hời)
    """

    @staticmethod
    def generate_3_angle_matrix(sku: str, product_title: str, price_vnd: float) -> List[Dict[str, Any]]:
        return [
            {
                "angle_id": f"{sku}_ANGLE_1_PAIN_POINT",
                "angle_type": "PAIN_POINT_RESCUE",
                "angle_title": "Góc 1: Giải cứu nỗi đau bực mình tức thì",
                "hook_concept": "Mở đầu trực tiếp vào cảnh tượng khó chịu bẩn thỉu mà ai cũng từng gặp phải.",
                "visual_style": "Cận cảnh vết bẩn / khó khăn thực tế + biểu cảm bức xúc -> Lướt 3s sạch bong",
                "production_cost_tier": "LOW (Tận dụng footage chân thực của shop hoặc clip quay thật)",
                "target_metric": "3s Retention Rate & Clicks"
            },
            {
                "angle_id": f"{sku}_ANGLE_2_SATISFYING_DEMO",
                "angle_type": "SATISFYING_DEMO",
                "angle_title": "Góc 2: Trải nghiệm ASMR & Trực quan công năng",
                "hook_concept": "Mở đầu bằng âm thanh hoặc chuyển động cực kỳ thỏa mãn mắt nhìn (ASMR/Satisfying).",
                "visual_style": "Chuyển động mượt mà, lướt 1 đường là sạch, zoom cận cảnh chi tiết linh kiện máy",
                "production_cost_tier": "MEDIUM (Motion graphics + Clip cắt dựng nhịp nhanh)",
                "target_metric": "Completion Rate & Video Shares"
            },
            {
                "angle_id": f"{sku}_ANGLE_3_PRICE_OFFER",
                "angle_type": "PRICE_OFFER_SHOCK",
                "angle_title": "Góc 3: Cú sốc giá rẻ & Trợ giá độc quyền",
                "hook_concept": "Mở đầu bằng mức giá giật gân: Bằng 2 cốc trà sữa nhưng dùng được vài năm.",
                "visual_style": "Badge giá đỏ nhấp nháy, so sánh giá ngoài siêu thị đắt gấp 3 với giá giỏ hàng trợ giá",
                "production_cost_tier": "LOW (Chữ to rõ, hiệu ứng tương phản số tiền, đếm ngược deal)",
                "target_metric": "CTR vào giỏ hàng & Số đơn tức thì"
            }
        ]
