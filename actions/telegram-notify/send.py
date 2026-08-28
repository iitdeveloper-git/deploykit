#!/usr/bin/env python3
"""
Telegram Deployment & CI Notification Dispatcher
Sends standardized, rich HTML notifications with automatic plain-text fallback.
Zero external dependencies (pure Python standard library).
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any


def parse_context(env: dict[str, str] | None = None) -> dict[str, str]:
    """Extract and sanitize runtime context from environment variables."""
    if env is None:
        env = dict(os.environ)

    repo = env.get("GH_REPO", "")
    server_url = env.get("GH_SERVER_URL", "https://github.com").rstrip("/")
    app = env.get("INPUT_APP", "").strip() or repo or "CI/CD Pipeline"

    return {
        "status": env.get("INPUT_STATUS", "success").strip().lower(),
        "app": app,
        "env_name": env.get("INPUT_ENV", "Production").strip(),
        "tag": env.get("INPUT_TAG", "").strip(),
        "app_url": env.get("INPUT_URL", "").strip(),
        "custom_raw": env.get("INPUT_CUSTOM", "").strip(),
        "thread_id": env.get("INPUT_THREAD_ID", "").strip(),
        "bot_token": env.get("INPUT_BOT_TOKEN", "").strip(),
        "chat_id": env.get("INPUT_CHAT_ID", "").strip(),
        "actor": env.get("GH_ACTOR", "").strip(),
        "server_url": server_url,
        "repo": repo,
        "sha": env.get("GH_SHA", "").strip(),
        "run_id": env.get("GH_RUN_ID", "").strip(),
    }


def get_status_metadata(status: str, env_name: str) -> tuple[str, str, str]:
    """Determine header emoji, status label, and environment indicator emoji."""
    is_ci = any(k in env_name.lower() for k in ["ci", "test", "build", "lint", "check"])

    if status == "success":
        header_emoji = "🚀"
        env_emoji = "🟢"
        status_label = "CI Pipeline Passed" if is_ci else "Deployment Succeeded"
    elif status in ["cancelled", "canceled"]:
        header_emoji = "⚪️"
        env_emoji = "⚪️"
        status_label = "Run Cancelled"
    elif status == "timed_out":
        header_emoji = "⏳"
        env_emoji = "🟡"
        status_label = "Job Timed Out"
    else:
        header_emoji = "❌"
        env_emoji = "🔴"
        status_label = "CI / Test Suite Failed" if is_ci else "Deployment Failed"

    return header_emoji, status_label, env_emoji


def build_messages(ctx: dict[str, str]) -> tuple[str, str]:
    """Generate both formatted HTML and plain text notification payloads."""
    header_emoji, status_label, env_emoji = get_status_metadata(
        ctx["status"], ctx["env_name"]
    )

    commit_url = ""
    short_sha = ctx["sha"]
    if ctx["repo"] and ctx["sha"]:
        commit_url = f"{ctx['server_url']}/{ctx['repo']}/commit/{ctx['sha']}"
        short_sha = ctx["sha"][:7] if len(ctx["sha"]) >= 7 else ctx["sha"]

    run_url = ""
    if ctx["repo"] and ctx["run_id"]:
        run_url = f"{ctx['server_url']}/{ctx['repo']}/actions/runs/{ctx['run_id']}"

    # Build HTML Message
    app_esc = html.escape(ctx["app"])
    env_esc = html.escape(ctx["env_name"])
    status_label_esc = html.escape(status_label)
    actor_esc = html.escape(ctx["actor"])
    tag_esc = html.escape(ctx["tag"])

    html_lines = [
        f"<b>{header_emoji} {app_esc} — {status_label_esc}</b>",
        "",
        f"🏷 <b>Environment:</b> {env_emoji} {env_esc}",
    ]
    if tag_esc:
        html_lines.append(f"📦 <b>Release:</b> <code>{tag_esc}</code>")
    if actor_esc:
        html_lines.append(f"👤 <b>Triggered By:</b> {actor_esc}")
    if commit_url:
        html_lines.append(f'🔗 <b>Commit:</b> <a href="{commit_url}">{short_sha}</a>')
    if ctx["app_url"]:
        esc_url = html.escape(ctx["app_url"])
        html_lines.append(f'🌐 <b>Live URL:</b> <a href="{esc_url}">{esc_url}</a>')

    if ctx["custom_raw"]:
        escaped_custom = html.escape(ctx["custom_raw"])
        escaped_custom = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped_custom)
        escaped_custom = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped_custom)
        html_lines.extend(["", "📝 <b>Release Notes:</b>", escaped_custom])

    if run_url:
        html_lines.extend(["", f'📊 <a href="{run_url}">View GitHub Actions Run</a>'])

    html_text = "\n".join(html_lines)

    # Build Plain Text Fallback Message
    plain_lines = [
        f"{header_emoji} {ctx['app']} — {status_label}",
        "",
        f"Environment: {ctx['env_name']}",
    ]
    if ctx["tag"]:
        plain_lines.append(f"Release: {ctx['tag']}")
    if ctx["actor"]:
        plain_lines.append(f"Triggered By: {ctx['actor']}")
    if commit_url:
        plain_lines.append(f"Commit: {commit_url}")
    if ctx["app_url"]:
        plain_lines.append(f"Live URL: {ctx['app_url']}")
    if ctx["custom_raw"]:
        plain_lines.extend(["", "Release Notes:", ctx["custom_raw"]])
    if run_url:
        plain_lines.extend(["", f"Actions Run: {run_url}"])

    plain_text = "\n".join(plain_lines)

    return html_text, plain_text


def send_telegram(
    bot_token: str,
    payload: dict[str, Any],
    timeout: int = 15,
) -> tuple[bool, str]:
    """Execute HTTP POST request to Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("ok", False), json.dumps(data)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return False, f"HTTP {e.code}: {err_body}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, str(e)


def main() -> int:
    ctx = parse_context()

    if not ctx["bot_token"] or not ctx["chat_id"]:
        print("⚠️ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not provided. Skipping notification.")
        return 0

    html_text, plain_text = build_messages(ctx)

    payload: dict[str, Any] = {
        "chat_id": ctx["chat_id"],
        "text": html_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if ctx["thread_id"]:
        try:
            payload["message_thread_id"] = int(ctx["thread_id"])
        except ValueError:
            print(f"⚠️ Invalid message_thread_id: {ctx['thread_id']}. Ignoring.")

    # Attempt 1: Rich HTML message
    ok, result = send_telegram(ctx["bot_token"], payload)
    if ok:
        print("✅ Telegram HTML notification sent successfully.")
        return 0

    print(f"⚠️ Failed sending HTML notification: {result}. Retrying with plain text fallback...")

    # Attempt 2: Plain text fallback
    payload["text"] = plain_text
    payload.pop("parse_mode", None)
    ok, result = send_telegram(ctx["bot_token"], payload)
    if ok:
        print("✅ Telegram plain text notification sent successfully.")
        return 0

    print(f"❌ Telegram notification failed: {result}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
