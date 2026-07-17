# INIT-PROMPT — New Game Initialization

> Entry point for an AI agent (Claude / Gemini / Copilot) to bootstrap a
> brand-new interactive novel game using this repository's rules. Follow these
> steps in order. Do not improvise around them.

---

## 0. Prerequisites

Confirm before starting:

- `AGENTS.md` exists and is the current source of truth (v1.0.0).
- Synced rule files are up to date: `python scripts/sync_rules.py`.
- At least one LLM API key is set in `.env` (copy from `.env.example`).
- (Optional) MCP servers configured: `cp mcp.example.json mcp.json`.
- The 21 skill documents under `docs/skills/` and 4 prompts under
  `docs/prompts/` are present.

---

## 1. Load the rules

1. Read `AGENTS.md` end to end. It is the single source of truth.
2. Read every skill document it references via `@docs/skills/*.md`.
3. Read the four engine prompts under `docs/prompts/`:
   - `system-prompt.md` — base system prompt & persona.
   - `narrator-engine.md` — narration generation.
   - `npc-engine.md` — NPC behavior & dialogue.
   - `game-master.md` — rules arbitration & world simulation.
4. Acknowledge the rule priority order (see README → Rule Priority).

---

## 2. Collect the game seed

Run this seed-collection flow with the human author. Ask, in order, and record
every answer:

1. **Genre** — fantasy / sci-fi / mystery / horror / romance / mixed?
   (see `@docs/skills/genre-system.md`)
2. **Setting** — world, era, location, key factions.
3. **Protagonist** — name, background, starting abilities, motivation.
4. **Tone & rating** — lighthearted / grimdark; all-ages / mature.
5. **Core conflict** — the central tension driving the story.
6. **Scope** — one-shot session vs. multi-session campaign.
7. **Mechanics toggles** — combat on/off, inventory on/off, romance on/off,
   permadeath on/off, etc.
8. **Difficulty** — starting difficulty band
   (see `@docs/skills/difficulty-engine.md`).
9. **Taboos / hard limits** — content the author never wants generated.
10. **Win / lose conditions** — what does success or failure look like?

Persist the answers to `.game-state/seed.json`.

---

## 3. First-time setup

1. **State machine** — initialize `.game-state/state.json` with the opening
   node, default flags, and counters (see `@docs/skills/game-state-machine.md`).
2. **Memory** — bootstrap `.game-state/memory.json` with seed facts
   (see `@docs/skills/memory-system.md`).
3. **Narrative tree** — create `.game-state/narrative-tree.json` with the
   opening scene as the root node (see `@docs/skills/branching-narrative.md`).
4. **NPCs** — register `.game-state/npcs.json` from the seed
   (see `@docs/skills/npc-ai.md`).
5. **Difficulty profile** — write `.game-state/difficulty.json`
   (see `@docs/skills/difficulty-engine.md`).
6. **Anti-dumb-AI check** — run the checklist against the seed
   (see `@docs/skills/anti-dumb-ai.md`).
7. **Security checklist** — verify no secrets are written into state
   (see `@docs/skills/security-checklist.md`).
8. **Commit** — snapshot the initial game state with the git SOP
   (see `@docs/skills/git-sop.md`).

---

## 4. Start the first session

1. Load `docs/prompts/system-prompt.md` as the base prompt.
2. Compose the opening scene using `@docs/prompts/narrator-engine.md`.
3. Hand control to the player.
4. **Per turn:** read player input → validate against the current state node →
   update state → narrate the next beat → offer 2–4 meaningful choices.
5. **Per session end:** run `@docs/skills/game-evaluation.md`, update memory,
   save a snapshot to `.game-saves/`.

---

## 5. Guardrails

- Never bypass the anti-dumb-AI standard (§12).
- Never edit `AGENTS.md` or any rule file during a game; rules are immutable
  at runtime.
- Always validate player choices against the current state-machine node before
  narrating consequences.
- Always persist state to `.game-state/` before narrating the next beat.
- If context budget is exceeded, follow `@docs/skills/context-management.md`
  before continuing.
