#!/usr/bin/env python3
"""PreToolUse hook: 危険なコマンド/機密ファイルアクセスをブロックする。

Claude Code から stdin 経由で以下の形式のJSONを受け取る:
  {"tool_name": "Bash", "tool_input": {"command": "..."}, ...}

exit code:
  0 -> 許可
  2 -> ブロック(stderrの内容がClaudeへのフィードバックになる)
"""
import json
import re
import sys

DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+/(?:\s|$)", "ルート直下への rm -rf は禁止されています"),
    (r"git\s+push\s+.*--force(?!-with-lease)", "force push は禁止されています。--force-with-lease を検討してください"),
    (r"git\s+reset\s+--hard", "git reset --hard は破壊的操作のため、ユーザーの明示的な許可が必要です"),
    (r"curl[^|]*\|\s*(sudo\s+)?(sh|bash)", "curl の出力を直接シェルにパイプする実行は禁止されています"),
    (r"wget[^|]*\|\s*(sudo\s+)?(sh|bash)", "wget の出力を直接シェルにパイプする実行は禁止されています"),
    (r"chmod\s+-R?\s*777", "777への一括パーミッション変更は禁止されています"),
    (r"\bmkfs\.", "ファイルシステムの初期化コマンドは禁止されています"),
    (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "fork bomb と思われるコマンドを検出しました"),
    (r"\.env(\.[a-zA-Z0-9_-]+)?\b", ".env ファイルへのアクセスは禁止されています"),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            sys.stderr.write(f"[pre-tool-safety] ブロック: {reason}\nコマンド: {command}\n")
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
