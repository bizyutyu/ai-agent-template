---
name: review-pr-deep
description: PR差分を4観点（品質・セキュリティ・パフォーマンス・テスタビリティ）で並列レビューし統合レポートを生成する
allowed-tools:
  - Bash(jq *)
  - Bash(gh pr *)
  - Bash(gh search *)
  - Bash(gh api *)
  - Bash(git worktree *)
  - Bash(git diff *)
  - Bash(git fetch *)
  - Agent
---

# Task

自分宛のレビュー依頼PRに未対応のものがあるとき、このスキルで4観点並列レビューを実行する。

## 不変条件

- コメント投稿は必ず人間が内容を確認してから手動で行う（全自動投稿はしない）
- worktreeは処理完了後に必ず削除する

---

## Step 1: 対象PRを確認

```bash
gh search prs --review-requested=@me --state=open \
  --json number,title,url,repository --limit 100 \
  --jq '.[] | "\(.repository.nameWithOwner) #\(.number) \(.title)\n  \(.url)"'
```

上記で対象PR（repo・number・branch）を特定する。

## Step 2: ブランチ名を取得

```bash
gh pr view <number> --repo <repo> --json headRefName,title -q '"\(.headRefName) \(.title)"'
```

## Step 3: worktreeを展開

```bash
git -C ~/$(echo <repo> | cut -d/ -f2) fetch origin
git -C ~/$(echo <repo> | cut -d/ -f2) worktree add ~/worktrees/<repo-basename>-pr<number> <branch>
```

## Step 4: PR差分を取得

```bash
git -C ~/worktrees/<repo-basename>-pr<number> diff origin/main...HEAD
```

diffが空の場合はworktreeを削除してスキップする。

## Step 5: 4エージェントを並列起動

以下の4つの `Agent` ツール呼び出しを**同一メッセージで並列実行**する。
各エージェントに共通で渡す情報:
- PR番号・タイトル・リポジトリ
- Step 4で取得したdiff全文

**model は指定しない（セッションのデフォルトモデルを使用）**

### エージェントA: コード品質

```
以下のPR差分を**コード品質の観点のみ**でレビューしてください。
他の観点（セキュリティ・パフォーマンス・テスタビリティ）は無視してください。

観点: 可読性・命名規則・DRY原則・関数/クラスの責務分離・マジックナンバー

PR: <repo> #<number> "<title>"

---差分---
<diff>

返却フォーマット:
## コード品質
### 高
- `file:line` - 問題の説明と改善案
### 中
- ...
### 低
- ...
### 良い点
- ...
指摘なしの場合は「指摘なし」と記載。
```

### エージェントB: セキュリティ

```
以下のPR差分を**セキュリティの観点のみ**でレビューしてください。
他の観点（品質・パフォーマンス・テスタビリティ）は無視してください。

観点: 入力バリデーション・機密情報の露出・SQLインジェクション・XSS・認証/認可の欠陥

PR: <repo> #<number> "<title>"

---差分---
<diff>

返却フォーマット:
## セキュリティ
### 高
- `file:line` - 脆弱性の説明とリスク
### 中
- ...
### 低
- ...
指摘なしの場合は「指摘なし」と記載。
```

### エージェントC: パフォーマンス

```
以下のPR差分を**パフォーマンスの観点のみ**でレビューしてください。
他の観点（品質・セキュリティ・テスタビリティ）は無視してください。

観点: 計算量(O記法)・不要なループ・N+1クエリ・メモリリーク・不要な再レンダリング

PR: <repo> #<number> "<title>"

---差分---
<diff>

返却フォーマット:
## パフォーマンス
### 高
- `file:line` - 問題の説明と改善案
### 中
- ...
### 低
- ...
指摘なしの場合は「指摘なし」と記載。
```

### エージェントD: テスタビリティ

```
以下のPR差分を**テスタビリティの観点のみ**でレビューしてください。
他の観点（品質・セキュリティ・パフォーマンス）は無視してください。

観点: テスト欠落・エッジケース未考慮・DIの欠如・モック困難な依存・副作用の隠蔽

PR: <repo> #<number> "<title>"

---差分---
<diff>

返却フォーマット:
## テスタビリティ
### 高
- `file:line` - 問題の説明と改善案
### 中
- ...
### 低
- ...
指摘なしの場合は「指摘なし」と記載。
```

## Step 6: 結果を統合してレポートを出力

4エージェントの結果を受け取り、以下のフォーマットで統合レポートを表示する。

```markdown
# PR #<n> Deep Review: <title>

> レビュー対象: <repo> | ブランチ: <branch>

## 🔴 コード品質
<エージェントAの結果>

## 🔐 セキュリティ
<エージェントBの結果>

## ⚡ パフォーマンス
<エージェントCの結果>

## 🧪 テスタビリティ
<エージェントDの結果>

## 総評
（4エージェントの結果を踏まえた全体サマリー2〜3行）

---
⚠️ コメント投稿は内容を確認してから手動で行うこと
```

## Step 7: worktreeを削除

```bash
git -C ~/$(echo <repo> | cut -d/ -f2) worktree remove ~/worktrees/<repo-basename>-pr<number>
```
