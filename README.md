# AgentSeed — One Command to Give Your Agent a Brain

> **`pip install https://github.com/weed33834/agentseed/releases/download/v2.4.0/agentseed-2.4.0-py3-none-any.whl && agentseed forge`** → A blank agent instantly gains a complete persona, rule system, skills, and tool config.

**🌐 Languages:** [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md)

**📦 Platforms:** [GitHub](https://github.com/weed33834/agentseed) — **Primary** (Releases, pip install, CI/CD) · [Gitee](https://gitee.com/badhope/agentseed) — Backup Mirror · [Gitcode](https://gitcode.com/badhope/agentseed) — Backup Mirror

![License](https://img.shields.io/badge/license-MIT-blue)
![Personas](https://img.shields.io/badge/personas-6-green)
![Platforms](https://img.shields.io/badge/platforms-13-orange)
![Tests](https://img.shields.io/badge/tests-144%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-informational)

AgentSeed is a **Persona-Governance Platform for AI Agents**. It's what you inject into a blank AI coding assistant (Claude Code, Cursor, Copilot, Trae, Gemini, Windsurf, and more) to give it:

- 🧬 **A Permanent Brain (Governance Engine)** — safety boundaries, decision formulas, self-evolution triggers
- 🎭 **A Swappable Personality (Persona Packs)** — coding, writing, research, game design, and custom
- 🚀 **Zero-Config Platform Sync** — 13 platforms, one command

---

## How It Works

```
┌──────────────────────────────────────────────┐
│                 AgentSeed                      │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  ⚡ GOVERNANCE ENGINE (non-swappable)  │ │
│  │  P0 red lines · decision formulas ·    │ │
│  │  self-evolution triggers               │ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🎭 PERSONA PACKS (swappable)            │ │
│  │  coding · novel · paper · agent-builder   │ │
│  │  conversation · interactive-novel · custom│ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🚀 13 PLATFORMS SYNC                    │ │
│  │  Claude Code · Cursor · Copilot · Trae   │ │
│  │  Gemini · Windsurf · Cline · Continue    │ │
│  │  Amazon Q · Qodo · Lingma · Comate       │ │
│  │  AGENTS.md (universal)                   │ │
│  └─────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Install
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.0/agentseed-2.4.0-py3-none-any.whl

# Auto-detect → assemble → generate
agentseed forge

# Interactive mode: choose your persona
agentseed forge --interactive

# Specify a persona
agentseed forge --profile coding

# Preview without writing
agentseed forge --dry-run

# Switch persona
agentseed switch --profile novel

# List all available personas
agentseed list

# Sync to a specific platform
agentseed sync --platform cursor

# Start MCP Server (stdio mode)
agentseed serve

# Start MCP Server (HTTP/SSE mode)
agentseed serve --port 8080
```

AgentSeed will detect your project type (pyproject.toml → coding, chapters/ → novel, etc.), select the best Persona Pack, and generate all necessary rule files.

### MCP Server

AgentSeed exposes its governance engine and persona management as MCP tools, enabling any MCP-compatible client to query and enforce AI safety rules programmatically:

| Tool | Description |
|------|-------------|
| `governance_check` | Check if a tool call violates P0 security red lines |
| `persona_list` | List all available persona packs |
| `persona_activate` | Switch to a specific persona |
| `gap_detect` | Analyze context for capability gaps |

Configure your MCP client with:

```json
{
  "mcpServers": {
    "agentseed": {
      "command": "agentseed",
      "args": ["serve"]
    }
  }
}
```

---

## Why AgentSeed?

| Problem | AgentSeed Solution |
|---------|-------------------|
| AI agents lack consistent behavior rules | **P0 Governance** — same safety baseline everywhere |
| Different tasks need different personalities | **Persona Packs** — swap identities without losing safety |
| Setting up rules for multiple tools is tedious | **13-platform sync** — one command, all covered |
| Agents get stuck when their preset tools fail | **Self-Evolution Engine** — auto-detect gaps, search/fetch/install |
| Custom personas are hard to create and share | **Persona Market** — create once, share with community |

### vs Competitors

| Project | What It Does | AgentSeed Difference |
|---------|-------------|---------------------|
| agent-rules (steipete) | Unified .mdc rules for Cursor/Claude | Archived; coding-only |
| agent-rules-books | Rules distilled from software books | Coding-only; no personas |
| ACP | Agent config + MCP management | No governance; no self-evolution |
| agents.md | AGENTS.md format standard | Format only; no content |
| chatgpt_system_prompt | System prompt collection | Collection only; no toolchain |
| **AgentSeed** | **Full persona + governance + sync platform** | **Complete agent brain** |

---

## What's Inside

### 🧬 Governance Engine (Constitution Layer)
The permanent brain. Never overridden by any Persona Pack.

- `core/governance.md` — P0 red lines (security, truth, boundaries)
- `core/constraints.yaml` — Machine-enforceable hooks
- `core/agent-modes.md` — Task / Project / Autonomous modes
- `core/self-evolution.md` — ★ Gap detection + self-healing
- `core/dar-spec.md` — Domain authority scoring (search quality)
- `core/persona-router.md` — Persona routing & selection

### 🎭 Persona Packs (Swappable)
Each Pack = SOUL + Rules + Skills + MCP + Prompts

| Persona | For | Key Traits |
|---------|-----|-----------|
| `coding` | Software Engineers | Refactoring, testing, CI/CD |
| `novel` | Novelists | Chapters, characters, worldbuilding |
| `paper` | Academics | Literature review, LaTeX, submission |
| `conversation` | General Assistants | Q&A, research, analysis |
| `interactive-novel` | Game Writers | Branching narrative, state machine |
| `agent-builder` | Agent Designers | Build, evaluate, deploy agents |

### 🚀 Platform Sync
Generates platform-native rule files for **13 platforms**:

Claude Code, Cursor, Copilot, Trae, Gemini, Windsurf, Cline, Continue, Amazon Q, Qodo, Lingma, Comate, and AGENTS.md (universal).

---

## Architecture

See [docs/AGENTSEED_ARCHITECTURE.md](docs/AGENTSEED_ARCHITECTURE.md) for the full architecture design.

Key innovations:
- **Skeleton Mode**: Core rules inline, skills on-demand — keeps prompts lean
- **Self-Evolution Engine**: Agents detect their own capability gaps and self-heal
- **Quality Gates**: All auto-fetched content passes safety → quality → compatibility checks

---

## Install

```bash
# pip — install from GitHub Releases (primary)
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.0/agentseed-2.4.0-py3-none-any.whl

# From source
git clone https://github.com/weed33834/agentseed.git     # GitHub (primary)
git clone https://gitee.com/badhope/agentseed.git        # Gitee (mirror)
git clone https://gitcode.com/badhope/agentseed.git      # Gitcode (mirror)
cd agentseed
pip install -e .
```

---

## Develop

```bash
# Create a new persona
agentseed persona new my-role

# Validate rules
agentseed verify

# Run tests
python -m pytest tests/

# Check rule quality
python scripts/validate_rules.py
```

---

## License

MIT

---

*AgentSeed: The constitution teaches an agent when to find its own resources; identity decides what it excels at.*
