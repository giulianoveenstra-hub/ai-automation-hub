# Claude Code – AI Automation Hub

This repository is a **shared automation guidance and coordination repository**, not a universal workspace containing every customer's documents or code.

## Read minimally
1. Read `AGENTS.md` for safety and editing conventions.
2. Read `docs/WORKSPACE-ARCHITECTURE.md` only when organizing repositories, environments or cross-project workflows.
3. For ARVO status work, consult `ARVO-STATUS.md` and relevant supplier files, verifying freshness before acting.
4. For other projects, work in that project's own private repository. Do not assume this repository contains their up-to-date state.

## Execution policy
- Before editing: inspect the exact files, current branch, outstanding changes and relevant open pull requests.
- Keep changes isolated on new branches; test and provide a pull request for review.
- Never commit secrets, customer personal data, copyrighted media or unpublished business records to a public repository.
- Never remove or overwrite repositories, projects, plugins, skills, files or settings without a prior inventory, a recoverable backup and explicit confirmation of the exact targets.
- Use project-specific `CLAUDE.md`, with only short, general rules in any global `~/.claude/CLAUDE.md`.
- Do not claim that ChatGPT or Claude automatically syncs memory, chats, iCloud files, or other repositories.
- Prefer lean, composable solutions and avoid unnecessary paid services or broad permissions.
- Report actual changes, checks and outstanding limitations. No unverified completion claims.

## Execution environment and efficient use
- Prefer GitHub-backed Claude Code **cloud sessions** for longer-running repository tasks that must continue while the MacBook sleeps or is closed. Local sessions stop progressing when the Mac sleeps; cloud sessions do not grant access to local Finder or iCloud files.
- Finish any Mac-local inventory/configuration locally, save only reviewed non-secret artifacts to the appropriate private repository, then run separately authorized cloud tasks from that repository.
- Use minimal task-relevant context and targeted file reads. Default to a cost-effective model/effort for routine changes; escalate for genuinely complex design, security or architecture work. Do not switch models repeatedly in a large session.
- Scope tools and skills per task, avoid unneeded parallel agents, summarize context between phases and use a fresh session for unrelated work. Never skip required tests or security checks just to reduce tokens.
- Report what executed locally, what ran in cloud, what was measured, and what remains unverified.
