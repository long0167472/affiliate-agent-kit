---
name: aff-video-producer
description: Turn an affiliate storyboard and permitted footage into platform-native short videos with shot-level quality control and traceable source assets. Use this skill when producing, editing, rendering, or checking affiliate video assets with Remotion/FFmpeg.
---

# Video producer

You own the rendered `VideoAsset` and production manifest. Read `references/contracts.md` and the relevant platform guidance in `references/platform-evidence.md`. The storyboard is a hypothesis: improve the edit when the actual footage or generated clip reveals a stronger truthful sequence, then record the change.

## Inputs

Approved `CreativePlan`, `ProductBrief` (including `available_assets` with `permission` status), platform target, audio/voice permissions, `veo_provider` config if API route is enabled, and a target experiment variant. Never assume a public listing image, review clip, or creator video is licensed for reuse without the `permission` field confirmed in the `ProductBrief`.

## Asset sourcing decision tree

Before generating anything, check `ProductBrief.available_assets` and apply this priority order:

1. **Seller-provided media kit assets** (`permission: seller_granted` or `permission: marketplace_affiliate_hub`) — safest path; use directly. These are images/clips explicitly placed by the seller in the platform's affiliate marketplace or media folder for creator use.
2. **Listing images with written seller permission** (`permission: seller_written_consent`) — acceptable; record the conversation/timestamp as evidence.
3. **Listing images, no explicit permission** (`permission: unknown`) — **do not use directly in video frames.** Pass to `GeminiVeoProvider` as a reference input to generate a new visual derivative. The generated clip is AI content; the original listing image is the visual reference, not an exported asset in the final video. Record this path clearly in the manifest.
4. **No usable image exists** — return `NEEDS_EVIDENCE` with a request for the seller's affiliate media kit or the simplest substitute (e.g., a single still from the listing that can serve as a Veo reference input).

> TikTok Shop and Shopee prohibit video content made solely from static PDP screenshots or slideshows. A Veo-animated clip derived from a static image satisfies the "dynamic video" requirement, provided it is labelled with the required AI/AIGC disclosure.

## Production

Treat reasoning, asset sourcing, rendering, and generative media as separate pipeline stages with separate capability checks. Prefer a deterministic local renderer (Remotion or FFmpeg) for final assembly. Use `GeminiVeoProvider` to turn product images into motion clips when real footage is unavailable.

### Stage 1 — Asset inventory

List every available asset from the `ProductBrief`. For each record: source URL or file path, asset type (listing image / seller kit / user footage / review screenshot), `permission` status, what the asset visually shows, and whether it depicts the exact SKU/variant. Reject any asset whose `permission` is `unknown` from being used raw in the final video; route it to Veo instead.

### Stage 2 — GeminiVeoProvider (image-to-video)

Use when real footage is absent and a seller image with at least `permission: unknown` is available as a visual reference.

**Inputs to Veo:**
- Up to 3 reference images (listing images, seller kit stills, or product photos — used as `ingredients`, not as final video frames)
- Storyboard prompt from `CreativePlan.storyboard[i]`: describe the intended motion, camera angle, environment, and timing for the first 3 seconds
- `aspect_ratio: "9:16"`, `resolution: "720p"` for MVP; upgrade to `1080p` only after verifying cost economics

**What Veo can do for affiliate video:**
- Animate a static product image into a lifestyle scene (marble surface, hand interaction, lighting transition)
- Generate multiple hook variants from the same product reference with different opening environments
- Produce native audio (ambient sound, no synthetic voiceover claiming first-hand use)

**Hard limits — do not instruct Veo to:**
- Generate a human claiming to have personally tested the product
- Show a before/after result that the ProductBrief marks as `forbidden_or_unproven_claims`
- Replicate a competitor's creative or copy another creator's shot sequence
- Represent the product with a feature, color, or quantity not present in the exact SKU

**API call pattern (Python reference for controller):**

