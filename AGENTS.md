# Lazy Agent – Repository Rules

**Goal:** minimum sufficient context while maintaining accuracy, verification and safety.

ARVO is the main project. These are repository instructions; they do not configure the runtime.

1. **Read before act:** determine the task and likely affected files first. Do not inspect the full repository without a reason.
2. **Progressive disclosure:** for ARVO start at `ARVO-STATUS.md`. Read `ocs/supplier-comparison.md` for suppliers, `ocs/ocs/supplier-scoring.md` for rating criteria, and `AI-HUB-PLAN.md` for strategic constraints only if necessary.
3. **Reuse before research:** reuse current, evidenced decisions and results. Verify volatile information against the latest authorized source; never treat snapshots as live inbox, Shopify or website data.
4. **No duplicate work:** track `DONE`, `OPEN`, `WAITING`, `DECIDED`, and never reassign already completed actions without evidence of a new requirement.
5. **Minimize calls and output:** request only relevant sections; batch independent reads if useful; avoid repeating searches. Prefer short, actionable outputs unless depth is requested.
6. **Verify before commit:** inspect the current file/version before editing, make the smallest coherent change, validate references and changed content, report what was and was not tested.
7. **Safety:** do not fabricate prices, measurements, commitments, communications or availability. No credentials or private correspondence in this public repo. Supplier orders, external communication, publishing and financial commitments require human authorization.
No paid external actions. Do not change settings outside this repository without explicit user approval. Existing authorization in the current task applies to its requested branch and pull request.

8. **Model choice:** use cheaper models for routine work only if the actual running product exposes model selection; this file cannot set ChatGPT Work credits, model routing or token billing.

For recurring supplier/status updates, use `.agents/skills/arvo-project-update/SKILL.md` only when the task matches. Timestamp status and separate user reports from independently verified facts.
