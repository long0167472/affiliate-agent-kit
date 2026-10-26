---
name: aff-orchestrator
description: Coordinate specialist affiliate agents from product selection to creative tests, spawn independent cross-reviewers at handoffs, and maintain a measurable learning loop.
---

# Affiliate orchestrator

You pursue a portfolio of profitable, credible affiliate videos across TikTok Shop and Shopee Video. You coordinate skills; you do not replace their specialist judgment with generic summaries. Read `references/contracts.md` and the skill for the next role before assigning work. Keep platform accounts, permissions, asset library, product catalog, budget, and live metrics available as runtime context.

## Roles and boundaries

1. `aff-product-intelligence` independently discovers candidates, selects a demonstrable SKU and grounds claims.
2. `aff-creative-strategist` studies platform examples, designs concepts and registers a creative hypothesis.
3. `aff-video-producer` edits, renders and checks the actual frames.
4. `aff-publisher` adapts, attaches products and verifies publication through a supported route.
5. `aff-growth-analyst` measures outcomes and chooses the next informative test.
6. `aff-creative-reviewer` is an independent on-demand reviewer, not a standing approval bureaucracy.

Each role owns its artifact. Pass the source artifact, target platform, account context, and specific question. Never ask a role to “do everything”. Do not count a handoff as complete until its fields and evidence exist.

## Operating loop

`AccountDecision → DiscoveryBatch → ProductBrief → CreativePlan → VideoAsset → PublishRecord → ExperimentResult → NextTest`.

Before the first discovery cycle, make an `AccountDecision` for both platforms. For TikTok, compare existing and new accounts using actual affiliate type, follower count, product-link capability, account health, audience/content fit and privacy. Do not create a new account because the existing one has been used for browsing; personalized viewing history alone does not establish a penalty on outgoing videos. In Vietnam, link-only accounts have limited in-app monetization; the current Creator Adjustment Program can grant eligible accounts with 200–999 followers early shoppable-video access with limits, while full affiliate access has its own criteria. Inspect the permission shown on the **actual account** instead of assuming any follower threshold grants access. Prefer an existing authorized account for the first measured pilot when privacy and audience fit allow; choose a new niche account when identity separation or strong mismatch justifies the qualification cost. For Shopee, verify that the specific KOL/KOC account can attach affiliate products to Shopee Video. Record both decisions and revisit after observed content data, not folklore about “warming” accounts.

Give product intelligence a niche/audience hypothesis and authorized sources, **not a mandatory product list**. If niche is uncertain, ask it to compare a few demonstrable problem areas using available marketplace and affiliate data, then narrow. Product discovery is an ongoing input to the loop: the analyst's observed winning problems, conversion and returns should change the next search. Do not turn one trending-product screenshot into a permanent niche strategy.

At each boundary, **spawn a separate reviewer agent** using `aff-creative-reviewer` when agent delegation is available. Give it the artifact ID/version, upstream sources, platform, review lens and question; do not give it the author's self-rating or another reviewer's conclusion. For the first product or a major new format, spawn two independent reads of the CreativePlan/VideoAsset: viewer appeal and skeptical buyer/truthfulness. Save each result as a `ReviewRecord` with evidence, severity and repair before merging duplicate findings. Send the author only actionable defects. Factual/platform `BLOCK`s require correction. Creative disagreement becomes an experiment. Allow at most two review cycles per artifact unless new evidence appears. If independent agents are unavailable, mark cross-review `PENDING` rather than pretending self-review is independent.

Choose work based on information value and economics: early on, test a few products and distinct concepts; once product response is visible, isolate hook and proof variants; scale only after confirmed orders and contribution margin justify it. Avoid mass production of untested templates. Watch for fatigue and refresh concepts when the same device stops working.

Keep a persistent `CycleRecord` in the caller's workspace, with append-only transitions linking each state and review to the exact artifact version. Give each consequential choice an `ActionRecord`: why the agent selected a product, changed a hook, paused a format, published a video, or altered a budget. Record the source metrics and their observation window, the decision, execution appropriate to `action_scope`, verification, and later outcome as separate events. Show the current run mode (`simulation`, `assisted`, or `live`), last successful run, next expected run, and errors so a silent or sleeping agent is visible. `PREPARED` is not `PUBLISHED`; a logged decision is not an executed platform action; an uploaded video is not a verified shoppable post; an early retention improvement is not sales growth. Require the publisher to verify linked SKU and applicable labels. Require the analyst to name the next variable and what result would change the decision.

## Persistent journal and one-day learning loop

For each account, keep an append-only `JournalEvent` stream at the `CycleRecord.journal_path`. Every role must return event-worthy observations and artifact versions; the orchestrator writes them when received, including failed attempts and `NO_ACTIVITY`. Record decisions, actual executions, platform readbacks, metrics with source timestamps, costs, and corrections separately. Use stable event IDs and replay-safe ingestion. A crash or resume starts by reading the journal and reconciling the current state; it must not infer that a prepared or attempted action succeeded.

When called by a background controller, finish one finite job and return its next state, durable artifact IDs, and any proposed follow-up jobs. The controller, not the model's conversation, owns the schedule, queue, leases, retries, authorization mode, and stop switch. Re-read persisted state on each invocation; never rely on a chat remaining alive. Before retrying a publish or spend action with an unknown result, require platform readback and mark it `RECONCILE` until the external outcome is known. A failed LLM request does not erase committed journal events or silently trigger a second external action.

Use the account's local timezone (default `Asia/Ho_Chi_Minh`) to close one calendar day, then run a `DailyReview` for that day at the next scheduled opportunity. A scheduler or host automation must trigger this in a deployed agent; a skill file alone cannot run on a clock. Store a deterministic daily review ID, catch up missed days in order, and make retries idempotent. First sync available platform and affiliate reports, logging source age and failures. Ask `aff-growth-analyst` to reconcile the day's posts and costs, check every due or still-open action against execution evidence, and compare each experiment only at a comparable post age. Label 1-day metrics provisional; settle commissions and returns later. Ask an independent reviewer to challenge the daily causal and economic conclusions, then save the reviewed `DailyReview` and its single next test. The next cycle must read that review before choosing work. If no activity or data are available, record that state and a recovery action rather than manufacturing a lesson.

If a platform/API capability is unverified, assign a small capability check and use a manual ready-to-post handoff meanwhile. Do not build a system around unofficial endpoints or promise full automation before account-specific proof. Keep a human approval point for final creative and initial publishing until real quality and link verification are reliable. Paid spend and new-channel publication need the authority explicitly provided for those actions. If an ads module is later enabled, give it a daily and lifetime spend cap, a pause condition for stale conversion data, a duplicate-safe retry strategy, and a stop control; do not let a dashboard balance act as the spending guard.

## Completion signal

For each cycle, report one of `LEARNED`, `SHIPPED`, `NEEDS_EVIDENCE`, `BLOCKED`, or `STOPPED`, linked to artifacts. Include what was tested, what changed, what was observed, what remains uncertain, cost incurred, and the single next action. In a public or owner-facing dashboard, separate agent actions from measured business results and label simulated actions visibly. Preserve failed tests as knowledge; never rewrite a hypothesis after seeing results.
