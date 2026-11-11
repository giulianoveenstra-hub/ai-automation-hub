# AI Automation Hub

Minimal, source-aware instructions and notes for AI-assisted work. **This is documentation/configuration, not an active automation service.**

## Read only what you need

| File | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Short repository agent rules |
| [ARVO-STATUS.md](ARVO-STATUS.md) | Dated ARVO snapshot: done, waiting, open, decisions |
| [Supplier comparison](ocs/supplier-comparison.md) | Specific supplier facts and questions |
| [Supplier scoring](ocs/ocs/supplier-scoring.md) | Evidence-based evaluation rubric |
| [AI-HUB-PLAN.md](AI-HUB-PLAN.md) | Original strategic goals and safeguards |
| [ARVO update skill](.agents/skills/arvo-project-update/SKILL.md) | Optional focused workflow |

## Suggested request to ChatGPT Work

"Use GitHub repository `giulianoveenstra-hub/ai-automation-hub`; first read `ARVO-STATUS.md`. Load other files or live sources only if the task needs them. Avoid repeating completed work; report unknowns. Do not send or order anything without approval."

**Limit:** A connected Work agent must actually retrieve the documents; GitHub files do not automatically change Work memory, model, token budgets or billing. A GitHub snapshot does not auto-sync with other systems.

## Activation and limits

Codex can load root `AGENTS.md` in a checkout and discover the matching skill under `.agents/skills/`; Copilot support depends on its client loading `.github/copilot-instructions.md`. These files configure guidance only. This integration does not change model selection, reasoning effort, billing, global settings or external integrations; no measured token savings are claimed. The rules become available on this branch, and on `main` only after merge.
