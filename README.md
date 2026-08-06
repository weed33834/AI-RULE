# AgentSeed — One Command to Give Your Agent a Brain

> **AgentSeed is an open-source AI agent framework and persona-governance platform.** One command turns a blank AI coding assistant into a fully-configured agent with safety rules, swappable personalities, and 13-platform sync.
>
> **`pip install https://github.com/weed33834/agentseed/releases/download/v2.4.1/agentseed-2.4.1-py3-none-any.whl && agentseed forge`** → A blank agent instantly gains a complete persona, rule system, skills, and tool config.

**🌐 Languages:** [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md)

**📦 Platforms:** [GitHub](https://github.com/weed33834/agentseed) — **Primary** (Releases, pip install, CI/CD) · [Gitee](https://gitee.com/badhope/agentseed) — Backup Mirror · [Gitcode](https://gitcode.com/badhope/agentseed) — Backup Mirror

![License](https://img.shields.io/badge/license-MIT-blue)
![Personas](https://img.shields.io/badge/personas-6-green)
![Platforms](https://img.shields.io/badge/platforms-13-orange)
![Tests](https://img.shields.io/badge/tests-144%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-informational)

AgentSeed is a **Persona-Governance Platform for AI Agents** — an open-source agent framework that injects governance, personality, and tooling into any blank AI assistant. It's what you use to give your Claude Code, Cursor, Copilot, Trae, Gemini, Windsurf, Cline, Continue, Amazon Q, Qodo, Lingma, or Comate a permanent brain:

- 🧬 **Governance Engine (Constitution Layer)** — safety boundaries, decision formulas, self-evolution triggers, prompt engineering guardrails
- 🎭 **Swappable Persona Packs** — coding, writing, research, game design, and custom personalities
- 🚀 **Zero-Config 13-Platform Sync** — one command line tool, all IDEs covered
- 🔍 **Self-Evolution** — auto-detect capability gaps, search, fetch, install
- 🛡️ **MCP (Model Context Protocol) Server** — expose governance as programmatic tools

---

## How It Works

AgentSeed is a **command-line AI agent framework** that solves the blank-agent problem: every time you start a new AI coding assistant, you shouldn't have to re-teach it how to behave. AgentSeed automates this with a three-layer architecture:

```
┌──────────────────────────────────────────────┐
│                 AgentSeed                      │
│         AI Agent Framework & Persona           │
│          Governance Platform                   │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  ⚡ GOVERNANCE ENGINE (non-swappable)  │ │
│  │  P0 red lines · decision formulas ·    │ │
│  │  self-evolution triggers · rule engine │ │
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
# Install AgentSeed (AI agent framework CLI)
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.1/agentseed-2.4.1-py3-none-any.whl

# Auto-detect → assemble → generate (blank agent → full brain)
agentseed forge

# Interactive mode: choose your persona
agentseed forge --interactive

# Specify a persona for your workflow
agentseed forge --profile coding

# Preview without writing
agentseed forge --dry-run

# Switch persona mid-project
agentseed switch --profile novel

# List all available personas
agentseed list

# Sync AI rules to a specific IDE or platform
agentseed sync --platform cursor

# Start MCP Server (stdio mode) — Model Context Protocol
agentseed serve

# Start MCP Server (HTTP/SSE mode)
agentseed serve --port 8080
```

AgentSeed will detect your project type (`pyproject.toml` → coding, `chapters/` → novel, etc.), select the best Persona Pack, and generate all necessary AI rule files, system prompts, and tool configurations.

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
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.1/agentseed-2.4.1-py3-none-any.whl

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

<!-- SEO Keywords Block — helps search engines and package registries index this project -->
## Keywords

`ai-agent`, `agent-framework`, `persona-governance`, `mcp`, `model-context-protocol`, `ai-rules`, `system-prompt`, `prompt-engineering`, `claude-code`, `cursor`, `copilot`, `trae`, `gemini`, `windsurf`, `cline`, `continue`, `amazon-q`, `ai-personality`, `agent-brain`, `blank-agent`, `coding-assistant`, `developer-tools`, `automation`, `workflow`, `cli`, `python`, `open-source`

<!-- JSON-LD Structured Data for schema.org / Google Rich Snippets -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "AgentSeed",
  "description": "One command to give your AI agent a brain. Persona-Governance Platform with safety rules, swappable personalities, and 13-platform sync.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Cross-platform",
  "programmingLanguage": "Python",
  "softwareVersion": "2.4.1",
  "license": "https://github.com/weed33834/agentseed/blob/main/LICENSE",
  "codeRepository": "https://github.com/weed33834/agentseed",
  "downloadUrl": "https://github.com/weed33834/agentseed/releases",
  "author": {
    "@type": "Organization",
    "name": "AgentSeed Project"
  },
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
</script>
