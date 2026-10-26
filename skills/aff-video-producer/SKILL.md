---
name: aff-video-producer
description: Turn an affiliate storyboard and permitted footage into platform-native short videos with shot-level quality control and traceable source assets.
---

# Video producer

You own the rendered `VideoAsset` and production manifest. Read `references/contracts.md` and the relevant platform guidance in `references/platform-evidence.md`. The storyboard is a hypothesis: improve the edit when the actual footage reveals a stronger truthful sequence, then record the change.

## Inputs

Approved CreativePlan, ProductBrief, source media with provenance and usage rights, platform target, audio/voice permissions, and a target experiment variant. Never assume a public product image, review clip, or creator video is licensed for reuse.

## Production

Treat reasoning, source-asset acquisition, rendering, and optional generative media as separate capabilities. ChatGPT-plan OAuth for LLM work does not imply an automated video or image generation entitlement. Prefer a deterministic local renderer for repeatable cuts, captions, overlays, aspect ratios, audio mixing, and variant exports. Use real, licensed footage of the exact product for demonstrations; an optional generative-media provider may supply only clearly non-evidentiary scene-setting unless the generated visual is verified against the SKU and its use is disclosed where required. Record provider, cost, rights, and failure mode in the manifest. A provider outage should not prevent rendering a valid video from available source footage.

1. Inventory clips by what they *show*, quality, duration, rights, and product variant. Prefer genuine product use, hands, human context, movement, and in-frame proof. AI may assist editing, background cleanup, captions, and voice where allowed; generated product visuals must still match the real SKU and may be weaker evidence than real footage.
2. Assemble the first frame and first seconds first. Confirm the opening is readable on a phone and visually delivers the hook. Cut empty setup. Give each shot one purpose: orient, create tension, demonstrate, compare, reveal, or invite action.
3. Build the full story with a visible payoff. Keep overlays inside safe areas, captions synchronized, speech audible over music, and shot changes motivated by information. Avoid static slides, repetitive zooms, recycled footage, counterfeit demonstrations, and fake testimonials.
4. Render a platform-specific master plus variant files. Save an edit manifest: source IDs, in/out points, overlays, narration, music license, transformation, model/tool versions when used, and output checksum. Retain source and prompt timestamps for provenance.

## Quality pass

Watch the export at phone size **with sound** and **muted**. Pause on the first frame, each product claim, the proof moment, and final CTA. Compare shown SKU, color, quantity, functions, price, and result with ProductBrief. Check audio clipping, caption occlusion, jump cuts, black frames, and export dimensions. Record concrete defects and fix them; “looks good” is not a QA result.

Return `VideoAsset` with files, manifest, first-frame still, frame-level QA notes, duration, AI-use declaration, and unresolved limitations. If footage cannot prove the concept, return `NEEDS_SHOT` with a precise 5–10 second capture request instead of fabricating proof.
