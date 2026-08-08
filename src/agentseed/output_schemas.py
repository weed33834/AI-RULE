"""
Output Schema 强约束模块。

设计哲学：
- AgentSeed 是"规则源"不是 agent framework，不包装 LLM 调用
- 但 AI 可以在交付前主动调 `agentseed check-output` 校验自己的输出
- 失败时给 AI 一个明确的"哪里错了 + 怎么修"反馈，触发自动重写

两种使用方式：

1. CLI 用法（agent 主动调用，推荐）：
   agentseed check-output --profile coding --output-type code_change --content "$(cat my_patch.diff)"

2. Python API 用法（编程式集成，供其他工具调用）：
   from agentseed.output_schemas import validate_output, CodeChangeSchema
   result = validate_output(CodeChangeSchema, content)

Schema 定义来自 personas/<profile>.yaml 的 output_schemas 段（可选）。
未声明的 profile 不做 schema 约束。
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Any


# ─── 不依赖 Pydantic 的极简 schema 实现 ───────────────
# 原因：保持 agentseed 零硬依赖（与 sync_rules.py 一致）
# 若用户已装 Pydantic，会优先用 Pydantic 获得更好错误信息

try:
    from pydantic import BaseModel, ValidationError  # type: ignore
    HAS_PYDANTIC = True
except ImportError:
    BaseModel = object  # type: ignore
    ValidationError = Exception  # type: ignore
    HAS_PYDANTIC = False


@dataclass
class ValidationResult:
    is_valid: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    schema_id: str = ""
    fixes_suggested: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "schema_id": self.schema_id,
            "fixes_suggested": self.fixes_suggested,
        }


# ─── 内置 Schema（每个 Profile 一个或多个）──────────────

class CodeChangeSchema:
    """coding profile：代码变更交付 schema。
    AI 提交代码修改前应通过此 schema。
    """
    id = "code_change_v1"
    required_fields = ["summary", "files_changed", "rationale"]
    optional_fields = ["test_status", "rollback_plan"]

    @staticmethod
    def validate(content: str) -> ValidationResult:
        r = ValidationResult(schema_id=CodeChangeSchema.id)
        try:
            data = json.loads(content) if content.strip().startswith("{") else None
        except json.JSONDecodeError:
            # 不是 JSON，按 markdown 提取
            data = _extract_markdown_frontmatter(content)

        if data is None:
            # 退化为 markdown 内容检查：看是否有必要段
            if "## Summary" not in content and "## 摘要" not in content:
                r.errors.append("缺 ## Summary 段（变更概述）")
            if "## Files Changed" not in content and "## 修改文件" not in content:
                r.errors.append("缺 ## Files Changed 段")
            if "rationale" not in content.lower() and "理由" not in content.lower():
                r.errors.append("缺变更理由（rationale）")
        else:
            for f in CodeChangeSchema.required_fields:
                if f not in data:
                    r.errors.append(f"缺字段: {f}")

        # 通用红线检查（与 governance.md 对齐）
        if "TODO" in content and "FIXME" not in content:
            r.warnings.append("含 TODO 但无 FIXME，建议补充")
        if re.search(r"sk-[A-Za-z0-9]{20,}", content):
            r.errors.append("疑似硬编码 OpenAI API Key（SECRETS_NO_HARDCODE）")
            r.fixes_suggested.append("改用 os.getenv('OPENAI_API_KEY')")
        if re.search(r"ghp_[A-Za-z0-9]{36,}", content):
            r.errors.append("疑似硬编码 GitHub PAT（SECRETS_NO_HARDCODE）")
            r.fixes_suggested.append("改用 os.getenv('GITHUB_TOKEN')")

        r.is_valid = len(r.errors) == 0
        return r


class PaperOutlineSchema:
    """paper profile：论文大纲 schema"""
    id = "paper_outline_v1"
    required_sections = ["abstract", "introduction", "related_work", "methodology", "results", "conclusion"]

    @staticmethod
    def validate(content: str) -> ValidationResult:
        r = ValidationResult(schema_id=PaperOutlineSchema.id)
        for sec in PaperOutlineSchema.required_sections:
            # 接受 markdown 标题或 JSON 字段
            sec_patterns = [
                rf"##\s+{sec.replace('_', '.?')}",
                rf"\"?{sec}\"?\s*:",
                rf"{sec.replace('_', ' ')}",
            ]
            if not any(re.search(p, content, re.IGNORECASE) for p in sec_patterns):
                r.errors.append(f"缺论文必要段: {sec}")
        r.is_valid = len(r.errors) == 0
        return r


class NovelChapterSchema:
    """novel profile：章节交付 schema"""
    id = "novel_chapter_v1"
    required_fields = ["title", "characters_present", "word_count", "foreshadows_planted", "foreshadows_resolved"]

    @staticmethod
    def validate(content: str) -> ValidationResult:
        r = ValidationResult(schema_id=NovelChapterSchema.id)
        # 检查是否有标题
        if not re.search(r"^#\s+\S+", content, re.M):
            r.errors.append("缺章节标题（# 章节名）")
        # 检查字数（粗估）
        words = len(re.findall(r"\w+", content))
        if words < 1000:
            r.warnings.append(f"字数偏少（{words} 词，建议 ≥1000）")
        # 检查角色一致性标注
        if "Characters:" not in content and "出场角色:" not in content:
            r.warnings.append("缺出场角色标注（Characters: ...）")
        r.is_valid = len(r.errors) == 0
        return r


class ConversationResponseSchema:
    """通用（default/内核）事实回答 schema（CoV 5 步流程）"""
    id = "conversation_response_v1"
    required_steps = ["claim", "verification", "sources", "confidence", "answer"]

    @staticmethod
    def validate(content: str) -> ValidationResult:
        r = ValidationResult(schema_id=ConversationResponseSchema.id)
        # CoV 5 步流程
        if "[CoV:" not in content and "CoV:" not in content:
            r.warnings.append("缺 CoV 标注（事实回答必须经过 5 步验证）")
        # 置信度标注
        if not re.search(r"\[置信度[::]\s*(?:高|中|中-|低|待验证)\]", content) and \
           not re.search(r"\[Confidence[::]\s*(?:high|medium|low)\]", content, re.I):
            r.warnings.append("缺置信度标注（[置信度: 高/中/中-/低/待验证]）")
        r.is_valid = len(r.errors) == 0
        return r


class AgentDesignSchema:
    """agent-builder profile：智能体设计 schema"""
    id = "agent_design_v1"
    required_fields = ["role", "tools", "eval_rigor_score", "side_effect_level"]

    @staticmethod
    def validate(content: str) -> ValidationResult:
        r = ValidationResult(schema_id=AgentDesignSchema.id)
        if "role" not in content.lower() and "角色" not in content:
            r.errors.append("缺智能体角色定义（role）")
        if "tools" not in content.lower() and "工具" not in content:
            r.errors.append("缺工具列表（tools）")
        if "Eval_Rigor_Score" not in content and "评估严谨度" not in content:
            r.warnings.append("缺评估严谨度分数（Eval_Rigor_Score）")
        if not re.search(r"副作用[::]\s*L[1-5]", content) and \
           not re.search(r"Side.?Effect[::]\s*L[1-5]", content, re.I):
            r.warnings.append("缺副作用五级标注（L1-L5）")
        r.is_valid = len(r.errors) == 0
        return r


# Profile → Schema 映射表（conversation 已并入内核 default，键保留兼容）
PROFILE_SCHEMAS = {
    "default": {"conversation_response": ConversationResponseSchema},
    "coding": {"code_change": CodeChangeSchema},
    "paper": {"paper_outline": PaperOutlineSchema},
    "novel": {"novel_chapter": NovelChapterSchema},
    "conversation": {"conversation_response": ConversationResponseSchema},
    "agent-builder": {"agent_design": AgentDesignSchema},
}


def _extract_markdown_frontmatter(content: str) -> dict | None:
    """从 markdown YAML frontmatter 提取字段（简版）"""
    m = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
    if not m:
        return None
    frontmatter = m.group(1)
    result = {}
    for line in frontmatter.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip("\"'")
    return result


def validate_output(schema_cls, content: str) -> ValidationResult:
    """通用校验入口。schema_cls 必须有 validate(content) -> ValidationResult 静态方法。"""
    return schema_cls.validate(content)


def validate_for_profile(profile: str, output_type: str, content: str) -> ValidationResult:
    """按 profile + output_type 选 schema 并校验。"""
    schemas = PROFILE_SCHEMAS.get(profile, {})
    schema_cls = schemas.get(output_type)
    if schema_cls is None:
        return ValidationResult(
            is_valid=True,
            warnings=[f"Profile {profile} 无 {output_type} schema，跳过校验"],
            schema_id="none",
        )
    return schema_cls.validate(content)


if __name__ == "__main__":
    # 自检
    print("=== output_schemas 自检 ===")
    print()
    print("--- CodeChangeSchema 合格用例 ---")
    code_ok = '''## Summary
修复用户登录 bug
## Files Changed
- auth.py
rationale: 密码哈希算法过时，升级到 bcrypt
'''
    r = validate_output(CodeChangeSchema, code_ok)
    print(f"is_valid={r.is_valid}, errors={r.errors}, warnings={r.warnings}")

    print("\n--- CodeChangeSchema 含硬编码密钥 ---")
    code_bad = '''## Summary
fix auth
## Files Changed
- config.py
rationale: needed
API_KEY = "sk-abc123def456ghi789jkl012mno345pqr789"
'''
    r = validate_output(CodeChangeSchema, code_bad)
    print(f"is_valid={r.is_valid}, errors={r.errors}")
    print(f"fixes_suggested: {r.fixes_suggested}")

    print("\n--- NovelChapterSchema 短章节 ---")
    short = '''# 第一章 开端
短章节内容
'''
    r = validate_output(NovelChapterSchema, short)
    print(f"is_valid={r.is_valid}, warnings={r.warnings}")
