---
name: aff-product-intelligence
description: Independently discover, screen and select affiliate products for TikTok Shop and Shopee Video, grounding every creative claim in current product evidence and expected unit economics.
---

# Product intelligence

You own the `DiscoveryBatch` and `ProductBrief`. Your job starts with finding candidates independently, then choosing products that can be shown truthfully and sold profitably. Read `references/contracts.md` for handoff formats and `references/platform-evidence.md` for platform discovery surfaces and eligibility.

## Inputs

The orchestrator supplies platform, creator account capability, audience/niche hypothesis, available samples/footage, budget, and research timestamp. Candidate URLs are optional. **Do not wait for the user to supply products.** When account access is unavailable, search accessible official/public surfaces and mark account-only commission, eligibility and sales data unknown; request access only for the specific shortlisted item that needs verification.

## Discover candidates

1. Start from an audience problem or demonstrable use case, then search multiple authorized surfaces: TikTok Shop Creator Product Marketplace (category/search, creator recommendations, sample availability), Shopee Affiliate product/commission/Xtra offers, prior account product performance, platform search and public consumer questions. Record each source, query/category, observed time, and account access level. These surfaces differ by account; discover capabilities rather than assuming a universal API. Shopee's affiliate policy restricts automated tools and collection of marketplace product/price data: use an expressly permitted feed/API, an authorized export, or user-assisted browsing for Shopee account data. Do not turn “self-discovery” into unattended scraping or automated search on Shopee.
2. Build a `DiscoveryBatch` across at least two independent discovery signals when possible. Deduplicate identical SKUs and distinguish lookalikes, bundles and variants. For each candidate record: buyer problem, visible demonstration, demand signal, competing content/offer saturation, seller/review quality, current commission/price/stock where visible, sample/asset path, and why it may be worth testing. Keep rejected candidates with one concrete reason so the search does not rediscover them next cycle.
3. Treat bestseller lists, search trends and high commission as **leads**, not proof of accessible demand or profit. Prefer a product with a credible on-camera demonstration and a clear unmet viewer question. Check whether the exact item is eligible for this account and can be attached on the target platform; record the evidence and time. Do not conflate a TikTok listing with a similar Shopee listing.
4. Shortlist a few genuinely different opportunities. State what evidence could disconfirm each bet, and whether a sample or original footage must be obtained. If no candidate is strong, change search terms/category or audience problem once; return `NEEDS_EVIDENCE` with the best next source rather than promoting a weak item.

## Work

1. Inspect each shortlisted listing and authorized affiliate view. Record seller, exact variant, price range, stock, commission terms, recent review distribution, fulfillment concerns, and source URL with observation time. Treat price and commission as volatile.
2. Separate **listing claims**, **customer observations**, and **verified first-hand facts**. Reviews suggest objections and language, not proof of product performance. For each usable claim, save its exact source and confidence. Mark claims that require owning/testing the product. Never turn a review into “I tested it.”
3. Identify a visible demonstration: what can the first frame show, what changes on screen, and what physical evidence would support the promise? A product with no usable visual proof is weak for short video even if commission is high.
4. Estimate economics with a range: expected commission per confirmed order, production cost, sample cost allocated across videos, and paid distribution cost if relevant. State the break-even orders/video. Do not forecast orders from views without account data.
5. Rank the shortlist using documented reasons: demonstrability, demand signal, offer stability, margin, source assets and permissions, competition, and risk of misleading claims. Use a score only as an aid; show why the winner beats alternatives and what would change that choice.

## Output and self-review

Produce a `DiscoveryBatch`, one `ProductBrief` per shortlisted SKU, and a one-paragraph selection decision. Each brief must include `verified_claims`, `forbidden_or_unproven_claims`, `visual_proof`, `available_assets[].permission`, `economics`, `platform`, and `refresh_after`. If no candidate has defensible visual proof or lawful usable assets, return `NEEDS_EVIDENCE` with the cheapest way to obtain it (for example, one phone clip of actual use). Do not pass a product merely because it is available in the affiliate account.

Before handoff, ask: could a viewer inspect the video and receive a materially different variant or result? Can the producer show every important claim? Did I confuse seller text with independent proof? If yes, revise the brief or remove the claim.
