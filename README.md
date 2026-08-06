# AgentSeed

> **`pip install https://github.com/weed33834/agentseed/releases/download/v2.4.1/agentseed-2.4.1-py3-none-any.whl && agentseed forge`**

**🌐 [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md)**

**📦 [GitHub](https://github.com/weed33834/agentseed) (primary) · [Gitee](https://gitee.com/badhope/agentseed) · [Gitcode](https://gitcode.com/badhope/agentseed)**

![License](https://img.shields.io/badge/license-MIT-blue)
![Personas](https://img.shields.io/badge/personas-6-green)
![Platforms](https://img.shields.io/badge/platforms-14-orange)
![Tests](https://img.shields.io/badge/tests-143%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-informational)

---

You know the drill. Every time you open a new AI coding session, you spend the first 10 minutes reminding it not to hallucinate, not to run `rm -rf`, and what stack you're using. AgentSeed writes that once and syncs it everywhere.

One command detects your project, picks the right personality, and generates rule files for all your tools — Claude Code, Cursor, Copilot, Windsurf, Trae, whatever you use.

```bash
agentseed forge
```

That's it. From empty directory to a 1200-line AGENTS.md with safety rules, project-specific skills, and platform configs. Works the same whether you're coding, writing a novel, drafting a paper, or building another agent.

---

## What you get

**A baseline that doesn't get overwritten.** Core safety rules (don't rm -rf, don't hallucinate credentials, don't install things unprompted) ship with AgentSeed and no persona can override them.

**Swappable personalities.** Six built-in: `coding` (your default), `novel`, `paper`, `conversation`, `interactive-novel`, `agent-builder`. Each comes with its own prompts, skills, and tool preferences. Switch mid-project with `agentseed switch --profile novel`.

**All your tools, one sync.** Generates the right format for 14 platforms:
- Claude Code → `CLAUDE.md`
- Cursor → `.cursor/rules/project.mdc`
- Copilot → `.github/copilot-instructions.md`
- Windsurf → `.windsurfrules`
- Gemini → `GEMINI.md`
- Trae → `.trae/rules/project_rules.md`
- Cline → `.clinerules/project.md`
- Continue → `.continue/rules/project.md`
- Amazon Q → `.amazonq/rules/project.md`
- Qodo → `best_practices.md`
- Lingma → `.lingma/rules/project.md`
- Comate → `.comate/rules/project.mdr`
- Codex → `.codex/rules.md`
- AGENTS.md (works with 20+ tools that natively read it)

**Hooks with teeth.** Every platform gets a `pre_tool_use.py` interceptor that blocks dangerous operations before they execute. Fail-open design: if the hook crashes, the tool call goes through.

**MCP Server.** Run `agentseed serve` and any MCP-compatible client gets `governance_check`, `persona_list`, `persona_activate`, and `gap_detect`.

**Self-evolution.** AgentSeed scores capability gaps (missing tools, unknown domains) and suggests what to install. Not magic — just a weighted formula that gets better as you add more skills.

---

## Install

```bash
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.1/agentseed-2.4.1-py3-none-any.whl
```

Or build from source:

```bash
git clone https://github.com/weed33834/agentseed.git
cd agentseed
pip install -e .
```

---

## Usage

```bash
agentseed forge              # detect project → assemble → generate
agentseed forge --dry-run    # preview what would be generated
agentseed forge --profile coding
agentseed forge --profile novel

agentseed switch --profile paper

agentseed sync               # sync to all platforms
agentseed sync --platform cursor

agentseed status             # what's assembled, what's missing

agentseed serve              # start MCP server (stdio)
agentseed serve --port 8080  # start MCP server (HTTP)

agentseed platform list      # 14 built-in platforms
agentseed platform import my-ide --entry .myide/rules.md --format markdown

agentseed persona list       # available personas
agentseed persona search "product manager"
```

---

## Add your own platform

```bash
agentseed platform import my-editor --entry .myeditor/rules.md --format markdown --hook-dir .myeditor
```

This registers the platform, generates a pre-tool-use hook, and includes it in every `agentseed sync`.

---

## Project structure

```
core/                  safety baseline (P0 red lines, decision formulas, router)
personas/              one directory per personality (coding, novel, paper, …)
capabilities/          modular skill packs (testing, research, creative, …)
adapters/hooks/        per-platform pre-tool-use interceptors
src/agentseed/         CLI, sync engine, router, forge, evolution
```

---

## vs. similar projects

- **agent-rules (steipete)** — archived, coding-only Cursor rules.
- **agents.md** — file format proposal; no content, no toolchain.
- **ACP** — agent config manager; no governance or self-evolution.
- **Cursor Directory / cursor.directory** — community rule snippets; no multi-platform sync.
- **AgentSeed** — safety rules + personas + 14-platform sync + hooks + self-evolution, all from one CLI.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: edit source files in `core/`, `personas/`, or `capabilities/`; run `agentseed sync` to regenerate platform files; don't hand-edit generated files.

Tests: `python -m pytest tests/` (143 passing).

---

MIT
