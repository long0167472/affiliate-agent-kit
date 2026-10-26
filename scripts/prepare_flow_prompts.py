"""
prepare_flow_prompts.py
────────────────────────────────────────────────────────────────
Tạo file prompt sẵn để paste vào Google Flow (flow.google.com)
Không cần API key — dùng credit Google AI Pro có sẵn
────────────────────────────────────────────────────────────────

Chạy:  python scripts/prepare_flow_prompts.py
Output: output/flow_prompts.md  (mở file này, copy từng prompt vào Flow)
"""

import pathlib, json, datetime

OUTPUT_DIR = pathlib.Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

PRODUCT = "Bộ dụng cụ thái rau củ đa năng 4-in-1 (lưỡi inox 420)"
PLATFORM = "Shopee Video + TikTok Shop"
CYCLE    = "cycle-2026-10-26-01"

# ── Storyboard shots (từ CreativePlan plan-p001-v1) ──────────────────────────
SHOTS = [
    {
        "id": "shot_1_hook",
        "duration": "8 giây",
        "purpose": "Hook — tạo pain point recognition ngay giây 0",
        "reference_image": "Ảnh sản phẩm đang dùng (product_in_use.jpg từ listing Shopee)",
        "flow_settings": {
            "aspect_ratio": "9:16 (Vertical)",
            "resolution":   "720p hoặc 1080p",
            "model":        "Veo 3.1 Fast (hoặc Quality nếu còn nhiều credit)",
            "audio":        "Generate audio: ON",
        },
        "prompt": (
            "Close-up shot of hands awkwardly chopping an onion on a wooden cutting board. "
            "Slow motion for the first 2 seconds showing the struggle — tears implied off-camera. "
            "Warm cozy kitchen lighting. 9:16 vertical video. "
            "Slightly comedic frustrated tone. Ends with the hand pausing, looking defeated."
        ),
        "on_screen_text": "Thái hành thế này mãi à? 😭",
        "note": "Đây là hook — cần first 0.5s thấy bàn tay + dao + hành ngay lập tức",
    },
    {
        "id": "shot_2_reveal",
        "duration": "8 giây",
        "purpose": "Product reveal — chuyển từ pain sang solution",
        "reference_image": "Ảnh sản phẩm chính (product_hero.jpg từ listing Shopee) ← QUAN TRỌNG",
        "flow_settings": {
            "aspect_ratio": "9:16 (Vertical)",
            "resolution":   "720p",
            "model":        "Veo 3.1 Fast",
            "audio":        "Generate audio: ON (satisfying 'ting' sound)",
        },
        "prompt": (
            "Product hero shot: a vegetable chopper slicer device placed elegantly "
            "on a white marble kitchen countertop. Four stainless steel blade inserts "
            "fanned out neatly beside it. Dramatic soft rim lighting from the left side. "
            "Slow cinematic push-in camera movement over 6 seconds. "
            "Commercial product video style. 9:16 vertical. Clean minimal background."
        ),
        "on_screen_text": "Tìm ra rồi 🔪✨",
        "note": "Upload ảnh hero sản phẩm làm reference — Veo sẽ dùng làm visual anchor",
    },
    {
        "id": "shot_3_proof",
        "duration": "10 giây",
        "purpose": "Proof moment — demonstrable capability (ASMR satisfying)",
        "reference_image": "Ảnh sản phẩm đang dùng (product_in_use.jpg)",
        "flow_settings": {
            "aspect_ratio": "9:16 (Vertical)",
            "resolution":   "720p",
            "model":        "Veo 3.1 Fast",
            "audio":        "Generate audio: ON — cần tiếng crunch/click thỏa mãn",
        },
        "prompt": (
            "Top-down overhead shot: a whole orange carrot is placed inside a vegetable chopper "
            "container. A hand presses the lid down firmly once with a satisfying crunch. "
            "The carrot instantly separates into perfectly uniform small orange cubes that "
            "fall neatly into the clear transparent container below. "
            "ASMR-style extreme close-up. Then quick cut to the same action with a white onion. "
            "9:16 vertical. Natural bright morning kitchen light. Total 10 seconds."
        ),
        "on_screen_text": "Chỉ 1 cái ấn. Đều luôn. 😤",
        "note": (
            "Shot quan trọng nhất — nếu Veo không generate được tay người thật thỏa mãn, "
            "thử prompt: 'top-down product demonstration, no visible hands, just the chopper "
            "mechanism activating and vegetables appearing diced'"
        ),
        "unresolved_limits": "PROOF_WEAKENED_BY_AI — clip không verify chất liệu lưỡi thật",
    },
    {
        "id": "shot_4_result",
        "duration": "8 giây",
        "purpose": "Payoff — emotional resolution + desire",
        "reference_image": "Ảnh kết quả (ảnh listing show rau củ đã thái đều — nếu có)",
        "flow_settings": {
            "aspect_ratio": "9:16 (Vertical)",
            "resolution":   "720p",
            "model":        "Veo 3.1 Lite (tiết kiệm credit — shot này ít cần chất lượng cao)",
            "audio":        "Generate audio: OFF (sẽ overlay nhạc riêng khi ghép)",
        },
        "prompt": (
            "Overhead flat-lay shot: a beautiful white ceramic bowl filled with colorful "
            "uniformly diced fresh vegetables — bright orange carrot cubes, green cucumber "
            "slices, white onion pieces, red bell pepper chunks. "
            "Vibrant fresh produce colors. Soft natural window light from the side. "
            "Slow gentle zoom-out over 6 seconds revealing the full bowl. "
            "9:16 vertical. Clean white kitchen surface. Food photography aesthetic."
        ),
        "on_screen_text": "20 phút → 30 giây 🤩",
        "note": "Shot này có thể thay bằng ảnh tĩnh overlay trong CapCut nếu Veo tốn quá nhiều credit",
    },
]

