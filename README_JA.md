# ▲ Rule Hub — 統合AIコラボレーションルール（日本語）

[English](README.md) · [中文](README_CN.md) · [日本語]

![License](https://img.shields.io/badge/license-MIT-blue)
![Profiles](https://img.shields.io/badge/profiles-5-green)
![Files](https://img.shields.io/badge/files-209+-orange)
![Tests](https://img.shields.io/badge/tests-40%20passing-brightgreen)
![Languages](https://img.shields.io/badge/docs-EN%20%2F%20%E4%B8%AD%20%2F%20%E6%97%A5-informational)

> 5つの独立ルール体系を一つのリポジトリに統合：コア層＋単一プロファイル＋機能パック。
> 一度クローンし、プロファイルを選択、各AIツールのルールエントリを生成。

---

## このリポジトリについて

本リポジトリは **AIコラボレーションルールの唯一の正ソース** であり、特定プロジェクトの業務コードではありません。5つの独立ルールリポジトリ（coding / conversation / novel / interactive-novel / agent-builder）を統合し、シーン別に分離ロードすることで、「捏造禁止」と「小説には創作が必要」といった領域制約の衝突を回避します。

| プロファイル | 由来 | 用途 |
|---|---|---|
| `coding` | badhope/AI | ソフトウェア開発、バグ修正、リファクタリング、コードレビュー |
| `conversation` | badhope/universal | 一般Q&A、リサーチ、比較、情報検索 |
| `novel` | badhope/novel | 小説執筆、章作成、キャラクター・世界構築 |
| `interactive-novel` | badhope/interactive-novel | インタラクティブフィクション、分岐叙事、状態機械 |
| `agent-builder` | badhope/AgentCreater | AIエージェントの設計、評価、デプロイ |

## クイックスタート

```bash
git clone https://gitcode.com/badhope/AI-RULE.git
cd AI-RULE

# プロファイル一覧
python scripts/sync_rules.py --list

# coding プロファイルの Claude Code エントリを生成
python scripts/sync_rules.py --profile coding --tool claude-code
```

生成されたエントリファイル（例：`CLAUDE.md`）をプロジェクトルートに配置するか、サブモジュールとして参照してください。

AIにはこう伝えます：

```text
Rule Hub から coding Profile をロードしてください。
```

## プロファイル選択

明示指定（推奨）または自動検出（プロジェクトアンカーによる）。

| アンカー | 判定されるプロファイル |
|---|---|
| `pyproject.toml`, `package.json` + ソースコード | `coding` |
| `.ai-memory/creative-blueprint.md`, `chapters/` | `novel` |
| `.game-state/`, `game-state-machine.md` | `interactive-novel` |
| `config.yaml` + `tools.json` | `agent-builder` |
| 該当なし | `conversation` |

## リポジトリ構造

```
AI-RULE/
├── AGENTS.md                    # ルールハブエントリ（セレクタ＋優先度＋言語仲介）
├── core/                        # 全プロファイル共通のP0ハード制約
│   ├── governance.md            # セキュリティ、権限、MCPレッドライン
│   ├── interaction.md           # 確認、意図正規化、出力仕様
│   ├── profile-router.md        # プロファイル選択と機能パックホワイトリスト
│   └── language-mediation.md    # 言語仲介プロトコル
├── profiles/                    # 5つの独立ルールセット
├── capabilities/                # 13のオンデマンド機能パック
├── manifests/                   # プロファイル別アセンブリマニフェスト
├── scripts/sync_rules.py        # ツールエントリファイル生成
└── tests/                       # 5テストスイート（40チェック、全通過）
```

## 言語メカニズム

ルールファイルは推論精度のため **英語** で記述されたシステムプロンプトと、明確さのため中英バイリンガルで書かれたルール文書で構成されています。AIはユーザーの言語で応答します：

1. 入力：言語を自動検出 → 英語で推論
2. 出力：英語で生成 → ユーザー言語に翻訳 → 翻訳調を除去

詳細は `core/language-mediation.md` を参照。

## 対応AIツール

| ツール | 出力ファイル |
|---|---|
| Claude Code | `CLAUDE.md` |
| Gemini | `GEMINI.md` |
| Cursor | `.cursor/rules/project.mdc` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Trae | `.trae/rules/project_rules.md` |

## 研究主導の最適化

本リポジトリはプロンプトエンジニアリングとAIアライメントの最新研究知見を取り入れています：

- **命令予算 (Instruction Budget)**：同時にアクティブな命令が増えると遵守率がべき乗減衰。P0ルールは同時5件以下、全体で12件以下に制限。
- **位置効果 (Lost in the Middle)**：LLMは文脈の先頭と末尾に注意を向ける。P0ルールはコンテキストウィンドウの両端に配置。
- **アンチパターン**：全大文字、純否定制約、手動CoTは新世代モデルで無効。条件ロジック＋正の代替で記述。
- **拡張思考 (Extended Thinking)**：Claude 4.x / OpenAI o シリーズのネイティブ推論で手動CoTを置き換え。
- **三層行動境界**：許可（自律）/ 要確認 / 禁止 — 曖昧な「適切な行動」宣言を置き換え。
- **GUID区切り文字注入防御**：固定 `[UNTRUSTED]` マーカーの代わりにランダムGUIDでマーカー閉鎖攻撃を防止。
- **棄権プロトコル**：「分からない」と言うことを許可しつつ、虚勢を防止。
- **自己精製**：ReflexionループとConstitutional自己批判による出力前品質チェック。

## ルール優先度

```
P0: core/ セキュリティ、権限、真実性、MCPレッドライン
> P1: ユーザーの現在の明示的確認
> P2: メインプロファイル領域ルール
> P3: 機能パックオンデマンドルール
> P4: モデルデフォルト動作
```

## 検証

```bash
pytest tests/                        # 5スイート、40チェック、全通過
```

## リポジトリ

本リポジトリはGitCodeとGitHubでミラーリングされています：

- GitCode（プライマリ）: https://gitcode.com/badhope/AI-RULE
- GitHub（ミラー）: https://github.com/weed33834/AI-RULE

## ライセンス

MIT
