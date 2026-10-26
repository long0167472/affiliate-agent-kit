"""
cli.py
================================================================================
GIAO DIỆN DÒNG LỆNH ĐIỀU HÀNH HỆ THỐNG AFFILIATE (AI GROWTH & CONVERSION SYSTEM):
================================================================================
Sử dụng:
  python cli.py status                     # Xem trạng thái hệ thống, Drive, hàng đợi
  python cli.py growth-calc                # Tính ngược từ mục tiêu lợi nhuận & xác suất đơn
  python cli.py plan-test                  # Lên ma trận 3 góc tiếp cận thử nghiệm (Controlled Test)
  python cli.py log-metrics                # Ghi nhận số liệu video thực tế & Chẩn đoán phễu TikTok 2026
  python cli.py import-analytics           # Nhập file CSV/Excel từ TikTok Shop Creator Analytics
  python cli.py growth-diagnosis           # Chẩn đoán phễu chi tiết & quyết định STOP / ITERATE / SCALE
  python cli.py growth-portfolio           # Bảng tổng kết hiệu suất toàn bộ danh mục sản phẩm
  python cli.py run-sample                 # Chạy quy trình mẫu cho sản phẩm
  python cli.py add-product                # Thêm một sản phẩm mới vào danh mục
  python cli.py process-queue              # Xử lý các tác vụ trong hàng đợi
  python cli.py open-flow                  # Mở trợ lý Google Flow
================================================================================
"""

import os
import sys
import argparse
import asyncio
import pathlib

# Đảm bảo in tiếng Việt không lỗi encoding trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config.settings import (
    GOOGLE_DRIVE_ROOT,
    FACTORY_ROOT,
    DIR_READY_TO_POST,
    DB_PATH
)
from engine.database import list_products, get_product, get_recent_events
from engine.queue_manager import QueueManager
from engine.growth_intelligence import (
    UnitEconomicsCalculator,
    FunnelDiagnoser,
    DecisionEngine,
    TikTokAnalyticsImporter,
    ControlledTestPlanner
)
from engine.editorial_engine import EditorialStrategyEngine
from orchestrator.controller import AffiliateOrchestrator
from flow.flow_browser import open_flow_in_browser

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        AFFILIATE AGENT KIT — AI GROWTH & CONVERSION SYSTEM       ║
║   Không chỉ là Video Factory • Hệ thống Tăng trưởng & Chuyển đổi ║
║   Research → Controlled Test → Measure → Learn → Scale / Stop    ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def show_status():
    print_banner()
    print("📁 CẤU HÌNH HỆ THỐNG:")
    print(f"  • Google Drive Desktop: {GOOGLE_DRIVE_ROOT}")
    print(f"  • Thư mục Nhà máy:     {FACTORY_ROOT}")
    print(f"  • Cơ sở dữ liệu:        {DB_PATH} (SQLite WAL)")
    
    # Hàng đợi
    stats = QueueManager.get_stats()
    print("\n⚡ TRẠNG THÁI HÀNG ĐỢI (JOB QUEUE):")
    if stats:
        for status, count in stats.items():
            print(f"  • {status:<15}: {count} tác vụ")
    else:
        print("  • Hàng đợi hiện đang trống.")

    # Sản phẩm
    products = list_products()
    print(f"\n📦 DANH SÁCH SẢN PHẨM ({len(products)} sản phẩm):")
    for p in products[:5]:
        comm_pct = p['commission_rate'] * 100
        print(f"  • [{p['sku']}] {p['title']} - {p['price_vnd']:,.0f}đ (Hoa hồng {comm_pct:.0f}%) -> {p['status']}")
    if len(products) > 5:
        print(f"    ... và {len(products)-5} sản phẩm khác.")

    # Video sẵn sàng đăng trong 08_Ready_To_Post
    ready_dirs = list(DIR_READY_TO_POST.glob("*/*"))
    print(f"\n🚀 SẢN PHẨM ĐÃ XUẤT RA GOOGLE DRIVE SẴN SÀNG ĐĂNG ({len(ready_dirs)}):")
    for rd in ready_dirs:
        video_exists = (rd / "video_final.mp4").exists()
        cap_exists = (rd / "caption.txt").exists()
        status_icon = "✅" if (video_exists and cap_exists) else "⚠️"
        print(f"  {status_icon} {rd.parent.name}/{rd.name} -> {rd}")
    print("\n" + "="*66)

