# AgentSeed — Project Overview

## What Is This?

**AgentSeed** is a high-constraint governance framework for autonomous agents — one command to wrap a blank agent in a non-negotiable safety layer, then plug in the scenario pack that fits the task at hand.

It's not business code. It's a **governance kernel + pluggable scenario packs** that integrates independent rule systems into a single repository, then generates platform-native entry files for **15 AI agent tools** (Claude Code, Cursor, Copilot, Windsurf, Trae, Gemini, Cline, Continue, Amazon Q, Codex, Qodo, Lingma, Comate, QwenWork, and the universal AGENTS.md).

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│  L4 RUNTIME SERVICES  CLI(--json) · MCP Server · HTTP  │
├─────────────────────────────────────────────────────────┤
│  L3 PLATFORM ADAPTERS  15 platforms + pre-tool-use hooks│
├─────────────────────────────────────────────────────────┤
│  L2 CAPABILITY PLUGINS research · testing · review · dar│  ← on-demand
├─────────────────────────────────────────────────────────┤
│  L1 SCENARIO PACKS     coding · novel · paper · …(ext.) │  ← mutually exclusive
├─────────────────────────────────────────────────────────┤
│  L0 GOVERNANCE KERNEL  P0 red lines · budget · failstop │  ← immutable
└─────────────────────────────────────────────────────────┘
      cross-cutting: self-evolution engine (gap detect)
      foundation: three registries (scenario / capability / platform)
```

- **L0 Governance Kernel (immutable)** — P0 safety, secrecy, truthfulness, instruction budget, fail-stop. No scenario pack can override it.
- **L1 Scenario Packs (pluggable, mutually exclusive)** — each pack = scenario protocol + prompts + skills + capability whitelist + routing anchors. Six starter packs ship; adding a scenario is a directory + a manifest, never a kernel change.
- **L2 Capability Plugins (additive, on-demand)** — enabled/disabled by the active scenario pack; loaded via on-demand index to respect the instruction budget.
- **L3 Platform Adapters** — same rule set rendered into each tool's native format, plus pre-tool-use interceptors.
- **L4 Runtime Services** — CLI (with `--json`), MCP Server (stdio/HTTP), runtime governance checks.

## Key Design Decisions

1. **Scenario packs are mutually exclusive** — you're either coding or writing a novel; rules shouldn't conflict
2. **Governance kernel is non-negotiable** — safety, security, and self-evolution apply regardless of scenario pack
3. **Skeleton mode by default** — kernel + active pack inline, skills/capabilities loaded on-demand to stay under platform limits
4. **Self-Evolution Engine** — agents detect their own capability gaps and self-heal (search → clone → install → verify)
5. **15-platform sync** — one manifest, generated for every AI agent tool
6. **Open registries** — scenario / capability / platform registries make the pack catalog extensible without kernel changes

## Rule Priority

```
P0 Kernel (safety/permissions) > P1 User Confirmed > P2 Main Scenario Pack > P3 Capabilities > P4 Model Default
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
