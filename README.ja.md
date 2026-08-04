# AgentSeed — たった1コマンドで、Agentに脳を。

> **`pip install agentseed && agentseed forge`** → まっさらな Agent に、人格・ルール・スキル・ツール設定を即座に注入。

**🌐 言語:** [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md)

![License](https://img.shields.io/badge/license-MIT-blue)
![Personas](https://img.shields.io/badge/personas-6-green)
![Platforms](https://img.shields.io/badge/platforms-13-orange)
![Tests](https://img.shields.io/badge/tests-144%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-informational)

AgentSeed は、AI Agent のための **Persona-Governance プラットフォーム** です。空白の AI コーディングアシスタント（Claude Code、Cursor、Copilot、Trae、Gemini、Windsurf など）に注入するだけで、次の3つを手に入れられます：

- 🧬 **永続的な脳（ガバナンスエンジン）** — 安全境界・意思決定フォーミュラ・自己進化トリガー
- 🎭 **差し替え可能な人格（Persona Packs）** — coding・novel・paper・conversation・interactive-novel・agent-builder
- 🚀 **ゼロコンフィグ同期** — 13 プラットフォーム、1コマンド

---

## 仕組み

```
┌──────────────────────────────────────────────┐
│                 AgentSeed                      │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  ⚡ ガバナンスエンジン（差し替え不可）    │ │
│  │  P0 安全レッドライン・決定式・自己進化   │ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🎭 ペルソナパック（差し替え可能）        │ │
│  │  coding · novel · paper · agent-builder   │ │
│  │  conversation · interactive-novel · カスタム│ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🚀 13 プラットフォーム同期               │ │
│  │  Claude Code · Cursor · Copilot · Trae   │ │
│  │  Gemini · Windsurf · Cline · Continue    │ │
│  │  Amazon Q · Qodo · Lingma · Comate       │ │
│  │  AGENTS.md（汎用）                        │ │
│  └─────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## クイックスタート

```bash
# インストール
pip install agentseed

# 自動検出 → アセンブル → 生成
agentseed forge

# 対話モード：ペルソナを選択
agentseed forge --interactive

# ペルソナを指定
agentseed forge --profile coding

# プレビュー（ファイル書き込みなし）
agentseed forge --dry-run

# ペルソナを切り替え
agentseed switch --profile novel

# 利用可能なペルソナ一覧
agentseed list

# 特定プラットフォームへ同期
agentseed sync --platform cursor
```

AgentSeed がプロジェクトの種類を自動検出し（pyproject.toml → coding、chapters/ → novel など）、最適な Persona Pack を選んで必要なルールファイルをすべて生成します。

---

## なぜ AgentSeed なのか？

| 課題 | AgentSeed の解決策 |
|---------|-------------------|
| AI Agent に一貫した行動ルールがない | **P0 ガバナンス** — どこでも同じ安全基準 |
| タスクごとに違う人格が必要 | **Persona Packs** — 安全を失わずに人格を交換 |
| 複数ツールのルール設定が面倒 | **13プラットフォーム同期** — 1コマンドで全部 |
| プリセットツールが失敗すると止まる | **自己進化エンジン** — ギャップ検出と自己修復 |
| カスタムペルソナの作成・共有が難しい | **ペルソナマーケット** — 一度作ればコミュニティで共有 |

### 競合との比較

| プロジェクト | 内容 | AgentSeed との違い |
|---------|-------------|---------------------|
| agent-rules (steipete) | Cursor/Claude 用の統一 .mdc ルール | アーカイブ済み；コーディングのみ |
| agent-rules-books | ソフトウェア書籍から抽出したルール | コーディングのみ；ペルソナなし |
| ACP | Agent 設定 + MCP 管理 | ガバナンスなし；自己進化なし |
| agents.md | AGENTS.md フォーマット標準 | フォーマットのみ；中身なし |
| chatgpt_system_prompt | システムプロンプト集 | 収集のみ；ツールチェーンなし |
| **AgentSeed** | **完全な人格 + ガバナンス + 同期プラットフォーム** | **完全な Agent の脳** |

---

## 中身

### 🧬 ガバナンスエンジン（憲法レイヤー）
永続的な脳。どの Persona Pack にも上書きされません。

- `core/governance.md` — P0 レッドライン（安全・真実・境界）
- `core/constraints.yaml` — 機械実行可能なフック
- `core/agent-modes.md` — Task / Project / Autonomous モード
- `core/self-evolution.md` — ★ ギャップ検出 + 自己修復
- `core/dar-spec.md` — ドメイン権威スコアリング（検索品質）
- `core/persona-router.md` — ペルソナルーティングと選択

### 🎭 ペルソナパック（差し替え可能）
各パック = SOUL + ルール + スキル + MCP + プロンプト

| ペルソナ | 対象 | 主な特性 |
|---------|-----|-----------|
| `coding` | ソフトウェアエンジニア | リファクタリング、テスト、CI/CD |
| `novel` | 小説家 | 章、キャラクター、世界観 |
| `paper` | アカデミック研究者 | 文献レビュー、LaTeX、投稿 |
| `conversation` | 汎用アシスタント | Q&A、調査、分析 |
| `interactive-novel` | ゲームライター | 分岐ストーリー、ステートマシン |
| `agent-builder` | Agent デザイナー | Agent の構築・評価・デプロイ |

### 🚀 プラットフォーム同期
**13 プラットフォーム**向けにネイティブなルールファイルを生成：

Claude Code, Cursor, Copilot, Trae, Gemini, Windsurf, Cline, Continue, Amazon Q, Qodo, Lingma, Comate、そして AGENTS.md（汎用）。

---

## アーキテクチャ

完全な設計は [docs/AGENTSEED_ARCHITECTURE.md](docs/AGENTSEED_ARCHITECTURE.md) を参照してください。

主な革新：
- **スケルトンモード**：コアルールをインライン化、スキルはオンデマンド読み込み — プロンプトを軽量に維持
- **自己進化エンジン**：Agent が自身の能力ギャップを検出し自己修復
- **品質ゲート**：自動取得したコンテンツはすべて 安全 → 品質 → 互換性 チェックを通過

---

## インストール

```bash
# pip（全プラットフォーム）
pip install agentseed

# pipx（分離環境、非 Python ユーザーに推奨）
pipx install agentseed

# ソースから
git clone https://github.com/weed33834/agentseed.git
cd agentseed
pip install -e .
```

---

## 開発

```bash
# 新しいペルソナを作成
agentseed persona new my-role

# ルールを検証
agentseed verify

# テスト実行
python -m pytest tests/

# ルール品質チェック
python scripts/validate_rules.py
```

---

## ライセンス

MIT

---

*AgentSeed: 憲法は Agent に「いつ自分でリソースを探すか」を教え、アイデンティティが得意分野を決める。*
