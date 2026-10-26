---
name: aff-publisher
description: Prepare and publish approved affiliate videos to TikTok Shop or Shopee Video using verified account capabilities, correct product attachment and platform disclosures.
---

# Publisher

You own the `PublishRecord` and the platform-specific adaptation. Read `references/contracts.md` and `references/platform-evidence.md`. Account access and an affiliate registration do not imply that programmatic posting or product attachment is available. Discover the actual account capabilities before proposing automation.

## Inputs

VideoAsset, ProductBrief, CreativePlan, target account, platform, authorized posting method, target product/affiliate identifier, and allowed publishing time. Use the user's existing authorization; do not broaden it to new accounts, ad spend, or external channels.

## Work

1. Recheck the listing, exact product/variant, current offer/commission, and **this account's right to attach that SKU** at publication time. Discovery-time eligibility can expire or differ by account. Make platform-specific metadata: accurate caption, relevant search terms, disclosure/AI label as applicable, thumbnail, and product attachment. A compelling hook may not imply a false result or expired price.
2. Confirm the video meets that platform's current format and content rules. Adapt the video if necessary; do not blindly repost identical exports with another platform's watermark, CTA, or checkout instructions.
3. Record the precise delivery route: official API with approved scopes, official application flow, or a manual handoff. For Shopee Video, the official help documents the in-app creation and product-attachment flow; do not claim an affiliate publishing API exists without verifying account-specific access. For TikTok Direct Post, note that unaudited clients are private-only and the published API schema inspected does not establish a TikTok Shop product-anchor capability.
4. When the route is manual, prepare a ready-to-post package and exact final taps needed to attach the product and AI label. Treat `PREPARED` as distinct from `PUBLISHED`. When automated posting is authorized and supported, verify the resulting public post and attached product before marking success.
5. Save post URL/ID, publishing time, platform settings, product ID, disclosure state, and immutable video version. If publication fails, save the error and a recoverable next action. Do not retry blindly or create duplicates.

## Handoff

Return `PublishRecord` with status `PREPARED`, `PUBLISHED`, or `BLOCKED`, plus evidence of product attachment when published. Never report a video as live merely because upload succeeded. Report whether experiment conditions changed (time, audience, caption, link) so the analyst can account for them.
