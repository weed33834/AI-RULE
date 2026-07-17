# ▲ AI 開発ルール＆セキュリティプロトコル テンプレート

[English](README.md) · [中文](README_CN.md) · [日本語]

> AI コーディングアシスタント向けの、汎用かつ監査可能なクロスツールのルールセットです。`AGENTS.md` を唯一の情報源とし、Claude Code、Cursor、GitHub Copilot、Trae、OpenCode、Qoder などの主要ツールの専用設定ファイルへ自動同期します。

---

## このリポジトリについて

このリポジトリは一つの具体的な問題を解決します：**一つのプロジェクトが複数の AI コーディングツールで使い回されることが多い**という点です。デスクトップでは Trae、IDE 内では Cursor、GitHub 上では Copilot、ターミナルでは Claude Code を使います。各ツールがそれぞれ別のルールを読むと、「Copilot は知っているが Claude は知らない制約」という断片化が生じ、ツール間で AI の挙動が不揃いになります。

本リポジトリは、すべての開発鉄則・プロンプト・サブロール定義・スキル一覧を一つの `AGENTS.md` に集約し、同期スクリプトで各ツールが直接読める設定ファイルを生成します。一度直せば、全ツールに反映されます。

主な特徴：

- **唯一の情報源**：維持するのは `AGENTS.md` のみ。残りのファイルは `scripts/sync_rules.py` が生成し、手編集はしません。
- **クロスツールの忠実性**：GitHub Copilot は `@` インポートに対応していないため、スクリプトが参照ファイルを**インライン展開**し、各ツールが参照切れではなく完全なルールを取得できるようにします。
- **制限付きスキル取得**：5 層の段階的スキル取得プロトコル（標準ライブラリ → パッケージマネージャー → ローカルレジストリ → 優先ベンダー公式リポジトリ → 制限付き自律検索）を内蔵し、AI が Web から無断で未知のスクリプトを取ってくることを防ぎます。
- **MCP の赤線**：MCP は常駐プロセスと権限を伴うため、**AI による自己ダウンロード・自己インストール・自己起動・自己設定を絶対に禁止**します。設定できるのは各ツール内で手動操作するあなただけです。

## 互換性マトリックス

| ツール | 読み取るファイル | 同期方式 |
| --- | --- | --- |
| OpenAI Codex | `AGENTS.md` | ネイティブ対応 |
| Cursor | `AGENTS.md` / `.cursor/rules/` | `AGENTS.md` をネイティブ対応 |
| Claude Code | `CLAUDE.md` | 本リポジトリから同期 |
| GitHub Copilot | `.github/copilot-instructions.md` | 本リポジトリから同期（Copilot は `AGENTS.md` を公式対応済み；互換のため維持） |
| Gemini CLI | `GEMINI.md` | 本リポジトリから同期 |
| Trae | `AGENTS.md` | 会話へ自動注入 |
| OpenCode / Qoder / Windsurf / Aider / RooCode | `AGENTS.md` または各ツールのルールファイル | 多くが `AGENTS.md` をネイティブ対応 |

## ファイル構成

