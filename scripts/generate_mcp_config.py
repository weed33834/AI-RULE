#!/usr/bin/env python3
"""generate_mcp_config.py - 聚合所有 capability/*.mcp.json 生成标准 MCP server 配置。

用法:
    python scripts/generate_mcp_config.py                    # 输出 JSON 到 stdout
    python scripts/generate_mcp_config.py --output mcp.json  # 写入文件
    python scripts/generate_mcp_config.py --profile coding   # 仅输出 coding profile 启用的能力包

符合 Anthropic MCP (Model Context Protocol) 标准，可被 MCP client 直接加载。
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CAPABILITIES_DIR = REPO_ROOT / "capabilities"

# 域到能力包的映射（从各 profile 的 manifest 推断）
PROFILE_CAPABILITIES: dict[str, list[str]] = {
    "coding": ["engineering", "dar", "testing", "review"],
    "paper": ["research", "dar", "review"],
    "novel": ["creative", "dar", "worldbuilding", "npc-simulation", "state-machine",
              "novel-chapter-deliverable-mode"],
    "interactive-novel": ["creative", "dar", "game-engine", "adaptive-difficulty",
                          "npc-simulation", "state-machine", "worldbuilding"],
    "conversation": ["agent-governance", "dar", "orchestration"],
    "agent-builder": ["engineering", "dar", "testing", "review", "agent-governance",
                      "orchestration"],
}


def load_mcp_json(cap_name: str) -> dict | None:
    p = CAPABILITIES_DIR / f"{cap_name}.mcp.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def generate(profile: str | None = None) -> dict:
    capabilities = PROFILE_CAPABILITIES.get(profile) if profile else [
        p.stem.removesuffix(".mcp") for p in CAPABILITIES_DIR.glob("*.mcp.json")
    ]

    tools: list[dict] = []
    resources: list[str] = []
    loaded: list[str] = []

    for cap in (capabilities or []):
        mcp = load_mcp_json(cap)
        if not mcp:
            continue
        loaded.append(cap)
        for tool in mcp.get("tools", []):
            tool["_capability"] = cap
            tools.append(tool)
        for res in mcp.get("resources", []):
            resources.append(f"{cap}/{res}")

    return {
        "name": "agentseed-capabilities",
        "version": "1.0.0",
        "description": f"AgentSeed 能力包聚合配置" + (f"（profile={profile}）" if profile else ""),
        "profile": profile,
        "capabilities_loaded": loaded,
        "tools": tools,
        "resources": resources,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="生成 MCP server 配置")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径（默认 stdout）")
    parser.add_argument("--profile", "-p", type=str, choices=list(PROFILE_CAPABILITIES.keys()),
                        help="目标 Profile，仅输出其启用的能力包")
    args = parser.parse_args()

    config = generate(args.profile)
    out = json.dumps(config, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"写入 {args.output}（{len(config['tools'])} tools, {len(config['resources'])} resources）")
    else:
        print(out)


if __name__ == "__main__":
    main()
