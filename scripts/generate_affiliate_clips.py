"""
generate_affiliate_clips.py
──────────────────────────────────────────────────────────────────────────────
Chạy Veo 3.1 để sinh 4 clip cho video affiliate: dụng cụ thái rau củ đa năng
──────────────────────────────────────────────────────────────────────────────

Setup:
  1. pip install google-genai pillow
  2. Đặt GOOGLE_API_KEY trong env:
       set GOOGLE_API_KEY=AIza...   (Windows CMD)
       $env:GOOGLE_API_KEY="AIza..." (PowerShell)
  3. Chuẩn bị 3 ảnh listing từ Shopee (download thủ công → đặt vào thư mục images/)
     - images/product_hero.jpg     : ảnh sản phẩm chính
     - images/product_blades.jpg   : ảnh lưỡi dao
     - images/product_in_use.jpg   : ảnh đang dùng (nếu có)
  4. python generate_affiliate_clips.py

Output: output/shot_1.mp4, shot_2.mp4, shot_3.mp4, shot_4.mp4
Cost estimate: ~$2-3 tong (4 clips x 10s x $0.05-0.10/s Lite/Fast 720p)
"""

import os
import time
import pathlib
from google import genai
from google.genai import types

# -- Config ------------------------------------------------------------------
API_KEY    = os.environ.get("GOOGLE_API_KEY")
MODEL      = "veo-3.1-fast-generate-preview"   # Doi sang "veo-3.1-lite-generate-preview" de tiet kiem
RATIO      = "9:16"
RESOLUTION = "720p"
OUTPUT_DIR = pathlib.Path("output")
IMAGE_DIR  = pathlib.Path("images")
OUTPUT_DIR.mkdir(exist_ok=True)

# -- Storyboard shots --------------------------------------------------------
SHOTS = [
    {
        "id": "shot_1_hook",
        "reference_image": "product_in_use.jpg",
        "prompt": (
            "Close-up shot of hands awkwardly chopping an onion on a wooden cutting board, "
            "slow motion first 2 seconds showing the struggle, tears implied off-camera, "
            "warm kitchen lighting, 9:16 vertical video, slightly comedic tone, "
            "ends with frustrated hand gesture"
        ),
    },
    {
        "id": "shot_2_reveal",
        "reference_image": "product_hero.jpg",
        "prompt": (
            "Product hero shot: a vegetable chopper slicer device placed on a white marble "
            "kitchen countertop, 4 stainless steel blade inserts spread around it, "
            "dramatic rim lighting from left, slow push-in camera movement over 6 seconds, "
            "commercial product video style, 9:16 vertical, clean minimal background"
        ),
    },
    {
        "id": "shot_3_proof",
        "reference_image": "product_in_use.jpg",
        "prompt": (
            "Top-down shot: a whole orange carrot is placed into a vegetable chopper container, "
            "a hand presses the lid down firmly once, the carrot separates into perfectly "
            "uniform small cubes that fall into the transparent container below, "
            "satisfying ASMR-style close-up, then cut to same action with a white onion, "
            "9:16 vertical, natural morning kitchen light, 10 seconds total"
        ),
    },
    {
        "id": "shot_4_result",
        "reference_image": "product_hero.jpg",
        "prompt": (
            "Overhead shot: white ceramic bowl filled with colorful uniformly diced "
            "fresh vegetables - orange carrots, green cucumber, white onion, red bell pepper, "
            "vibrant colors, natural soft window light, slow zoom-out over 6 seconds, "
            "9:16 vertical, food photography style"
        ),
    },
]

# -- Helpers -----------------------------------------------------------------
def upload_reference_image(client, filename):
    path = IMAGE_DIR / filename
    if not path.exists():
        print(f"  [WARNING] {filename} not found -- skipping reference image")
        return None
    uploaded = client.files.upload(path=str(path))
    print(f"  Uploaded: {filename} -> {uploaded.name}")
    return uploaded


def generate_clip(client, shot):
    print(f"\n[{shot['id']}] {shot['prompt'][:80]}...")
    ref_file = upload_reference_image(client, shot["reference_image"])

    try:
        operation = client.models.generate_videos(
            model=MODEL,
            prompt=shot["prompt"],
            image=ref_file,
            config=types.GenerateVideosConfig(
                aspect_ratio=RATIO,
                resolution=RESOLUTION,
                number_of_videos=1,
            ),
        )
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

    attempt = 0
    while not operation.done:
        attempt += 1
        print(f"  Polling... attempt {attempt}")
        time.sleep(20)
        operation = client.operations.get(operation)

    if not operation.response.generated_videos:
        print(f"  [ERROR] No video returned")
        return None

    clip = operation.response.generated_videos[0]
    out_path = OUTPUT_DIR / f"{shot['id']}.mp4"
    client.files.download(file=clip.video)
    clip.video.save(str(out_path))
    print(f"  SAVED -> {out_path}")
    return str(out_path)


# -- Main --------------------------------------------------------------------
def main():
    if not API_KEY:
        print("ERROR: GOOGLE_API_KEY not set.")
        print("  PowerShell: $env:GOOGLE_API_KEY='AIza...'")
        return

    client = genai.Client(api_key=API_KEY)
    print(f"Model: {MODEL} | Output: {OUTPUT_DIR.absolute()}")
    print("Estimated cost: ~$2-3 for 4 clips")

    results = []
    for shot in SHOTS:
        out = generate_clip(client, shot)
        results.append({"id": shot["id"], "path": out, "ok": bool(out)})

    print("\n--- SUMMARY ---")
    for r in results:
        icon = "OK" if r["ok"] else "FAIL"
        print(f"  [{icon}] {r['id']:20s} -> {r['path'] or 'FAILED'}")

    print("\nNext steps:")
    print("  1. Review clips in output/")
    print("  2. Assemble with CapCut or Remotion: shot_1 + shot_2 + shot_3 + shot_4")
    print("  3. Add text overlay + music")
    print("  4. Post to Shopee Video + attach affiliate SKU link")
    print("  5. Enable AI label before publishing!")


if __name__ == "__main__":
    main()
