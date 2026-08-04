#!/usr/bin/env python3
"""统一规则中枢同步脚本 — 薄 shim。

实际实现已迁移到 `agentseed/sync_rules.py`（让 `pip install agentseed` 也能独立工作）。
本文件保留是为了向后兼容：
- `python scripts/sync_rules.py ...` 仍可用（git clone 用户的使用路径）
- 测试中 `from sync_rules import ...` 仍可用（conftest 把 scripts/ 加到 sys.path）

Shim 通过把仓库根加到 sys.path，让 `import agentseed.sync_rules` 在 dev 模式下能找到 agentseed 包。
"""
import sys
from pathlib import Path

# 把仓库根加到 sys.path，使 agentseed 包可被 import
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# 把 scripts/ 也加到 sys.path，使 `from sync_rules import xxx` 仍能解析到本 shim
# （shim 模块本身会被加载为 sync_rules 名字，因此其属性自然就是 agentseed.sync_rules 的属性）
from agentseed.sync_rules import *  # noqa: F401,F403
from agentseed.sync_rules import (  # noqa: F401  显式 re-export 常用 API
    REPO_ROOT, PERSONAS_DIR, CORE_DIR, ADAPTERS_DIR,
    RESOURCES_ROOT, OUTPUT_ROOT,
    TOOL_OUTPUT, TOOL_CHAR_LIMIT, PROFILE_INLINE_BASENAMES, SKELETON_BUDGET_BYTES,
    PROFILE_LAYER_BUDGET, P0_KEYWORDS,
    HOOK_PLATFORMS,
    parse_manifest, parse_includes, parse_list_field,
    read_file, expand_refs,
    extract_metadata, derive_keywords, _collect_mcp_files,
    _infer_trigger, _truncate_field,
    _extract_section_title, _is_section_start, _split_profile_content,
    build_ruleset, _build_on_demand_index,
    write_tool_file, _shard_root, _shard_listing, _build_sharded_entry,
    _write_sharded, write_provenance,
    verify_ruleset, _verify_constraints_yaml,
    emit_constraints,
    PROFILE_ANCHORS, INTENT_KEYWORDS,
    detect_tool_from_cwd, detect_profile_from_cwd, setup_default,
    list_profiles, main,
    # 资源根检测 / 刷新相关（pip 打包模式 + AGENTSEED_REPO 优先级）
    _packaged_resources_root, _find_rule_hub_root, _resolve_resources_root,
    resources_source, refresh_resources_root,
    set_output_root, reset_output_root,
)


if __name__ == "__main__":
    main()
