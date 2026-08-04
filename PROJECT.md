# AgentSeed — Project Overview

## What Is This?

**AgentSeed** is a unified Persona-Governance Platform for AI Agents — one command to give a blank agent a complete brain.

It's not business code. It's a **rule-and-persona hub** that integrates **6 independent rule systems** into a single repository, then generates platform-native entry files for **13 AI coding assistants**.

## Core Architecture

```
┌─────────────────────────────────────────┐
│            GOVERNANCE ENGINE             │
│  core/governance.md    — P0 safety       │
│  core/constraints.yaml — hooks           │
│  core/self-evolution.md — ★ Gap auto-fix │
│  core/agent-modes.md   — Task/Proj/Auto  │
│  core/dar-spec.md      — Search quality  │
│  core/persona-router.md — Persona select │
├─────────────────────────────────────────┤
│            PERSONA PACKS                 │
│  personas/coding/  — Software Engineer   │
│  personas/novel/  — Novelist             │
│  personas/paper/  — Academic             │
│  personas/conversation/ — Generalist     │
│  personas/interactive-novel/ — Game Write│
│  personas/agent-builder/ — Agent Design  │
├─────────────────────────────────────────┤
│            SYNC ENGINE                   │
│  13 platforms: Claude Code, Cursor,      │
│  Copilot, Trae, Gemini, Windsurf,        │
│  Cline, Continue, Amazon Q, Qodo,        │
│  Lingma, Comate, AGENTS.md               │
└─────────────────────────────────────────┘
```

## Key Design Decisions

1. **Persona Packs are mutually exclusive** — you're either coding or writing a novel; rules shouldn't conflict
2. **Governance Engine is non-negotiable** — safety, security, and self-evolution apply regardless of persona
3. **Skeleton mode by default** — core rules inline, skills/capabilities loaded on-demand to stay under platform limits
4. **Self-Evolution Engine** — agents detect their own capability gaps and self-heal (search → clone → install → verify)
5. **13-platform sync** — one manifest, generated for every AI coding tool

## Rule Priority

```
P0 Core (safety/permissions) > P1 User Confirmed > P2 Main Persona > P3 Capabilities > P4 Model Default
```

## Language Policy

- System prompts: English
- Output: User's language
- Code comments: User's language

## Development

```bash
pip install -e .
python -m pytest tests/
python scripts/validate_rules.py
agentseed list
agentseed verify
```

See `docs/AGENTSEED_ARCHITECTURE.md` for the full design document.
