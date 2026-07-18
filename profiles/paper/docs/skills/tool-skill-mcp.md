# Tool / Skill / MCP Strategy

> This document defines the relationship between tools, skills, and MCP, and the strategy for using them.
> It is the complete implementation of AGENTS.md §14 Tools & Skills.

## §1 The Three Concepts

| Concept | Metaphor | Description | Control |
|---------|----------|-------------|---------|
| Tool | Hands and feet | Built-in tools, available out of the box | AI can use autonomously |
| Skill | Recipe | Documents under `docs/skills/` that teach how to do complex things | AI reads on demand |
| MCP | Transfusion | Background services connecting to external systems | User configures manually |

## §2 Tool Usage Principles

- Prefer dedicated tools over generic shell commands.
- Read file contents before any file operation.
- Do not create unnecessary files.
- Prefer editing existing files over creating new ones.
- Confirm high-risk operations (deletion, push, database write, manuscript submission) before executing.

## §3 Skill Usage Principles

- For complex tasks, first check whether a matching skill document exists under `docs/skills/`.
- A skill document is a recipe — read on demand, do not preload in full every turn.
- When a skill document conflicts with AGENTS.md, AGENTS.md takes precedence.
- After completing a complex task, consider extracting a new skill document (see `evolution-policy.md` §2).

## §4 MCP Strategy

- MCP services connect to external systems and require environment variables, ports, and permissions.
- The AI must not download, install, or start MCP services on its own.
- MCP configuration is the user's responsibility.
- The AI may output install commands and configuration JSON for the user's reference.
- Approved MCP services are recorded in a configuration file for human reference only.

## §5 Default Tool Sources

The paper profile uses the following default sources. Each source has a specific role; do not substitute one for another without a reason.

| Task | Default Source | Notes |
|------|----------------|-------|
| General web search | Bing | Browser-based retrieval of non-academic context |
| Academic search (broad) | Google Scholar | Cross-disciplinary; citation counts and related work |
| Academic search (semantic) | Semantic Scholar | API-friendly; semantic recommendations; TLDRs |
| Preprints (CS / Physics / Math) | arXiv | Latest preprints; check for peer-reviewed version |
| Biomedical literature | PubMed | MeSH-indexed; authoritative for life sciences |
| Computer Science bibliography | DBLP | Authoritative author and venue indexing |
| Citation management | Zotero | Local + cloud library; group libraries for collaboration |
| DOI lookup | CrossRef | Authoritative DOI metadata; use for verification |
| Retraction check | Retraction Watch | Required before citing any work whose integrity is uncertain |

### 5.1 Source Selection Rules

- For DOI verification, always use CrossRef — never a search engine.
- For preprint citation, prefer the published version when one exists; cite both if the venue requires.
- For retraction status, always check Retraction Watch before final submission of the reference list.
- For biomedical claims, prefer PubMed over generic web search.
- When multiple sources disagree, prefer the source closest to the publisher (CrossRef > publisher site > Google Scholar).

## §6 Deep Search Protocol

All profiles use the deep search protocol by default. The protocol governs how literature is located, verified, and recorded.

```
1. Query formulation
   - Start from the research question; extract 3–6 discriminative terms.
   - Formulate the query per source's syntax (Google Scholar operators, PubMed MeSH, arXiv categories).

2. Source sequencing
   - Broad first (Google Scholar / Semantic Scholar), then specific (arXiv / PubMed / DBLP).
   - For each candidate hit, fetch the abstract and metadata.

3. Verification
   - Resolve the DOI via CrossRef; record the metadata.
   - Check Retraction Watch for any retraction record.
   - Mark the verification status in `.ai-memory/references.bib` (see `context-management.md` §5.2).

4. Sandbox raw outputs
   - Raw search outputs go to `/data/user/work/` temporary files.
   - Only the digest (citation key, DOI, abstract summary, verification status) enters the context window.

5. Citation map update
   - Add the citation to `.ai-memory/references.bib`.
   - Add the citation-claim link to `.ai-memory/citation-map.md`.
```

## §7 Authorization Whitelist

The AI may use the following without per-call confirmation. Anything outside this list requires explicit user approval.

| Allowed Without Confirmation | Confirmation Required |
|------------------------------|-----------------------|
| Read-only literature search via the default sources | Any new MCP service |
| CrossRef DOI lookup | Any external API call that sends data out |
| Retraction Watch query | Submitting a manuscript to a venue |
| Zotero read-only queries | Bulk citation import (may overwrite existing entries) |
| Reading local files under the repo | Writing to files outside the repo |
| Writing to `/data/user/work/` temp files | Deleting any file |
| `pip-audit` and `pip-licenses` | Installing new third-party dependencies |

## §8 Tool Selection Priority

| Need | Priority |
|------|----------|
| File read | Dedicated read tool > shell `cat` |
| File search | Grep / Glob > shell `find` / `grep` |
| File edit | Edit tool > shell `sed` / `awk` |
| File write | Write tool > shell `echo` / `cat` |
| Citation lookup | CrossRef API > web search |
| Bibliography management | Zotero CLI > manual `.bib` edits |
| PDF text extraction | Dedicated extractor > manual copy |
| Reference verification | Retraction Watch API > web search |
| Version control | Terminal `git` |

## §9 Relationship with Other Documents

- All skill documents are part of the "Skill" layer.
- `evolution-policy.md` governs the lifecycle of skills.
- `security-checklist.md` includes the safety checks that apply to every tool use.
- `context-management.md` §7 defines the sandboxing workflow for tool outputs.
- `path-scoped-rules.md` activates tool conventions based on file type.
