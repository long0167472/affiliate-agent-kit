# Shared handoff contracts

Use these fields as the minimum shared language. Store each artifact with a stable ID, creation time, author role, version, and links to source artifacts. JSON, Markdown frontmatter, or database rows are acceptable; the fields matter more than storage format. Never silently overwrite an earlier experiment variant.

## AccountDecision

`decision_id`, `platform`, `observed_at`, `current_account{handle,affiliate_type,follower_count,video_product_link_access,account_health,content_history,audience_fit,privacy_concern}`, `new_account_option{eligibility_path,expected_delay,brand_advantage}`, `recommended_account`, `reasons`, `unknowns_to_verify`, `revisit_trigger`. For TikTok record whether the account has full affiliate, Creator Adjustment, or link-only rights as displayed. For Shopee record whether this KOL/KOC account can attach products in Shopee Video. Browsing-only use of an account is not, by itself, evidence that its outgoing videos are suppressed.

## DiscoveryBatch

`batch_id`, `account_decision_id`, `platform`, `audience_problem`, `searched_at`, `sources[{surface,query_or_category,access_level,observed_at}]`, `candidates[{product_id,exact_sku,listing_url,buyer_problem,visual_demo,demand_signal,competition_or_content_gap,seller_quality,offer_and_commission,sample_or_asset_path,sample_availability,eligibility,evidence_at,uncertainties,decision,reason}]`, `shortlist`, `next_search_if_empty`. Distinguish measured account data from public proxies and missing data.

## ProductBrief

`product_id`, `discovery_batch_id`, `platform`, `sku_and_variant`, `listing_url`, `seller`, `observed_at`, `price_range`, `commission_basis`, `stock_status`, `eligibility{status,source,checked_at}`, `sample_availability`, `audience_problem`, `visual_proof`, `available_assets[{id,source,permission}]`, `verified_claims[{claim,source,observed_at,confidence}]`, `forbidden_or_unproven_claims`, `limitations`, `economics{commission_per_confirmed_order,cost_per_video,break_even_orders}`, `refresh_after`, `status`. `available_assets.permission` is the asset-rights record; use `unknown` until verified.

## CreativePlan

`plan_id`, `product_id`, `target_viewer`, `viewer_moment`, `concepts[{mechanism,first_frame,first_line,promise,proof,cta}]`, `selected_concept`, `storyboard[{start,end,visual,audio,on_screen_text,purpose,asset_id,claim_id}]`, `claim_to_shot_map`, `platform_examples[{url,observed_at,first_frame,hook,shot_progression,product_reveal,proof_moment,cta,mechanism}]`, `hypothesis`, `changed_variable`, `held_constant`, `primary_metric`, `disconfirming_outcome`, `status`. Add a brief comparison explaining which observed mechanism each original concept adapts and what is deliberately different; do not copy wording or footage.

## VideoAsset

`asset_id`, `plan_id`, `variant_id`, `platform`, `render_path`, `checksum`, `duration`, `dimensions`, `first_frame_path`, `source_manifest`, `ai_usage`, `qa_findings[{timestamp,issue,resolution}]`, `unresolved_limits`, `status`.

## PublishRecord

`publish_id`, `asset_id`, `platform`, `account`, `method`, `status`, `prepared_at`, `published_at`, `post_url`, `product_id`, `attachment_verified`, `ai_label`, `commercial_disclosure`, `caption`, `conditions_changed`, `error_or_next_action`.

## ExperimentResult

`experiment_id`, `hypothesis`, `registered_at`, `variants`, `window`, `exposure_counts`, `metrics[{name,numerator,denominator,source,observed_at,status}]`, `relative_lift`, `economics{gross_merchandise_value,pending_commission,confirmed_commission,paid_commission,cancelled_or_refunded_orders,sample_cost,production_cost,ad_spend,net_contribution}`, `confounders`, `interpretation`, `decision`, `next_test`. Merchandise value is not the creator's revenue. Do not call pending commission or gross merchandise value profit. `net_contribution` must state whether it uses confirmed or actually paid commission and which costs are included.

## CycleRecord, event journal, and daily learning

`CycleRecord`: `cycle_id`, `platform`, `account`, `objective`, `budget`, `run_mode`, `journal_path`, `artifact_versions`, `current_state`, `last_run_at`, `last_data_sync_at`, `next_due_at`, `last_daily_review_id`, `state_transitions[{from,to,at,reason,actor,artifact_id,version}]`, `next_action`. The orchestrator chooses a persistent workspace path with the caller; append transitions rather than replacing history, so a resumed run sees why a decision changed. `run_mode` is `simulation`, `assisted`, or `live`, chosen from observed capabilities and authorization; it must appear next to public metrics. If data are stale, say so rather than displaying an old number as current.

