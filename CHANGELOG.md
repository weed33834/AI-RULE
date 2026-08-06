# Changelog

## [2.4.1] — 2026-08-05

### Added
- MCP Server (`agentseed serve`): four tools (governance_check, persona_list, persona_activate, gap_detect) via stdio or HTTP.
- CLI `platform` subcommands: list, import, remove, validate, export. 14 built-in platforms registered.
- 14-platform hook coverage: every platform now has `pre_tool_use.py` + `hooks.json.template` + `README.md`.
- Cross-platform env layer (`src/agentseed/env.py`): path normalization, encoding, command execution.
- SEO: JSON-LD, codemeta.json, CITATION.cff, GitHub topics, multi-language READMEs.

### Fixed
- codex platform missing from TOOL_OUTPUT (was registered but not synced).
- Version string unified to 2.4.1 across all files (pyproject, init, cli, mcp_server, docs).
- Dead references to deleted files (scripts/sync_rules.py, manifests/, profiles/, ai_rule).

## [2.3.0] — 2026-08-04

### Added
- Persona router (`src/agentseed/router.py`): explicit > anchor > keyword > fallback; mutual exclusion; capability whitelist.
- Persona market (`src/agentseed/market.py`): search, install with Quality Gate.
- CLI: `forge`, `switch`, `persona`, `status`, `sync` commands.
- Forge engine: detect environment → route persona → build ruleset → write platform files.
- Self-evolution engine (`src/agentseed/evolution.py`): GapScore formula, Quality Gate (safety/quality/compatibility).

### Changed
- `docs/AGENTSEED_ARCHITECTURE.md`: structure diagram and mapping table synced to actual repo layout.
- `CONTRIBUTING.md`: updated to v2 workflow.

## [2.0.0] — 2026-08-03

### Changed
- **Rebrand**: AI-RULE → AgentSeed. Package `ai-rule` → `agentseed`, CLI `agentseed`.
- Directory restructure: `ai_rule/` → `src/agentseed/`, `profiles/` → `personas/`, `manifests/` → `personas/<id>/persona.yaml`, capabilities modularized.
- Removed top-level `skills/`, `mcp/`, and `README.ja.md` (re-added in 2.3.0).
- Environment variable: `AI_RULE_REPO` → `AGENTSEED_REPO`.

### Added
- Forge engine, self-evolution engine, persona template (`personas/_template/default/`).

### Fixed
- 107+ legacy brand/path references cleaned to zero.
- `setup.py` syntax fix; all persona/core GBK encoding fixed to UTF-8.

## [1.4.0] — 2026-07-25

- Runtime skills (7 files), MCP tools (4 Python tools), rule injection script, BOOTSTRAP self-check.
- DAR mode overrides configuration.

## [1.3.1] — 2026-07-19

- DAR multi-model evaluation (10 models × 6 scenarios, 120 API calls).

## [1.3.0] — 2026-07-19

- DAR (Domain Authority Registry): T1-T4 source grading, scoring formula, 6 domain configs.
- DAR test framework and evaluation suite.

## [1.2.0] — 2026-07-18

- Paper persona (6th profile), default tool source configs, CITATION.cff.

## [1.1.0] — 2026-07-17

- Instruction Budget, Position Effects, Anti-Patterns, Extended Thinking, Abstention Protocol.
- Self-Refinement, GUID delimiter injection defense, NeMo self-check templates.

## [1.0.0] — 2026-07-16

- Initial release: 5 profiles merged (coding, conversation, novel, interactive-novel, agent-builder).
