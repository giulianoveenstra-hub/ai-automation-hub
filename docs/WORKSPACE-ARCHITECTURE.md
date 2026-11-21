# Multi-project development workspace – proposed architecture

Status: **proposal for review**, 2026-11-21. This is general process documentation; it does not create Finder folders, cloud projects, connectors or synchronized memory.

## Separation of responsibilities

| System | Source of truth for | Important limit |
|---|---|---|
| GitHub | Versioned code, small non-secret config and developer documentation | Not a general storage vault for invoices or personal documents |
| Claude Code (local/cloud) | Code authoring, testing and repository changes | Code sessions and `CLAUDE.md` are not automatically synced with Claude chat project instructions |
| ChatGPT | Cross-project planning, research, connected actions | Must read a live source instead of assuming remembered project status |
| iCloud Drive | Approved briefs, contracts, PDFs, images and other non-code business files | A cloud code session does not automatically read a Mac's iCloud Drive |
| Finder `~/Developer` | Local Git working copies | Keep active repositories outside automatically synced iCloud folders |

## Repository boundaries

Existing:
- `ai-automation-hub` – shared rules and automation guidance; **public**, so no secrets/private client data.
- `arvo-content-studio` – ARVO content and reel production; **private**.

Proposed new repositories only when the projects require actual versioned source code:
- `localweb-studio` (private): reusable website starter, components, checklists, design guidelines, CI and tests. No client secrets.
- `localweb-client-<slug>` (private): one real client website per repository; use a separate demo repository when appropriate.
- `stay-awhile-platform` (private): event registration/website development, only if required.
- `arvo-storefront` (private): Shopify or storefront source code, only if custom code exists.

Other non-code projects do not require repositories merely for being active.

## Local paths (create after auditing existing folders)

```text
~/Developer/
  ai-automation-hub/
  arvo-content-studio/
  localweb-studio/
  localweb-client-.../
  stay-awhile-platform/

iCloud Drive/Business/
  00_Inbox/
  01_ARVO/
  02_Event_Building/
  03_LocalWeb_Studio/
    01_Briefings/
    02_Customer_Materials/
    03_Proposals/
    04_Approvals/
  04_Vision_2031/
  90_Archive/
```

These are recommended *logical* paths, not proof that the folders exist. Check existing paths, duplicates, pending uploads and sync state before moving or renaming anything.

## Agent guidance and skills

- Global `~/.claude/CLAUDE.md`: short, stable defaults (German language, precision, safety, minimal changes, verification).
- Repository root `CLAUDE.md`: technology, tests, architecture and repository-specific workflow.
- Optional narrow skills only when they are used regularly; do not install every marketplace plugin globally.
- `.github/copilot-instructions.md` and `AGENTS.md`: keep intentionally concise, avoid duplicating complete instructions across tools.
- Use explicit brief/status files for fresh project facts; do not use an agent's conversational memory as the authoritative database.

## Operating workflow

1. Intake and select one project; inspect its current source and state.
2. Write a concise issue/brief with acceptance criteria.
3. Use a dedicated Git branch or worktree.
4. Implement and test; do not assume tests pass without executing them.
5. Open a pull request; review changes before merging.
6. Deploy to preview only with permission; publish production only when approved.
7. Keep confidential client materials in a restricted location and commit code only to the correct private repository.
8. Summarize completed work, verification, remaining risks and next steps.

## Safety and migration

- Preserve current repositories and their open pull requests.
- Inventory Claude chat/code projects, imported skills, plugins, MCPs, configuration files and local folders before making changes.
- Export unique chats/files/instructions before deleting old Claude projects; a GitHub repository does not back up those chat histories.
- Never mass-uninstall or remove until exact targets and their dependencies are confirmed.
- Prefer a reviewable migration plan and recoverable snapshots before destructive operations.
- Review `ai-automation-hub` public visibility and existing business information before using it as any broader knowledge store.

## Current checks needed

- Confirm which GitHub projects are mounted inside Claude Code and which are local-only.
- Verify the local Finder layout and iCloud sync; no direct macOS inspection was performed in this repository update.
- Review current Claude code settings and installed plugin versions.
- Decide whether to keep the public hub only for generic examples or eventually migrate private instructions into a separate private repository.
