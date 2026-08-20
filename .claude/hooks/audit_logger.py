#!/usr/bin/env python3
"""PostToolUse hook: すべてのツール実行を監査ログとしてJSONL形式で記録する。

出力先: .claude/logs/audit_trail.jsonl
このスクリプトはログ出力に失敗してもClaude Codeの動作を妨げないよう、
常にexit code 0を返す。
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "audit_trail.jsonl"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": payload.get("session_id"),
        "hook_event": payload.get("hook_event_name"),
        "tool_name": payload.get("tool_name"),
        "cwd": payload.get("cwd"),
    }

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
