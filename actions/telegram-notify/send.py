import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

status = os.environ.get("INPUT_STATUS", "success").lower()
app = os.environ.get("INPUT_APP", "Growixa")
env_name = os.environ.get("INPUT_ENV", "Production")
tag = os.environ.get("INPUT_TAG", "")
app_url = os.environ.get("INPUT_URL", "")
custom_raw = os.environ.get("INPUT_CUSTOM", "")
thread_id = os.environ.get("INPUT_THREAD_ID", "")
bot_token = os.environ.get("INPUT_BOT_TOKEN", "")
chat_id = os.environ.get("INPUT_CHAT_ID", "")

actor = os.environ.get("GH_ACTOR", "")
server_url = os.environ.get("GH_SERVER_URL", "https://github.com")
repo = os.environ.get("GH_REPO", "")
sha = os.environ.get("GH_SHA", "")
run_id = os.environ.get("GH_RUN_ID", "")

if not bot_token or not chat_id:
    print("⚠️ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not provided. Skipping notification.")
    sys.exit(0)

is_ci = any(k in env_name.lower() for k in ["ci", "test", "build", "lint"])

if status == "success":
    header_emoji = "🚀"
    env_emoji = "🟢"
    status_label = "CI Pipeline Passed" if is_ci else "Deployment Succeeded"
elif status == "cancelled":
    header_emoji = "⚪️"
    env_emoji = "⚪️"
    status_label = "Run Cancelled"
else:
    header_emoji = "❌"
    env_emoji = "🔴"
    status_label = "CI / Test Suite Failed" if is_ci else "Deployment Failed"

app_esc = html.escape(app)
env_esc = html.escape(env_name)
status_label_esc = html.escape(status_label)
actor_esc = html.escape(actor)
tag_esc = html.escape(tag)

commit_url = f"{server_url}/{repo}/commit/{sha}" if repo and sha else ""
run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if repo and run_id else ""

lines = [
    f"<b>{header_emoji} {app_esc} — {status_label_esc}</b>",
    "",
    f"🏷 <b>Environment:</b> {env_emoji} {env_esc}",
]
if tag_esc:
    lines.append(f"📦 <b>Release:</b> <code>{tag_esc}</code>")
if actor_esc:
    lines.append(f"👤 <b>Triggered By:</b> {actor_esc}")
if commit_url:
    short_sha = sha[:7] if len(sha) >= 7 else sha
    lines.append(f'🔗 <b>Commit:</b> <a href="{commit_url}">{short_sha}</a>')
if app_url:
    esc_url = html.escape(app_url)
    lines.append(f'🌐 <b>Live URL:</b> <a href="{esc_url}">{esc_url}</a>')

if custom_raw:
    escaped_custom = html.escape(custom_raw)
    escaped_custom = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped_custom)
    escaped_custom = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped_custom)
    lines.extend(["", "📝 <b>Release Notes:</b>", escaped_custom])

if run_url:
    lines.extend(["", f'📊 <a href="{run_url}">View GitHub Actions Run</a>'])

html_text = "\n".join(lines)

plain_lines = [
    f"{header_emoji} {app} — {status_label}",
    "",
    f"Environment: {env_name}",
]
if tag:
    plain_lines.append(f"Release: {tag}")
if actor:
    plain_lines.append(f"Triggered By: {actor}")
if commit_url:
    plain_lines.append(f"Commit: {commit_url}")
if app_url:
    plain_lines.append(f"Live URL: {app_url}")
if custom_raw:
    plain_lines.extend(["", "Release Notes:", custom_raw])
if run_url:
    plain_lines.extend(["", f"Actions Run: {run_url}"])
plain_text = "\n".join(plain_lines)


def send_telegram(payload: dict) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("ok", False), json.dumps(data)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return False, f"HTTP {e.code}: {err_body}"
    except Exception as e:
        return False, str(e)


# Attempt 1: Rich HTML message
payload = {
    "chat_id": chat_id,
    "text": html_text,
    "parse_mode": "HTML",
    "disable_web_page_preview": True,
}
if thread_id:
    payload["message_thread_id"] = int(thread_id)

ok, result = send_telegram(payload)
if ok:
    print("✅ Telegram HTML notification sent successfully.")
    sys.exit(0)

print(f"⚠️ Failed sending HTML notification: {result}. Retrying with plain text fallback...")

# Attempt 2: Plain text fallback
payload["text"] = plain_text
payload.pop("parse_mode", None)
ok, result = send_telegram(payload)
if ok:
    print("✅ Telegram plain text notification sent successfully.")
    sys.exit(0)

print(f"❌ Telegram notification failed: {result}")
sys.exit(1)
