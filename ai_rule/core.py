"""ai-rule 核心层：直接 re-export ai_rule.sync_rules 的关键 API。

sync_rules.py 的实际实现就在本包内（ai_rule/sync_rules.py），
所以本模块只是把它的 API 暴露成一个稳定的入口，便于 `from ai_rule import build_ruleset`。
"""
from .sync_rules import (  # noqa: F401
    REPO_ROOT, MANIFEST_DIR, CORE_DIR, ADAPTERS_DIR,
    TOOL_OUTPUT, TOOL_CHAR_LIMIT, PROFILE_INLINE_BASENAMES, SKELETON_BUDGET_BYTES,
    parse_manifest, parse_includes, parse_list_field,
    read_file, expand_refs,
    extract_metadata, derive_keywords, _collect_mcp_files,
    build_ruleset, _build_on_demand_index,
    write_tool_file, _shard_root, _shard_listing, _build_sharded_entry,
    _write_sharded, write_provenance,
    list_profiles, main,
)