# ── Assembly instructions ─────────────────────────────────────────────────────
ASSEMBLY = """
## Lắp ráp video sau khi download 4 clip từ Flow

### Dùng CapCut (đơn giản nhất, miễn phí):
1. Tạo project mới → 9:16, 30fps
2. Import 4 clip theo thứ tự: shot_1 → shot_2 → shot_3 → shot_4
3. Thêm text overlay tại mỗi shot (xem cột "on_screen_text" ở trên)
4. Thêm nhạc nền: upbeat Vietnamese pop/EDM ngắn ~30s (CapCut có library miễn phí)
5. Shot 3: thêm text "Lưỡi inox 420 — xem review mua hàng ↓" (social proof)
6. Shot 4 cuối: thêm overlay CTA:
   - "Đang giảm 40% | Freeship hôm nay"
   - "Giỏ hàng góc phải ↓"
7. Export: 1080×1920 (9:16), MP4, 30fps

### Thứ tự timeline:
shot_1_hook (8s) → shot_2_reveal (8s) → shot_3_proof (10s) → shot_4_result (8s)
Tổng: ~34 giây ✓ (Shopee Video tối ưu 15–60s)

### Trước khi đăng:
- [ ] Bật AI label (Shopee Video: tab "AI" khi đăng)
- [ ] Gắn affiliate link SKU từ Shopee Affiliate dashboard
- [ ] Caption theo template trong PublishRecord
- [ ] Preview confirm product hiện đúng trong video
"""

# ── Tính credit estimate ──────────────────────────────────────────────────────
CREDIT_TABLE = {
    "Veo 3.1 Lite":    10,
    "Veo 3.1 Fast":    20,
    "Veo 3.1 Quality": 100,
}