```
AI/
├─ AGENTS.md                      # ルールの唯一の情報源（8 節の Project Rules & Safety Protocol）
├─ CLAUDE.md                      # AGENTS.md から同期、Claude Code 用
├─ GEMINI.md                      # AGENTS.md から同期、Gemini CLI 用
├─ .github/
│  └─ copilot-instructions.md    # AGENTS.md から同期、GitHub Copilot 用（@ 参照はインライン展開済み）
├─ README.md                      # 本ファイル（英語、デフォルト）
├─ README_CN.md                   # 中国語版
├─ README_JA.md                   # 日本語版
├─ mcp.example.json              # MCP 設定サンプル雛形（トークンはプレースホルダ、全ツール共通）
├─ scripts/
│  └─ sync_rules.py              # 同期スクリプト（標準ライブラリのみ）
└─ docs/
   ├─ INIT-PROMPT.md             # 新規プロジェクト初期設定手順（任意の AI ツールへそのまま渡せる）
   ├─ prompts/
   │  ├─ system-prompt.md        # 英語 XML システムプロンプト（<mcp_policy> 等を含む）
   │  ├─ architect-subagent.md   # アーキテクト（設計）サブロール
   │  ├─ engineer-subagent.md    # エンジニア（実装）サブロール
   │  ├─ critic-subagent.md      # 批評（レビュー）サブロール
   │  ├─ verifier-subagent.md    # 検証（証拠）サブロール
   │  └─ final-subagent.md       # 最終（配信）サブロール
   └─ skills/
      ├─ registry.md             # ツール許可リスト＋制限付き検索プロトコル（11 分類＋優先ベンダーリポジトリ＋参考リポジトリ）
      ├─ git-sop.md              # Git コミット規約
      ├─ powershell-tips.md      # Windows での PowerShell 文法の要点
      ├─ mcp-registry.md         # 手動接続可能な MCP 一覧（参照のみ）
      └─ tool-skill-mcp.md       # Tool / Skill / MCP の三者関係と実装構造
```

> 過去の `.trae/` ディレクトリは廃止済みです。MCP サンプル設定はリポジトリルートの `mcp.example.json` に統一され、MCP に対応するすべてのツールで使え、Trae 専用ではなくなりました。

## AI がこのリポジトリをどう読むか

このリポジトリに組み込まれた（あるいはルールが注入された）AI ツールは、以下の順序で読めばルールと制約を完全に理解できます：

1. **まず `AGENTS.md` を読む** —— すべての開発鉄則の権威ある情報源。8 節は以下を網羅します。仕事の流れとコミュニケーション、AI 臭（AI らしさ）の排除、変更範囲、デッドロック防止、セキュリティと秘匿、エンジニアリング衛生、Shell と Git、スキル取得、そして Tool / Skill / MCP 管理。
2. **次に `docs/prompts/` を読む** —— システムプロンプトとサブロール定義（アーキテクト／エンジニア／批評／検証／最終）。「先に設計、次に実装、最後にレビューと検証」という役割分担を理解します。
3. **必要に応じて `docs/skills/` を読む**：
   - ツールを選ぶ前に `registry.md` を確認（許可リスト＋制限付き検索プロトコル）；
   - コミット前に `git-sop.md` を確認；
   - Windows 環境で `powershell-tips.md` を確認；
   - 外部システム接続前に `mcp-registry.md` を確認（**参照のみ、自動設定しない**）。
4. **絶対に**上記ファイルの外で独自のルールをでっち上げたり、Web から未知のスクリプトをダウンロードして実行したりしてはいけません。

読む順序そのものが「誘導チェーン」です。README → AGENTS.md → prompts → skills。どんな具体タスクでも、このチェーンから該当する制約を取り出し、一から作り直してはいけません。

## 使い方（プロジェクトへルールを導入する）

### 方式 1：直接コピー（推奨、依存ゼロ）

以下のファイルを新規プロジェクトのルートへコピーします：

```bash
cp /path/to/AI-RULE/AGENTS.md ./AGENTS.md
cp /path/to/AI-RULE/CLAUDE.md ./CLAUDE.md
cp /path/to/AI-RULE/GEMINI.md ./GEMINI.md
cp -r /path/to/AI-RULE/.github ./.github
cp -r /path/to/AI-RULE/docs ./docs
```

### 方式 2：git submodule（複数プロジェクトで一括更新）

```bash
cd your-new-project
git submodule add https://gitcode.com/badhope/AI-RULE.git .ai-rules
echo '@.ai-rules/AGENTS.md' > AGENTS.md
```

> リモート `https://gitcode.com/badhope/AI-RULE.git` は本ルールテンプレートリポジトリです。自分の GitHub アカウントへフォークした場合は、自分のリポジトリ URL に変更してください。