async def run_sample():
    print_banner()
    print("▶ ĐANG CHẠY QUY TRÌNH MẪU CHO SẢN PHẨM:")
    print("  'Máy hút bụi mini cầm tay không dây 9000Pa' (Giá 149.000đ, Hoa hồng 12%)")
    
    orch = AffiliateOrchestrator()
    sample_product = {
        "sku": "SKU-VACUUM-MINI-001",
        "title": "Máy hút bụi mini cầm tay không dây 9000Pa đa năng",
        "price_vnd": 149000,
        "commission_rate": 0.12,
        "category": "Gia dụng & Xe hơi",
        "evidence_grade": "A",
        "tiktok_url": "https://shop.tiktok.com/view/product/172948291039821?region=VN&locale=vi-VN",
        "shopee_url": "https://shopee.vn/search?keyword=may+hut+bui+mini+cam+tay+khong+day+9000pa"
    }

    result = await orch.run_pipeline_for_sku("SKU-VACUUM-MINI-001", sample_product)
    print("\n🎯 KẾT QUẢ CUỐI CÙNG:")
    print(f"  • Trạng thái: {result['status']}")
    print(f"  • Điểm kiểm định QC: {result['quality_score']}/100")
    print(f"  • Video hoàn thiện: {result['video_file']}")
    print(f"  • Caption đăng bài: {result['caption_file']}")
    print("\n👉 BƯỚC CỦA BẠN: Mở thư mục trên Google Drive để xem video và đăng lên TikTok Shop!")

async def process_queue():
    print_banner()
    print("▶ ĐANG XỬ LÝ CÁC TÁC VỤ TRONG HÀNG ĐỢI...")
    orch = AffiliateOrchestrator()
    count = 0
    while True:
        has_more = await orch.process_next_queued_job()
        if not has_more:
            break
        count += 1
    print(f"\n[XONG] Đã xử lý {count} tác vụ trong hàng đợi.")

