# ai-agent-template

[Claude Code](https://docs.claude.com/en/docs/claude-code) 向けのAIエージェント設定一式(`CLAUDE.md` / skills / agents / hooks / settings.json)をまとめた、汎用リポジトリテンプレートです。

新しいプロジェクトを始めるとき、このリポジトリをベースにコピーする(またはGitHubの "Use this template" 機能を使う)ことで、
Claude Codeを使った開発をすぐに一貫したルールで始められます。

## 構成

```
.
├── CLAUDE.md                          # プロジェクト共通の指示(規約・ワークフロー・セキュリティ方針)
├── .claude/
│   ├── settings.json                  # 権限(permissions)・フックの登録。チームで共有する設定
│   ├── settings.local.json            # 個人用のローカル設定(gitignore済み。各自が作成する)
│   ├── agents/                        # サブエージェント定義
│   │   ├── code-reviewer.md
│   │   └── test-writer.md
│   ├── skills/                        # スキル(スラッシュコマンド)定義
│   │   └── example-skill/
│   │       └── SKILL.md
│   └── hooks/                         # PreToolUse / PostToolUse などのフックスクリプト
│       ├── pre_tool_safety.py         # 危険なコマンド・機密ファイルアクセスをブロック
│       └── audit_logger.py            # ツール実行を .claude/logs/audit_trail.jsonl に記録
├── .gitignore
└── LICENSE
```

## 各ファイルの役割

### `CLAUDE.md`
プロジェクトの概要・開発規約・コミット規約・セキュリティ注意事項をClaudeに伝えるファイルです。
`[ ]` で囲まれたプレースホルダー部分を実際のプロジェクトに合わせて書き換えてください。

### `.claude/settings.json`
チームで共有する設定です。以下を定義しています。
- `permissions.allow` / `permissions.deny`: 確認なしで実行してよいコマンド、常に拒否するコマンド
- `hooks`: `pre_tool_safety.py`(危険操作のブロック)と `audit_logger.py`(実行ログ記録)の登録

個人の好み(モデル選択やローカルのみのpermission追加など)は `.claude/settings.local.json` に書き、
このリポジトリでは追跡しません(`.gitignore` 済み)。

### `.claude/agents/`
特定タスクに特化したサブエージェントの定義です。`name` / `description` / `tools` をフロントマターで指定します。
サンプルとして `code-reviewer`(コードレビュー用)と `test-writer`(テスト作成用)を同梱しています。

### `.claude/skills/`
`/スキル名` で呼び出せるスキルの定義です。`example-skill` はコミットメッセージ生成のサンプル実装で、
1スキル=1機能・副作用の最小化というスキル設計原則を示すための参照実装も兼ねています。
新しいスキルを追加する場合は `example-skill/` をコピーして `SKILL.md` を書き換えてください。

### `.claude/hooks/`
Claude Codeのツール実行前後にstdin経由でJSONを受け取り、許可/ブロックやログ記録を行うスクリプトです。
- `pre_tool_safety.py`: `rm -rf /`、force push、`.env`アクセスなど危険なBashコマンドをブロック(exit code 2)
- `audit_logger.py`: すべてのツール実行を `.claude/logs/audit_trail.jsonl` に追記(このディレクトリはgitignore対象)

## 使い方(クイックスタート)

1. このテンプレートをコピーする(GitHubの "Use this template" ボタン、または `git clone` 後にリモートを付け替える)
2. `CLAUDE.md` のプレースホルダーをプロジェクトの実情に合わせて埋める
3. `.claude/settings.json` の `permissions.allow` を、プロジェクトでよく使うコマンドに合わせて調整する
4. 必要な `agents` / `skills` を追加・削除する(不要なサンプルは削除して構わない)
5. `.claude/hooks/*.py` に実行権限を付与する(`chmod +x .claude/hooks/*.py`)。任意でプロジェクト固有のフックを追加する

## ライセンス

[MIT License](./LICENSE)