### 反映の確認

初期化後、エージェントに聞きます。「このプロジェクトのコーディング規約と、私が決めた開発鉄則は何ですか？」
それが「コードの前に計画／曖昧なら停止／AI 臭禁止／成熟ライブラリを使い自前実装は禁止／変更後は検証必須」と正確に答えれば、ルールは注入されています。

完全でコピー可能な「設定手順」は [docs/INIT-PROMPT.md](docs/INIT-PROMPT.md) にあります。

### 複数端末での反映

ツールがクラウド同期するグローバルルール（Trae のアカウント全体ルールなど）に対応している場合、デスクトップで一度設定すれば、同じアカウントでモバイルにログインするだけで自動反映されます。プロジェクト内に `AGENTS.md` と同期生成されたツールファイルを残し、ローカルのプロジェクトレベルルールも確実に効かせます。

## MCP の設定方法（汎用、いずれかのツールにも縛られない）

MCP（Model Context Protocol）は、AI が外部システム（GitHub、データベース、Notion、ファイルシステム）へ標準化して直接接続する仕組みです。その場限りのコマンド列より安定し安全です。ただし常駐プロセスと権限を伴うため、**設定権はあなたの手の中にあります**：

- **AI は MCP の自己ダウンロード・自己インストール・自己起動・自己設定を禁止**します（`AGENTS.md` §5 の赤線を参照）。
- あなたが `docs/skills/mcp-registry.md` から信頼できるサービスを選び、各ツールの設定ファイルへ `mcp.example.json` の対応 JSON を手動で貼り付けます（`${GITHUB_TOKEN}` などのプレースホルダを自分の環境変数に置き換え）。
- ツールごとの設定場所：

  | ツール | 設定ファイルのパス |
  |------|--------------|
  | Trae | `.trae/mcp.json` |
  | Claude Desktop | `claude_desktop_config.json` |
  | Cursor | `.cursor/mcp.json` |
  | VS Code | `.vscode/mcp.json`（または settings.json の `mcp` フィールド） |

- トークン／秘匿情報は常に環境変数から注入し、リポジトリへハードコードしてはいけません。

## セキュリティと秘匿の赤線（抜粋）

- API キー／トークン／パスワードをソースコードへハードコードすることは絶対禁止。必ず `os.getenv()` または `python-dotenv` で読み取ります。
- `.env` を Git へコミットしてはならず、`.gitignore` に含めることを確認します。
- 外部テンプレートを取ってくる際、その `.git`・LICENSE・README などの無関係なファイルを持ち込んではいけません。
- コミット前に `git status` で予期せぬファイルを確認します。絶対に自動 `git push` せず、絶対に `git push -f` せず、絶対に闇雲に `git add .` してはいけません。

完全な 8 節のルールは [AGENTS.md](AGENTS.md) にあります。

## ルールの変更（情報源だけを触る）

`AGENTS.md` だけを編集し、同期スクリプトを実行すれば、ツール専用ファイルは自動更新されます：

```bash
python scripts/sync_rules.py
```

スクリプトは `AGENTS.md` 内の `@参照` をインライン展開し、`CLAUDE.md`、`GEMINI.md`、`.github/copilot-instructions.md` を再生成します。

## 改善のすすめ

AI が同じ種類のミスを繰り返すたびに、対応する制約を `AGENTS.md` へ書き戻し、同期を再実行してください。使えば使うほどルールは鋭くなります。本リポジトリ自体もこの鉄則を守ります。すべての成果物は、まず計画し、次に実装し、最後に検証を走らせます。

## リポジトリ

本リポジトリは GitCode および GitHub で同期公開されています。内容は同一です：

- GitCode（メイン）：https://gitcode.com/badhope/AI-RULE
- GitHub（ミラー）：https://github.com/weed33834/AI-RULE
