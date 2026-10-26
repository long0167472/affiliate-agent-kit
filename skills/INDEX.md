# Affiliate agent skill set

Seven independent Codex skills: five operating roles, one on-demand cross-reviewer, and one orchestrator. The intended starting sequence is product research → creative plan → video → platform publication → measurement. Reviewers inspect each handoff independently. The [worked example](references/worked-example.md) shows the required level of storyboard and experiment detail.

| Role | Artifact owned | Skill |
|---|---|---|
| Product intelligence | DiscoveryBatch, ProductBrief | [aff-product-intelligence](aff-product-intelligence/SKILL.md) |
| Creative strategist | CreativePlan | [aff-creative-strategist](aff-creative-strategist/SKILL.md) |
| Video producer | VideoAsset | [aff-video-producer](aff-video-producer/SKILL.md) |
| Publisher | PublishRecord | [aff-publisher](aff-publisher/SKILL.md) |
| Growth analyst | ExperimentResult | [aff-growth-analyst](aff-growth-analyst/SKILL.md) |
| Independent reviewer | Evidence-based findings | [aff-creative-reviewer](aff-creative-reviewer/SKILL.md) |
| Orchestrator | AccountDecision, state and next decision | [aff-orchestrator](aff-orchestrator/SKILL.md) |

The portable package has also been installed as seven discoverable skills in this device's Codex skills directory. It is **not** connected to affiliate accounts, media tools, analytics, or publishing APIs yet. The first real run should begin with the authorized account state, a niche or audience hypothesis, and available sample/footage budget. Product intelligence must discover candidates itself; a product URL is optional. That run will reveal which account-specific capabilities need implementation.

This Git package includes `scripts/install-skills.ps1` at its root for Windows Codex installation. The current video tool decision, including Google AI Pro/Flow, is in [`docs/production-tools.md`](../docs/production-tools.md).

For unattended execution, use the separate [controller architecture](../docs/affiliate-controller-architecture.md): a durable scheduler and journal invoke these skills as finite jobs, with an LLM provider selected according to actual ChatGPT OAuth entitlement or API access. A Codex chat or Goal is not the runtime state store.

## Nhật ký và vòng học hằng ngày

Orchestrator ghi `JournalEvent` dạng append-only theo từng tài khoản ngay khi có quan sát, quyết định, hành động, xác minh, chi phí, kết quả hoặc lỗi. Sau khi đóng ngày theo múi giờ của tài khoản, `aff-growth-analyst` lập `DailyReview`; reviewer độc lập kiểm tra kết luận và kế hoạch thử nghiệm ngày sau phải dẫn lại review đó. Ngày không hoạt động hay dữ liệu chưa đồng bộ cũng có bản ghi; số liệu 24 giờ đầu là tạm thời, hoa hồng/hoàn đơn được đối soát ở các bản cập nhật sau. Schema và quy tắc chống ghi trùng nằm trong [contracts](references/contracts.md). Cần một scheduler và kết nối dữ liệu thực khi triển khai agent; bộ skill hiện chỉ định nghĩa hành vi và hồ sơ lưu vết.