def main():
    parser = argparse.ArgumentParser(description="Affiliate Factory Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh cần thực hiện")

    # Status
    subparsers.add_parser("status", help="Xem trạng thái nhà máy & Google Drive")

    # Run sample
    subparsers.add_parser("run-sample", help="Chạy thử nghiệm sản phẩm mẫu hoàn chỉnh")

    # Process queue
    subparsers.add_parser("process-queue", help="Xử lý công việc trong hàng đợi")

    # Open Flow
    flow_parser = subparsers.add_parser("open-flow", help="Mở Google Flow trên trình duyệt")
    flow_parser.add_argument("--sku", type=str, help="Mã SKU cần làm prompt", default=None)

    # Add product
    add_parser = subparsers.add_parser("add-product", help="Thêm sản phẩm mới")
    add_parser.add_argument("--sku", type=str, required=True, help="Mã SKU")
    add_parser.add_argument("--title", type=str, required=True, help="Tên sản phẩm")
    add_parser.add_argument("--price", type=float, required=True, help="Giá bán VND")
    add_parser.add_argument("--commission", type=float, required=True, help="Tỷ lệ hoa hồng (VD: 0.12 cho 12%%)")
    add_parser.add_argument("--tiktok-url", type=str, default="", help="Link sản phẩm TikTok Shop")
    add_parser.add_argument("--shopee-url", type=str, default="", help="Link sản phẩm Shopee Video")

    # Sprint 1: Market Discovery
    subparsers.add_parser("sprint1-discover", help="Khởi chạy nghiên cứu thị trường Sprint 1 (18 ngách & Top 3)")

    # View Niches
    subparsers.add_parser("view-niches", help="Xem bảng xếp hạng 18 ngách tiềm năng")

    # Growth Calculator (Reverse Engineering & Probabilities)
    calc_parser = subparsers.add_parser("growth-calc", help="Tính ngược từ mục tiêu lợi nhuận & xác suất đơn")
    calc_parser.add_argument("--profit", type=float, default=5000000, help="Mục tiêu lợi nhuận hoa hồng VND (Mặc định: 5.000.000đ)")
    calc_parser.add_argument("--price", type=float, default=200000, help="Giá bán sản phẩm VND (Mặc định: 200.000đ)")
    calc_parser.add_argument("--commission", type=float, default=0.10, help="Tỷ lệ hoa hồng (Mặc định: 0.10 tức 10%%)")
    calc_parser.add_argument("--ctr", type=float, default=0.01, help="Tỷ lệ click CTR (Mặc định: 0.01 tức 1%%)")
    calc_parser.add_argument("--cvr", type=float, default=0.03, help="Tỷ lệ mua CVR (Mặc định: 0.03 tức 3%%)")

    # Plan Test (Controlled Test Matrix)
    test_parser = subparsers.add_parser("plan-test", help="Tạo ma trận 3 góc tiếp cận thử nghiệm cho SKU")
    test_parser.add_argument("--sku", type=str, required=True, help="Mã SKU cần lên kế hoạch thử nghiệm")

    # Log Metrics
    log_parser = subparsers.add_parser("log-metrics", help="Ghi nhận số liệu video thực tế & Chẩn đoán phễu TikTok 2026")
    log_parser.add_argument("--sku", type=str, required=True, help="Mã SKU")
    log_parser.add_argument("--video-id", type=str, required=True, help="Mã Video ID trên TikTok")
    log_parser.add_argument("--views", type=int, required=True, help="Lượt xem")
    log_parser.add_argument("--clicks", type=int, required=True, help="Lượt click sản phẩm")
    log_parser.add_argument("--orders", type=int, required=True, help="Số đơn hàng")
    log_parser.add_argument("--gmv", type=float, default=0.0, help="Doanh số GMV VND")
    log_parser.add_argument("--commission", type=float, default=0.0, help="Hoa hồng thực nhận VND")
    log_parser.add_argument("--angle", type=str, default="", help="Tên kịch bản / góc tiếp cận")

    # Growth Diagnosis
    diag_parser = subparsers.add_parser("growth-diagnosis", help="Chẩn đoán phễu chi tiết & quyết định STOP/ITERATE/SCALE cho SKU")
    diag_parser.add_argument("--sku", type=str, required=True, help="Mã SKU cần kiểm tra")

    # Growth Portfolio Overview
    subparsers.add_parser("growth-portfolio", help="Bảng tổng hợp hiệu suất toàn bộ danh mục sản phẩm")

    # View Audience Personas
    subparsers.add_parser("view-personas", help="Xem hồ sơ chân dung khán giả & danh mục nỗi đau thực tế")

    # View Editorial Plan
    subparsers.add_parser("view-editorial-plan", help="Xem kế hoạch biên tập 30 video cân bằng (50%% Giá trị, 30%% Niềm tin, 20%% Bán hàng)")

    # Init Editorial Plan
    subparsers.add_parser("init-editorial", help="Khởi tạo hoặc cập nhật chiến lược biên tập 30 video")

    args = parser.parse_args()

    if args.command == "status" or not args.command:
        show_status()
    elif args.command == "run-sample":
        asyncio.run(run_sample())
    elif args.command == "process-queue":
        asyncio.run(process_queue())
    elif args.command == "open-flow":
        open_flow_in_browser(args.sku)
    elif args.command == "add-product":
        orch = AffiliateOrchestrator()
        orch.add_product_and_enqueue({
            "sku": args.sku,
            "title": args.title,
            "price_vnd": args.price,
            "commission_rate": args.commission,
            "tiktok_url": args.tiktok_url,
            "shopee_url": args.shopee_url
        })
        print(f"✅ Đã thêm sản phẩm {args.sku} vào hàng đợi xử lý.")
    elif args.command == "sprint1-discover":
        print_banner()
        orch = AffiliateOrchestrator()
        orch.run_sprint1_discovery()
    elif args.command == "view-niches":
        print_banner()
        from engine.database import list_niches
        niches = list_niches()
        print(f"📊 BẢNG XẾP HẠNG {len(niches)} NGÁCH SẢN PHẨM TIỀM NĂNG (MÔ HÌNH 100 ĐIỂM):\n")
        for n in niches:
            badge = "🌟 [TOP 3]" if n["selected_status"] == "TOP_3_SELECTED" else "   "
            print(f"  {badge} #{n['rank']:<2} {n['name']:<48} | Điểm: {n['total_score']:>4.1f}/100 | {n['category']}")
        print("\n👉 Xem chi tiết báo cáo tại: docs/sprint1/market_report.md")
    elif args.command == "growth-calc":
        print_banner()
        res = UnitEconomicsCalculator.calculate_target_funnel(
            target_profit_vnd=args.profit,
            price_vnd=args.price,
            commission_rate=args.commission,
            ctr=args.ctr,
            cvr=args.cvr
        )
        print("🎯 BẢNG TÍNH NGƯỢC TỪ MỤC TIÊU LỢI NHUẬN (UNIT ECONOMICS):")
        print(f"  • Mục tiêu hoa hồng ròng:   {res['target_profit_vnd']:,.0f}đ")
        print(f"  • Giá bán sản phẩm:          {res['price_vnd']:,.0f}đ (Hoa hồng {res['commission_rate']*100:.0f}%)")
        print(f"  • Hoa hồng nhận / đơn:       {res['commission_per_order_vnd']:,.0f}đ")
        print(f"  • Giả định phễu:             CTR = {res['benchmark_ctr']*100:.1f}%, CVR = {res['benchmark_cvr']*100:.1f}%")
        print(f"  • Tỷ lệ chuyển đổi / view:   {res['orders_per_view']*100:.4f}% ({res['orders_per_view']} đơn/view)")
        print(f"  -------------------------------------------------------------")
        print(f"  👉 SỐ ĐƠN CẦN ĐẠT:           {res['required_orders']} đơn hàng")
        print(f"  👉 TỔNG VIEWS KỲ VỌNG:       {res['required_views']:,} lượt xem")
        print(f"  👉 GMV TƯƠNG ĐƯƠNG:          {res['gmv_equivalent_vnd']:,.0f}đ")
        print("\n📈 SỐ LƯỢNG VIDEO CẦN NẾU VIEW TRUNG BÌNH THẤP:")
        print(f"  • Nếu video chỉ đạt  200 view/video:  cần {res['videos_needed']['at_200_views']:,} video (Gần như bất khả thi!)")
        print(f"  • Nếu video chỉ đạt  500 view/video:  cần {res['videos_needed']['at_500_views']:,} video (Cực kỳ tốn công)")
        print(f"  • Nếu video đạt    1.000 view/video:  cần {res['videos_needed']['at_1000_views']:,} video")
        print(f"  • Nếu video đạt    5.000 view/video:  cần {res['videos_needed']['at_5000_views']:,} video")
        print(f"  • Nếu video đạt   10.000 view/video:  chỉ cần {res['videos_needed']['at_10000_views']} video!")
        print("\n💡 KẾT LUẬN: Tối ưu phân phối & chuyển đổi quan trọng hơn rất nhiều so với tăng số lượng video!")
        print("\n🎲 BẢNG XÁC SUẤT CÓ ĐƠN HÀNG TỪ MỘT VIDEO (CTR 1%, CVR 2%):")
        print("  Views/video | Đơn kỳ vọng | Xác suất >= 1 đơn | Xác suất >= 2 đơn")
        for row in UnitEconomicsCalculator.generate_probability_table():
            print(f"  {row['views']:>11,d} | {row['expected_orders']:>11.2f} | {row['prob_gte_1_percent']:>16.1f}% | {row['prob_gte_2_percent']:>16.2f}%")
    elif args.command == "plan-test":
        print_banner()
        prod = get_product(args.sku)
        title = prod["title"] if prod else args.sku
        price = prod["price_vnd"] if prod else 150000
        matrix = ControlledTestPlanner.generate_3_angle_matrix(args.sku, title, price)
        print(f"🧪 MA TRẬN 3 GÓC TIẾP CẬN THỬ NGHIỆM CHO SKU: {args.sku}")
        for idx, ang in enumerate(matrix, start=1):
            print(f"\n[{idx}] {ang['angle_title']}")
            print(f"  • Ý tưởng Hook: {ang['hook_concept']}")
            print(f"  • Hình ảnh:     {ang['visual_style']}")
            print(f"  • Chi phí dựng: {ang['production_cost_tier']}")
            print(f"  • Chỉ số đo:    {ang['target_metric']}")
    elif args.command == "log-metrics":
        print_banner()
        saved = TikTokAnalyticsImporter.ingest_record(
            video_id=args.video_id,
            sku=args.sku,
            views=args.views,
            clicks=args.clicks,
            orders=args.orders,
            gmv_vnd=args.gmv,
            commission_vnd=args.commission,
            angle_name=args.angle
        )
        diag = FunnelDiagnoser.diagnose(args.views, args.clicks, args.orders)
        print("✅ ĐÃ GHI NHẬN SỐ LIỆU VIDEO & CHẨN ĐOÁN PHỄU TIKTOK 2026:")
        print(f"  • Video ID:    {args.video_id} (SKU: {args.sku})")
        print(f"  • Views:       {args.views:,} | Clicks: {args.clicks} (CTR: {diag['ctr_percent']}%) | Orders: {args.orders} (CVR: {diag['cvr_percent']}%)")
        print(f"  • Trạng thái:  {diag['state']}")
        print(f"  • Vấn đề:      {diag['issue']}")
        print(f"  • Nguyên nhân: {diag['root_cause']}")
        print(f"  👉 HÀNH ĐỘNG:  {diag['recommended_action']}")
        print(f"  👉 QUYẾT ĐỊNH: {diag['decision']}")
    elif args.command == "growth-diagnosis":
        print_banner()
        diag = DecisionEngine.evaluate_product_status(args.sku)
        print(f"🔍 BÁO CÁO TĂNG TRƯỞNG & QUYẾT ĐỊNH CHO SKU: {args.sku}")
        print(f"  • Quyết định:     {diag['decision']}")
        print(f"  • Lý do:          {diag['reason']}")
        print(f"  • Khuyến nghị:    {diag['recommended_action']}")
        print(f"  • Tổng video:     {diag['videos_count']} video đã thử")
        print(f"  • Tổng views:     {diag['total_views']:,} lượt xem")
        print(f"  • Tổng clicks:    {diag['total_clicks']} clicks (CTR tổng: {diag['overall_ctr_percent']}%)")
        print(f"  • Tổng đơn hàng:  {diag['total_orders']} đơn (CVR tổng: {diag['overall_cvr_percent']}%)")
        print(f"  • Tổng hoa hồng:  {diag['total_commission_vnd']:,.0f}đ (RPM: {diag['rpm_commission_vnd']:,.0f}đ/1k view)")
    elif args.command == "growth-portfolio":
        print_banner()
        overview = DecisionEngine.get_portfolio_overview()
        print(f"📈 TỔNG HỢP DANH MỤC SẢN PHẨM ({len(overview)} sản phẩm):\n")
        for item in overview:
            status_icon = "🛑" if item["decision"] == "STOP" else ("🚀" if item["decision"] == "SCALE" else "🔄")
            print(f"  {status_icon} [{item['decision']}] SKU: {item['sku']:<22} | Views: {item['total_views']:>6,} | Clicks: {item['total_clicks']:>4} | Orders: {item['total_orders']:>2} | Comm: {item['total_commission_vnd']:>9,.0f}đ")
    elif args.command == "init-editorial":
        print_banner()
        EditorialStrategyEngine.initialize_editorial_system()
    elif args.command == "view-personas":
        print_banner()
        from engine.database import list_audience_personas
        personas = list_audience_personas()
        print(f"👥 DANH SÁCH CHÂN DUNG KHÁN GIẢ MỤC TIÊU ({len(personas)} hồ sơ):\n")
        for p in personas:
            print(f"🎯 [{p['id']}] {p['name']}")
            print(f"  • Định vị:        {p['archetype']}")
            print(f"  • Đối tượng:      {p['core_demographic']}")
            print(f"  • Bối cảnh sống:  {p['lifestyle_context']}")
            print(f"  • Lý do Follow:   {p['reasons_to_follow']}")
            print(f"  • Nỗi đau chính:  {len(p.get('primary_pains', []))} vấn đề nổi cộm")
            for idx, pain in enumerate(p.get('primary_pains', [])[:3], 1):
                print(f"     {idx}. {pain}")
            print(f"  • Giải pháp 0đ:   {len(p.get('free_solutions', []))} giải pháp hành vi không cần mua đồ\n")
    elif args.command == "view-editorial-plan":
        print_banner()
        from engine.database import list_editorial_plan
        plan = list_editorial_plan()
        print(f"📅 KẾ HOẠCH BIÊN TẬP 30 VIDEO CÂN BẰNG HOÀN HẢO ({len(plan)} video):\n")
        val_count = sum(1 for v in plan if v["content_type"] == "VALUE_ONLY")
        mis_count = sum(1 for v in plan if v["content_type"] == "MISTAKE_ANALYSIS")
        aff_count = sum(1 for v in plan if v["content_type"] == "AFFILIATE_SOLUTION")
        print(f"📊 Cơ cấu: {val_count} Giá trị thuần (50%) | {mis_count} Bóc tách & Niềm tin (30%) | {aff_count} Có Affiliate (20%)\n")
        for v in plan:
            type_tag = "🟢 [GIÁ TRỊ 0Đ]" if v["content_type"] == "VALUE_ONLY" else ("🟡 [BÓC TÁCH]" if v["content_type"] == "MISTAKE_ANALYSIS" else "🔴 [AFFILIATE]")
            link_info = f" -> Gắn: {v['linked_sku']}" if v["has_affiliate_link"] else " -> KHÔNG BÁN HÀNG"
            print(f"  #{v['video_number']:02d} {type_tag:<17} | {v['title']:<75} {link_info}")
        print("\n👉 Xem kịch bản chi tiết & Faceless Visual Style tại: docs/sprint1/editorial_strategy_30_videos.md")

if __name__ == "__main__":
    main()
