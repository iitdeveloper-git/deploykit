#!/usr/bin/env python3
"""DeployKit Multi-Channel Notification Dispatcher

Zero-dependency standard library dispatcher supporting:
- Telegram (Bot API with rich HTML and plaintext fallback)
- Slack (Incoming Webhooks with Block Kit & color attachments)
- Microsoft Teams (Incoming Webhooks with MessageCard format)
- Discord (Webhooks with rich embed cards)
- Generic Webhook (Configurable JSON HTTP POST)
"""

import html
import json
import os
import sys
import urllib.error
import urllib.request


def parse_context(env: dict[str, str] | None = None) -> dict[str, str]:
    """Extract and sanitize runtime context from environment variables."""
    e = env if env is not None else os.environ
    raw_status = e.get("INPUT_STATUS", "success").strip().lower()

    status_map = {
        "success": ("SUCCESS", "🟢", "#2da44e", 0x2DA44E, "Succeeded"),
        "failure": ("FAILURE", "🔴", "#cf222e", 0xCF222E, "Failed"),
        "cancelled": ("CANCELLED", "⚪️", "#8250df", 0x8250DF, "Cancelled"),
        "timed_out": ("TIMED_OUT", "🟡", "#d29922", 0xD29922, "Timed Out"),
    }
    canonical_status, emoji, color_hex, color_int, status_text = status_map.get(
        raw_status, ("UNKNOWN", "⚪️", "#6e7781", 0x6E7781, raw_status.title())
    )

    repo = e.get("GH_REPO", "unknown/repository")
    app_name = e.get("INPUT_APP", "").strip() or repo.split("/")[-1]

    server_url = e.get("GH_SERVER_URL", "https://github.com").rstrip("/")
    run_id = e.get("GH_RUN_ID", "").strip()
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else ""

    commit_sha = e.get("GH_SHA", "").strip()
    short_sha = commit_sha[:7] if commit_sha else ""

    return {
        "status": canonical_status,
        "status_text": status_text,
        "status_emoji": emoji,
        "status_color_hex": color_hex,
        "status_color_int": color_int,
        "app_name": app_name,
        "environment": e.get("INPUT_ENV", "Production").strip(),
        "release_tag": e.get("INPUT_TAG", "").strip(),
        "app_url": e.get("INPUT_URL", "").strip(),
        "custom_message": e.get("INPUT_CUSTOM", "").strip(),
        "actor": e.get("GH_ACTOR", "github-actions").strip(),
        "repo": repo,
        "commit_sha": commit_sha,
        "short_sha": short_sha,
        "run_url": run_url,
        "channel": e.get("INPUT_CHANNEL", "").strip().lower(),
        "webhook_url": e.get("INPUT_WEBHOOK_URL", "").strip(),
        "bot_token": e.get("INPUT_BOT_TOKEN", "").strip(),
        "chat_id": e.get("INPUT_CHAT_ID", "").strip(),
        "thread_id": e.get("INPUT_THREAD_ID", "").strip(),
    }


