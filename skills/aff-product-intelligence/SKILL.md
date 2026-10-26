---
name: aff-product-intelligence
description: Independently discover, screen and select affiliate products for TikTok Shop and Shopee Video, grounding every creative claim in current product evidence and expected unit economics. Use this skill when researching, screening, or selecting products/SKUs for affiliate marketing.
---

# Product intelligence

You own the `DiscoveryBatch` and `ProductBrief`. Your job starts with finding candidates independently, then choosing products that can be shown truthfully and sold profitably. Read `references/contracts.md` for handoff formats and `references/platform-evidence.md` for platform discovery surfaces and eligibility.

## Inputs

The orchestrator supplies platform, creator account capability, audience/niche hypothesis, available samples/footage, budget, and research timestamp. Candidate URLs are optional. **Do not wait for the user to supply products or physical samples.** When account access is unavailable, search accessible official/public surfaces and mark account-only commission, eligibility and sales data unknown; request access only for the specific shortlisted item that needs verification.

## Discover candidates

1. Start from an audience problem or demonstrable use case, then search multiple authorized surfaces: TikTok Shop Creator Product Marketplace (category/search, creator recommendations, sample availability), Shopee Affiliate product/commission/Xtra offers, prior account product performance, platform search and public consumer questions. Record each source, query/category, observed time, and account access level. These surfaces differ by account; discover capabilities rather than assuming a universal API. Shopee's affiliate policy restricts automated tools and collection of marketplace product/price data: use an expressly permitted feed/API, an authorized export, or user-assisted browsing for Shopee account data. Do not turn "self-discovery" into unattended scraping or automated search on Shopee.
2. Build a `DiscoveryBatch` across at least two independent discovery signals when possible. Deduplicate identical SKUs and distinguish lookalikes, bundles and variants. For each candidate record: buyer problem, visible demonstration, demand signal, competing content/offer saturation, seller/review quality, current commission/price/stock where visible, sample/asset path, and why it may be worth testing. Keep rejected candidates with one concrete reason so the search does not rediscover them next cycle.
3. Treat bestseller lists, search trends and high commission as **leads**, not proof of accessible demand or profit. Prefer a product where listing images or seller media kit provide enough visual material for AI-generated video (via `GeminiVeoProvider`) when no sample or user footage is available. Check whether the exact item is eligible for this account and can be attached on the target platform; record the evidence and time. Do not conflate a TikTok listing with a similar Shopee listing.
4. Shortlist a few genuinely different opportunities. State what evidence could disconfirm each bet, and whether seller images from the listing are sufficient for Veo reference input or if a sample or original footage must be obtained. If no candidate is strong, change search terms/category or audience problem once; return `NEEDS_EVIDENCE` with the best next source rather than promoting a weak item.

## Image and asset sourcing (no physical sample required)

When the creator has no physical product to photograph or film, follow this hierarchy and record the result in `available_assets[].permission`:

| Source | Permission label | Notes |
|---|---|---|
| Official affiliate media kit or seller-uploaded hub assets on TikTok Shop Creator Marketplace or Shopee Affiliate dashboard | `marketplace_affiliate_hub` | Safest — seller explicitly placed these for creator use. Pull URLs and record observed date. |
| Seller's listing images and product videos, seller explicitly grants permission in writing (chat, email, official collaboration agreement) | `seller_written_consent` | Record the message/timestamp as evidence ref. Ask via platform's collaboration/sample request tools. |
| Seller's listing images, no permission obtained yet | `unknown` | Do NOT use directly in final video frames. Mark for `GeminiVeoProvider` reference-input path (image used as an ingredient for AI generation, not as exported content). Note this in brief. |
| No images available at all (listing text only, no photos) | `unavailable` | Return `NEEDS_EVIDENCE`; this product cannot enter the Veo pipeline without at least one visual reference. |

**How to obtain seller permission quickly:**
- Use TikTok Shop's built-in "Sample Request" or collaboration tools inside Creator Product Marketplace — many sellers respond within 24 h and grant asset rights when accepting a collaboration.
- For Shopee, use the campaign/collaboration invitation system or message the seller via the Shopee platform.
- Do not scrape, screenshot competitor listings, or use review images with identifiable personal data.

## Work

1. Inspect each shortlisted listing and authorized affiliate view. Record seller, exact variant, price range, stock, commission terms, recent review distribution, fulfillment concerns, and source URL with observation time. Treat price and commission as volatile.
2. Separate **listing claims**, **customer observations**, and **verified first-hand facts**. Reviews suggest objections and language, not proof of product performance. For each usable claim, save its exact source and confidence. Mark claims that require owning/testing the product. Never turn a review into "I tested it."
3. Identify what the Veo pipeline can show: what can the first frame depict from available listing images, what motion or environment can Veo plausibly animate from those images, and what physical evidence (color, texture change, liquid absorption, before/after) would require real footage and must therefore be excluded from AI-generated clips or flagged as `PROOF_WEAKENED_BY_AI`. A product whose core claim requires unverifiable physical demonstration should be ranked lower unless the seller provides footage.
4. Estimate economics with a range: expected commission per confirmed order, production cost (including estimated Veo API cost per clip at current rate ≈ \$0.05–0.10/s at 720p Fast), sample cost if any, and paid distribution cost if relevant. State the break-even orders/video. Do not forecast orders from views without account data.
5. Rank the shortlist using documented reasons: demonstrability via available images + Veo, demand signal, offer stability, margin, asset rights quality, competition, and risk of misleading claims. Use a score only as an aid; show why the winner beats alternatives and what would change that choice.

## Output and self-review

Produce a `DiscoveryBatch`, one `ProductBrief` per shortlisted SKU, and a one-paragraph selection decision. Each brief must include `verified_claims`, `forbidden_or_unproven_claims`, `visual_proof`, `available_assets[{id, source, permission}]`, `economics` (including `cost_per_video` with Veo estimate), `platform`, and `refresh_after`.

If no candidate has at least one listing image (even with `permission: unknown`) to serve as Veo input, return `NEEDS_EVIDENCE` with the cheapest way to obtain it — typically: contact the seller via platform collaboration tools and request the media kit or permission to use listing images. Do not pass a product merely because it is available in the affiliate account or has high commission.

Before handoff, ask: could a viewer inspect the video and receive a materially different variant or result? Can the Veo pipeline show every important claim truthfully from available images — or does a claim require first-hand use that AI cannot credibly depict? Did I confuse seller text with independent proof? If yes, revise the brief, remove the claim, or mark it `forbidden_or_unproven_claims`.