```python
import time
from google import genai
from google.genai import types

client = genai.Client()  # Uses GOOGLE_API_KEY env var; requires Cloud Billing enabled

def generate_product_clip(storyboard_prompt: str, reference_image_paths: list[str],
                           aspect_ratio: str = "9:16", resolution: str = "720p",
                           model: str = "veo-3.1-fast-generate-preview") -> str:
    """
    Returns local path to saved MP4. Raises on API error.
    Record model, cost estimate, and prompt in the VideoAsset manifest.
    """
    # Upload reference images
    uploaded = [client.files.upload(path=p) for p in reference_image_paths]

    operation = client.models.generate_videos(
        model=model,
        prompt=storyboard_prompt,
        image=uploaded[0] if len(uploaded) == 1 else None,  # primary ingredient
        config=types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            number_of_videos=1,
        ),
    )
    while not operation.done:
        time.sleep(20)
        operation = client.operations.get(operation)

    clip = operation.response.generated_videos[0]
    client.files.download(file=clip.video)
    out_path = f"output/{clip.video.name}.mp4"
    clip.video.save(out_path)
    return out_path
```

**Cost guard:** estimate `duration_seconds × price_per_second` before each call. At current rates (Veo 3.1 Fast 720p ≈ \$0.10/s), a 10-second clip costs ≈ \$1 (≈ 25,000 đ). Log cost per clip in the manifest. If total generation cost for a video exceeds the `economics.cost_per_video` ceiling in the `ProductBrief`, pause and flag for orchestrator decision before proceeding.

**Provider fallback:** if the API returns 429 or billing errors, set `veo_status: UNAVAILABLE` in the manifest and fall back to the static-image slideshow path in Remotion (acknowledged as lower quality; reviewer must note this). Do not silently skip the cost log.

### Stage 3 — Assembly (Remotion / FFmpeg)

Use generated Veo clips and any seller-permitted static assets as inputs to Remotion or FFmpeg for final composition:

1. **First frame and hook (0–3 s):** confirm the Veo clip opens on the product clearly, hook text is readable at phone size, and the scene is not static.
2. **Story body:** intercut product close-ups (from seller kit or Veo), on-screen claim text, and any permitted seller footage. Each shot has one purpose: orient, create tension, demonstrate, compare, reveal, or invite action.
3. **Proof moment:** the frame that most clearly shows the specific capability or use case from `ProductBrief.visual_proof`. If Veo cannot credibly generate this (e.g., actual liquid absorption, before/after skin texture), mark `unresolved_limits: PROOF_WEAKENED_BY_AI` and flag for reviewer.
4. **CTA and disclosure:** add the required AI/AIGC label per platform policy (TikTok AIGC toggle; Shopee AI label). Include affiliate disclosure. Render captions synchronized to narration; keep text inside safe zones.
5. **Export:** render 9:16 master + at least one hook variant. Save manifest with source asset IDs, Veo prompt, model version, cost, in/out points, overlay positions, audio license, and output checksum.

### Stage 4 — Quality pass

Watch the export at phone size **with sound** and **muted**. Pause on: first frame, each claim frame, the proof moment, CTA. Check:
- Shown SKU color, quantity, and features match `ProductBrief.sku_and_variant` exactly
- No claim visible in video that appears in `ProductBrief.forbidden_or_unproven_claims`
- AI label is visible and correctly applied
- No competitor watermark, third-party app logo, or unrelated platform CTA
- Audio not clipping; captions not occluded by platform UI
- No black frames, jump cuts without purpose, or repeated clips

Record each defect with timestamp and fix it. "Looks good" is not a QA result.

## Output

Return `VideoAsset` with:
- `files`: render paths and checksums
- `source_manifest`: asset IDs, Veo prompt + model + cost per clip, in/out points, audio license
- `ai_usage`: `GEMINI_VEO` with model, prompt hash, reference image IDs, and cost
- `first_frame_path`
- `qa_findings[{timestamp, issue, resolution}]`
- `unresolved_limits`: especially `PROOF_WEAKENED_BY_AI` when the generated clip cannot show physical evidence
- `status`: `DONE`, `NEEDS_EVIDENCE`, or `BLOCKED`

If no usable image exists at all (neither listing image nor seller kit), return `NEEDS_EVIDENCE` with the precise ask: "Obtain one listing image or seller-kit still for SKU [X] to use as Veo reference input." Do not fabricate a clip from a text-only description of a product.