def send_http_request(url: str, payload: dict, timeout: int = 15) -> tuple[bool, int, str]:
    """Execute HTTP POST request using pure standard library urllib."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "DeployKit-Notifier/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return True, response.status, body
    except urllib.error.HTTPError as ex:
        body = ex.read().decode("utf-8", errors="replace")
        return False, ex.code, body
    except urllib.error.URLError as ex:
        return False, 0, str(ex.reason)
    except Exception as ex:
        return False, 0, str(ex)


# ---------------------------------------------------------------------------
# Provider Handlers
# ---------------------------------------------------------------------------


def dispatch_telegram(ctx: dict[str, str]) -> bool:
    """Send notification to Telegram with HTML formatting & plain-text fallback."""
    token = ctx["bot_token"]
    chat_id = ctx["chat_id"]
    if not token or not chat_id:
        print("DeployKit Warning: Telegram bot_token and chat_id are required.")
        return False

    app_name_safe = html.escape(ctx["app_name"])
    lines = [
        f"<b>{ctx['status_emoji']} {app_name_safe} — Deployment {ctx['status_text']}</b>",
        "",
        f"🏷 <b>Environment:</b> {html.escape(ctx['environment'])}",
    ]
    if ctx["release_tag"]:
        lines.append(f"📦 <b>Release:</b> {html.escape(ctx['release_tag'])}")
    if ctx["actor"]:
        lines.append(f"👤 <b>Triggered By:</b> {html.escape(ctx['actor'])}")
    if ctx["short_sha"]:
        lines.append(f"🔗 <b>Commit:</b> <code>{html.escape(ctx['short_sha'])}</code>")
    if ctx["app_url"]:
        lines.append(f'🌐 <b>Live URL:</b> <a href="{html.escape(ctx["app_url"])}">{html.escape(ctx["app_url"])}</a>')
    if ctx["custom_message"]:
        lines.extend(["", "📝 <b>Release Notes:</b>", html.escape(ctx["custom_message"])])
    if ctx["run_url"]:
        lines.extend(["", f'📊 <a href="{html.escape(ctx["run_url"])}">View GitHub Actions Run</a>'])

    html_payload = {
        "chat_id": chat_id,
        "text": "\n".join(lines),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if ctx["thread_id"]:
        try:
            html_payload["message_thread_id"] = int(ctx["thread_id"])
        except ValueError:
            pass

    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    success, code, body = send_http_request(api_url, html_payload)

    if not success and code == 400:
        # Fallback to plain text if HTML parsing failed
        plain_lines = [
            f"{ctx['status_emoji']} {ctx['app_name']} - Deployment {ctx['status_text']}",
            f"Environment: {ctx['environment']}",
        ]
        if ctx["release_tag"]:
            plain_lines.append(f"Release: {ctx['release_tag']}")
        if ctx["custom_message"]:
            plain_lines.append(f"Notes: {ctx['custom_message']}")
        if ctx["run_url"]:
            plain_lines.append(f"Run: {ctx['run_url']}")

        fallback_payload = {
            "chat_id": chat_id,
            "text": "\n".join(plain_lines),
            "disable_web_page_preview": True,
        }
        if ctx["thread_id"]:
            try:
                fallback_payload["message_thread_id"] = int(ctx["thread_id"])
            except ValueError:
                pass
        success, code, body = send_http_request(api_url, fallback_payload)

    if success:
        print(f"DeployKit: Telegram notification delivered successfully (HTTP {code}).")
        return True
    print(f"DeployKit Warning: Telegram delivery failed (HTTP {code}): {body}")
    return False


def dispatch_slack(ctx: dict[str, str]) -> bool:
    """Send notification to Slack Incoming Webhook."""
    webhook = ctx["webhook_url"]
    if not webhook:
        print("DeployKit Warning: Slack webhook_url is required.")
        return False

    title = f"{ctx['status_emoji']} *{ctx['app_name']}* — Deployment {ctx['status_text']}"
    fields = [
        {"type": "mrkdwn", "text": f"*Environment:*\n{ctx['environment']}"},
        {"type": "mrkdwn", "text": f"*Triggered By:*\n{ctx['actor']}"},
    ]
    if ctx["release_tag"]:
        fields.append({"type": "mrkdwn", "text": f"*Release:*\n{ctx['release_tag']}"})
    if ctx["short_sha"]:
        fields.append({"type": "mrkdwn", "text": f"*Commit:*\n`{ctx['short_sha']}`"})

    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": title}},
        {"type": "section", "fields": fields},
    ]
    if ctx["custom_message"]:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*Notes:*\n{ctx['custom_message']}"}})

    elements = []
    if ctx["app_url"]:
        elements.append({"type": "button", "text": {"type": "plain_text", "text": "🌐 Open App"}, "url": ctx["app_url"]})
    if ctx["run_url"]:
        elements.append({"type": "button", "text": {"type": "plain_text", "text": "📊 View Run"}, "url": ctx["run_url"]})
    if elements:
        blocks.append({"type": "actions", "elements": elements})

    payload = {
        "text": f"{ctx['app_name']} Deployment {ctx['status_text']}",
        "attachments": [{"color": ctx["status_color_hex"], "blocks": blocks}],
    }
    success, code, body = send_http_request(webhook, payload)
    if success:
        print(f"DeployKit: Slack notification delivered successfully (HTTP {code}).")
        return True
    print(f"DeployKit Warning: Slack delivery failed (HTTP {code}): {body}")
    return False


def dispatch_teams(ctx: dict[str, str]) -> bool:
    """Send notification to Microsoft Teams Incoming Webhook (MessageCard)."""
    webhook = ctx["webhook_url"]
    if not webhook:
        print("DeployKit Warning: Teams webhook_url is required.")
        return False

    facts = [
        {"name": "Environment", "value": ctx["environment"]},
        {"name": "Triggered By", "value": ctx["actor"]},
    ]
    if ctx["release_tag"]:
        facts.append({"name": "Release", "value": ctx["release_tag"]})
    if ctx["short_sha"]:
        facts.append({"name": "Commit", "value": ctx["short_sha"]})

    actions = []
    if ctx["app_url"]:
        actions.append({"@type": "OpenUri", "name": "Open Application", "targets": [{"os": "default", "uri": ctx["app_url"]}]})
    if ctx["run_url"]:
        actions.append({"@type": "OpenUri", "name": "View GitHub Actions Run", "targets": [{"os": "default", "uri": ctx["run_url"]}]})

    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": ctx["status_color_hex"].lstrip("#"),
        "summary": f"{ctx['app_name']} Deployment {ctx['status_text']}",
        "sections": [{
            "activityTitle": f"{ctx['status_emoji']} **{ctx['app_name']}** — Deployment {ctx['status_text']}",
            "activitySubtitle": ctx["repo"],
            "facts": facts,
            "text": ctx["custom_message"] if ctx["custom_message"] else "",
        }],
        "potentialAction": actions,
    }
    success, code, body = send_http_request(webhook, payload)
    if success:
        print(f"DeployKit: Microsoft Teams notification delivered successfully (HTTP {code}).")
        return True
    print(f"DeployKit Warning: Microsoft Teams delivery failed (HTTP {code}): {body}")
    return False


def dispatch_discord(ctx: dict[str, str]) -> bool:
    """Send notification to Discord Webhook with rich embed card."""
    webhook = ctx["webhook_url"]
    if not webhook:
        print("DeployKit Warning: Discord webhook_url is required.")
        return False

    fields = [
        {"name": "Environment", "value": ctx["environment"], "inline": True},
        {"name": "Triggered By", "value": ctx["actor"], "inline": True},
    ]
    if ctx["release_tag"]:
        fields.append({"name": "Release", "value": ctx["release_tag"], "inline": True})
    if ctx["short_sha"]:
        fields.append({"name": "Commit", "value": f"`{ctx['short_sha']}`", "inline": True})

    embed = {
        "title": f"{ctx['status_emoji']} {ctx['app_name']} — Deployment {ctx['status_text']}",
        "color": ctx["status_color_int"],
        "fields": fields,
    }
    if ctx["custom_message"]:
        embed["description"] = ctx["custom_message"]
    if ctx["app_url"]:
        embed["url"] = ctx["app_url"]
    if ctx["run_url"]:
        embed["footer"] = {"text": f"GitHub Actions Run • {ctx['repo']}"}

    payload = {
        "username": "DeployKit",
        "embeds": [embed],
    }
    success, code, body = send_http_request(webhook, payload)
    if success:
        print(f"DeployKit: Discord notification delivered successfully (HTTP {code}).")
        return True
    print(f"DeployKit Warning: Discord delivery failed (HTTP {code}): {body}")
    return False


def dispatch_webhook(ctx: dict[str, str]) -> bool:
    """Send structured event payload to generic Webhook URL."""
    webhook = ctx["webhook_url"]
    if not webhook:
        print("DeployKit Warning: Webhook URL is required.")
        return False

    payload = {
        "event": "deployment",
        "app_name": ctx["app_name"],
        "status": ctx["status"].lower(),
        "environment": ctx["environment"],
        "release_tag": ctx["release_tag"],
        "commit_sha": ctx["commit_sha"],
        "actor": ctx["actor"],
        "app_url": ctx["app_url"],
        "custom_message": ctx["custom_message"],
        "run_url": ctx["run_url"],
        "repository": ctx["repo"],
    }
    success, code, body = send_http_request(webhook, payload)
    if success:
        print(f"DeployKit: Webhook notification delivered successfully (HTTP {code}).")
        return True
    print(f"DeployKit Warning: Webhook delivery failed (HTTP {code}): {body}")
    return False


def main() -> int:
    ctx = parse_context()
    channel = ctx["channel"]

    # Auto-detect channel if channel is empty
    if not channel:
        if ctx["bot_token"] and ctx["chat_id"]:
            channel = "telegram"
        elif ctx["webhook_url"]:
            if "discord.com" in ctx["webhook_url"] or "discordapp.com" in ctx["webhook_url"]:
                channel = "discord"
            elif "hooks.slack.com" in ctx["webhook_url"]:
                channel = "slack"
            elif "webhook.office.com" in ctx["webhook_url"] or "office365.com" in ctx["webhook_url"]:
                channel = "teams"
            else:
                channel = "webhook"
        else:
            channel = "telegram"

    providers = {
        "telegram": dispatch_telegram,
        "slack": dispatch_slack,
        "teams": dispatch_teams,
        "discord": dispatch_discord,
        "webhook": dispatch_webhook,
    }

    handler = providers.get(channel)
    if not handler:
        print(f"DeployKit Error: Unsupported notification channel '{channel}'. Supported: {', '.join(providers.keys())}")
        return 1

    ok = handler(ctx)
    return 0 if ok else 0  # Notifications warn but do not fail build step unless required


if __name__ == "__main__":
    sys.exit(main())