`JournalEvent`: `event_id`, `account_id`, `cycle_id` (optional for account-wide events), `event_type`, `happened_at`, `recorded_at`, `timezone`, `actor`, `source`, `source_event_id`, `artifact_id`, `artifact_version`, `platform_object_id`, `payload`, `evidence_refs`. Use an append-only per-account journal for observations, decisions, executions, verifications, reviews, costs, outcomes, errors, and corrections. Persist an event as soon as its state change is known; do not wait for the daily review. Deduplicate connector replays by `(source, source_event_id)` or stable `event_id`. Preserve both event time and recording time so late reports do not rewrite history. A correction links the earlier event and states the changed value and reason. Metric events must state `measurement_kind` (`snapshot` or `delta`), metric name, unit, observation window, and source object ID; order/commission events must use the platform order or payout reference and record status transitions. Reconcile latest snapshots and order states by those keys instead of summing repeated cumulative reports. Allocate shared sample or production costs by a stated rule once, without copying the full expense into every product cycle. Never log secrets, tokens, buyer identity, or unnecessary personal data. `ActionRecord` and `ReviewRecord` are linked journal events, not separate unaudited narratives.

`DailyReview`: `review_id`, `review_version`, `platform`, `account`, `local_date`, `timezone`, `window_start`, `window_end`, `generated_at`, `data_as_of`, `source_sync_status`, `journal_event_ids`, `previous_review_id`, `open_action_followups[{action_id,state,due_at,execution_evidence,outcome_or_blocker}]`, `published_assets`, `funnel_snapshot{exposure,retention,product_clicks,orders,pending_commission,confirmed_commission,paid_commission,returns}`, `costs{sample,production,ads,other,allocation_basis}`, `hypotheses_reviewed[{hypothesis_id,expected,observed,denominators,interpretation,confidence,alternatives}]`, `decisions[{continue_iterate_pause_or_inconclusive,reason}]`, `what_changed`, `what_failed_or_is_unknown`, `next_test{one_variable,primary_metric,decision_threshold,owner,due_at}`, `reviewer_record_id`. Key `review_id` deterministically by platform, account and local date; key each immutable version by `review_id` plus `review_version` so retries cannot create duplicate daily conclusions. Create one primary daily review per account and local date after the day's cutoff; include a `NO_ACTIVITY` or `DATA_UNAVAILABLE` entry when appropriate rather than fabricating a learning. `open_action_followups` checks every due or still-open action, including actions carried from older days. The next day's plan must cite this review. A daily operational review is not a final 24-hour post-performance comparison until each compared post has a full comparable observation window. Commission and returns may mature later; append a versioned follow-up review or correction when settled data arrive instead of rewriting the original review. Net contribution must state the cost basis and commission maturity.

`ActionRecord`: `action_id`, `cycle_id`, `decided_at`, `actor`, `action_scope` (`internal` or `platform`), `target_platform`, `target_object`, `proposed_action`, `reason`, `evidence_refs`, `metric_snapshot{source,observation_window,observed_at,values}`, `expected_effect`, `execution_status`, `executed_at`, `external_id_or_url`, `verification_evidence`, `observed_outcome`, `failure_or_rollback`. Use statuses `PROPOSED`, `SIMULATED`, `PREPARED`, `EXECUTED`, and `VERIFIED` literally. A platform action needs its external ID plus an independent readback to become `VERIFIED`; an internal action needs the resulting artifact ID/version and a check that the change exists. A decision log is not proof that an action occurred.

`ReviewRecord`: `review_id`, `cycle_id`, `reviewer_agent_id`, `lens`, `artifact_id`, `artifact_version`, `reviewed_at`, `findings[{severity,evidence,repair}]`, `decision`. A revised artifact receives a new version and a new review; never attach an old `READY` result to an edited video.

## Task result vocabulary

- `DONE`: artifact exists and required evidence is attached.
- `NEEDS_EVIDENCE` / `NEEDS_SHOT`: a specific fact or visual must be obtained; include the minimal request.
- `PREPARED`: ready for a platform action that is not yet completed.
- `BLOCKED`: capability or external state prevents progress; include evidence and recovery path.
- `INCONCLUSIVE`: data do not separate competing explanations; specify the next observation.

The orchestrator may route a result back once with a precise defect. Further revision requires a new observation, asset, or hypothesis rather than repeated subjective praise/rejection.
