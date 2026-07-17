# Anti-Patterns: Outdated Prompt Techniques

> These techniques have been empirically shown to be ineffective or counterproductive on next-generation models (Claude 4.x, GPT-4.1, Gemini 2.x). Avoid them in all rule files.

## 1. ALL CAPS Emphasis

**Status**: ❌ Ineffective on Claude 4.5+

ALL CAPS words like "MUST", "ALWAYS", "NEVER" no longer guarantee adherence. Claude 4.5 prioritizes contextual logic over capitalization.

**Instead of**: `You MUST NEVER commit secrets.`
**Use**: `If a file contains API keys or credentials, do not commit it. Use environment variables instead.` (conditional logic)

## 2. Negative-Only Constraints

**Status**: ❌ Counterproductive ("Pink Elephant" effect)

Telling the model "Don't do X" draws attention to X, increasing the likelihood of doing it.

**Instead of**: `Never fabricate API responses.`
**Use**: `All API responses must come from actual tool calls. If the tool is unavailable, state that explicitly.` (positive instruction)

**Instead of**: `Don't use emojis.`
**Use**: `Use plain text formatting only.` (positive instruction)

## 3. Manual "Think Step by Step"

**Status**: ❌ Redundant with Extended Thinking

When Extended Thinking is enabled, the model manages its own reasoning budget. Manual "think step by step" instructions waste tokens and may interfere.

**Instead of**: `Think step by step before answering.`
**Use**: (nothing — let Extended Thinking handle it) or `Use Extended Thinking for complex multi-constraint tasks.`

## 4. Vague Authority Claims

**Status**: ❌ Ineffective

**Instead of**: `You are an expert. Always produce expert-level output.`
**Use**: `You have 10+ years of full-stack development experience. Apply production-grade patterns: error handling, input validation, and edge-case coverage.` (specific credentials + specific expectations)

## 5. Rule Without Rationale

**Status**: ⚠️ Suboptimal

Claude 4.x / GPT-4.1 follow rules better when they understand *why* the rule exists. Rules without rationale generalize poorly to edge cases.

**Instead of**: `Do not auto-push to remote.`
**Use**: `Do not auto-push to remote — unreviewed pushes may break CI or expose secrets. Always wait for explicit user confirmation.`

## Migration Checklist

When auditing existing rule files:
- [ ] Replace ALL CAPS emphasis with conditional logic
- [ ] Rewrite negative-only constraints as positive instructions
- [ ] Remove manual CoT instructions (or gate behind Extended Thinking check)
- [ ] Add rationale to all P0 rules
- [ ] Replace vague authority claims with specific credentials