def estimate_credits():
    # shot_1,2,3: Fast; shot_4: Lite
    models_used = ["Veo 3.1 Fast", "Veo 3.1 Fast", "Veo 3.1 Fast", "Veo 3.1 Lite"]
    total = sum(CREDIT_TABLE[m] for m in models_used)
    return total, models_used

# ── Generate output ───────────────────────────────────────────────────────────
def main():
    total_credits, models = estimate_credits()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# Flow Prompts — {PRODUCT}",
        f"**Generated:** {now} | **Cycle:** {CYCLE} | **Platform:** {PLATFORM}",
        "",
        "## 📋 Trước khi bắt đầu",
        "",
        "1. Mở **[flow.google.com](https://flow.google.com)** → đăng nhập tài khoản Google AI Pro",
        "2. Download 3 ảnh listing từ Shopee (tìm: 'dụng cụ cắt rau củ đa năng inox'):",
        "   - `product_hero.jpg` — ảnh sản phẩm chính, nền trắng",
        "   - `product_in_use.jpg` — ảnh đang dùng / tay đang cắt",
        "   - `product_result.jpg` — ảnh rau củ đã cắt đều (nếu có trong listing)",
        "3. Trong Flow: tạo **New Project** → đặt tên 'affiliate-rau-cu-01'",
        "",
        f"## 💳 Ước tính credit tiêu thụ: **~{total_credits} / 1.000 credit/tháng**",
        "",
        "| Shot | Model | Credit/lần | Ghi chú |",
        "|------|-------|-----------|---------|",
    ]

    for i, (shot, model) in enumerate(zip(SHOTS, models)):
        credit = CREDIT_TABLE[model]
        lines.append(f"| {shot['id']} | {model} | {credit} | {shot['purpose'][:40]} |")

    lines += [
        f"| **Tổng** | | **{total_credits}** | Còn ~{1000-total_credits} credit cho các thử nghiệm khác |",
        "",
        "---",
        "",
        "## 🎬 4 Shots — Copy prompt vào Flow",
        "",
    ]

    for i, shot in enumerate(SHOTS, 1):
        lines += [
            f"### Shot {i}: `{shot['id']}` ({shot['duration']})",
            "",
            f"**Mục đích:** {shot['purpose']}",
            "",
            "**Flow Settings:**",
        ]
        for k, v in shot["flow_settings"].items():
            lines.append(f"- {k}: `{v}`")

        lines += [
            "",
            f"**Reference Image:** {shot['reference_image']}",
            "*(Upload ảnh này trong Flow trước khi generate)*",
            "",
            "**Prompt** *(copy nguyên văn vào Flow)*:",
            "```",
            shot["prompt"],
            "```",
            "",
            f"**Text overlay khi ghép CapCut:** `{shot['on_screen_text']}`",
        ]

        if "note" in shot:
            lines += ["", f"> 💡 **Lưu ý:** {shot['note']}"]
        if "unresolved_limits" in shot:
            lines += ["", f"> ⚠️ **Giới hạn:** {shot['unresolved_limits']}"]

        lines += ["", "---", ""]

    lines.append(ASSEMBLY)

    out_path = OUTPUT_DIR / "flow_prompts.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Saved: {out_path.absolute()}")
    print(f"   Credit estimate: {total_credits}/1000 cho 4 clips")
    print(f"   Mở file này và follow từng bước trong Flow UI")

    # Cũng save JSON cho orchestrator/journal
    manifest = {
        "cycle_id": CYCLE,
        "generated_at": now,
        "shots": [
            {
                "id": s["id"],
                "model": m,
                "credit_cost": CREDIT_TABLE[m],
                "prompt_length": len(s["prompt"]),
                "status": "PREPARED",
            }
            for s, m in zip(SHOTS, models)
        ],
        "total_credit_estimate": total_credits,
        "status": "READY_FOR_FLOW",
    }
    manifest_path = OUTPUT_DIR / "flow_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Manifest: {manifest_path.absolute()}")


if __name__ == "__main__":
    main()
