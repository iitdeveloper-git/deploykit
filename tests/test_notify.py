import importlib.util
import io
import os
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

# Load actions/notify/send.py under distinct module name
_notify_spec = importlib.util.spec_from_file_location(
    "deploykit_notify_module",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "actions", "notify", "send.py")),
)
notify = importlib.util.module_from_spec(_notify_spec)
_notify_spec.loader.exec_module(notify)


class TestNotifyDispatcher(unittest.TestCase):
    def setUp(self):
        self.base_env = {
            "INPUT_STATUS": "success",
            "INPUT_APP": "Payment API",
            "INPUT_ENV": "Production",
            "INPUT_TAG": "v1.2.3",
            "INPUT_URL": "https://api.example.com",
            "INPUT_CUSTOM": "Fix checkout flow bug",
            "INPUT_THREAD_ID": "42",
            "INPUT_CHANNEL": "",
            "INPUT_WEBHOOK_URL": "",
            "INPUT_BOT_TOKEN": "123456:ABC-DEF",
            "INPUT_CHAT_ID": "-1001234567890",
            "GH_ACTOR": "octocat",
            "GH_SERVER_URL": "https://github.com",
            "GH_REPO": "iitdeveloper-git/deploykit",
            "GH_SHA": "abcdef1234567890",
            "GH_RUN_ID": "987654321",
        }

    def test_parse_context(self):
        ctx = notify.parse_context(self.base_env)
        self.assertEqual(ctx["status"], "SUCCESS")
        self.assertEqual(ctx["status_emoji"], "🟢")
        self.assertEqual(ctx["app_name"], "Payment API")
        self.assertEqual(ctx["short_sha"], "abcdef1")
        self.assertEqual(ctx["run_url"], "https://github.com/iitdeveloper-git/deploykit/actions/runs/987654321")

    def test_parse_context_fallbacks(self):
        ctx = notify.parse_context({})
        self.assertEqual(ctx["status"], "SUCCESS")
        self.assertEqual(ctx["app_name"], "repository")
        self.assertEqual(ctx["environment"], "Production")
        self.assertEqual(ctx["short_sha"], "")
        self.assertEqual(ctx["run_url"], "")

    def test_parse_context_statuses(self):
        for status, expected in [
            ("failure", "FAILURE"),
            ("cancelled", "CANCELLED"),
            ("timed_out", "TIMED_OUT"),
            ("custom_status", "UNKNOWN"),
        ]:
            env = self.base_env.copy()
            env["INPUT_STATUS"] = status
            ctx = notify.parse_context(env)
            self.assertEqual(ctx["status"], expected)

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"ok": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        ctx = notify.parse_context(self.base_env)
        self.assertTrue(notify.dispatch_telegram(ctx))

    def test_dispatch_telegram_missing_secrets(self):
        env = self.base_env.copy()
        env["INPUT_BOT_TOKEN"] = ""
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_no_actor(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"ok": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        env = self.base_env.copy()
        env["GH_ACTOR"] = ""
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_html_fallback_no_thread(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=io.BytesIO(b'{"description": "can\'t parse entities"}'),
        )
        mock_success = MagicMock()
        mock_success.status = 200
        mock_success.read.return_value = b'{"ok": true}'

        mock_urlopen.side_effect = [
            err_resp,
            MagicMock(__enter__=MagicMock(return_value=mock_success)),
        ]

        env = self.base_env.copy()
        env["INPUT_THREAD_ID"] = ""
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_minimal_fields(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"ok": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        env = {
            "INPUT_BOT_TOKEN": "123456:ABC-DEF",
            "INPUT_CHAT_ID": "-1001234567890",
            "GH_REPO": "org/repo",
            "INPUT_THREAD_ID": "not_an_int",
        }
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_failure_non_400(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(b'{"description": "Invalid token"}'),
        )
        mock_urlopen.side_effect = err_resp
        ctx = notify.parse_context(self.base_env)
        self.assertFalse(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_html_fallback(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=io.BytesIO(b'{"description": "can\'t parse entities"}'),
        )
        mock_success = MagicMock()
        mock_success.status = 200
        mock_success.read.return_value = b'{"ok": true}'

        mock_urlopen.side_effect = [
            err_resp,
            MagicMock(__enter__=MagicMock(return_value=mock_success)),
        ]

        ctx = notify.parse_context(self.base_env)
        self.assertTrue(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_html_fallback_minimal_with_invalid_thread(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=io.BytesIO(b'{"description": "can\'t parse entities"}'),
        )
        mock_success = MagicMock()
        mock_success.status = 200
        mock_success.read.return_value = b'{"ok": true}'

        mock_urlopen.side_effect = [
            err_resp,
            MagicMock(__enter__=MagicMock(return_value=mock_success)),
        ]

        env = {
            "INPUT_BOT_TOKEN": "123456:ABC-DEF",
            "INPUT_CHAT_ID": "-1001234567890",
            "GH_REPO": "org/repo",
            "INPUT_THREAD_ID": "not_an_int",
        }
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_telegram_html_fallback_failure(self, mock_urlopen):
        err_resp_1 = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=io.BytesIO(b'{"description": "can\'t parse entities"}'),
        )
        err_resp_2 = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=io.BytesIO(b'{"description": "chat not found"}'),
        )
        mock_urlopen.side_effect = [err_resp_1, err_resp_2]
        ctx = notify.parse_context(self.base_env)
        self.assertFalse(notify.dispatch_telegram(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_slack(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"ok"
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = "https://hooks.slack.com/services/XXX"
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_slack(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_slack_minimal_and_failure(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://hooks.slack.com",
            code=500,
            msg="Internal Error",
            hdrs={},
            fp=io.BytesIO(b"error"),
        )
        mock_urlopen.side_effect = err_resp
        env = {
            "INPUT_WEBHOOK_URL": "https://hooks.slack.com/services/XXX",
            "GH_REPO": "org/repo",
        }
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_slack(ctx))

    def test_dispatch_slack_missing_webhook(self):
        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = ""
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_slack(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_teams(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"1"
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = "https://webhook.office.com/webhookb2/XXX"
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_teams(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_teams_minimal_and_failure(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://webhook.office.com",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=io.BytesIO(b"invalid format"),
        )
        mock_urlopen.side_effect = err_resp
        env = {
            "INPUT_WEBHOOK_URL": "https://webhook.office.com/webhookb2/XXX",
            "GH_REPO": "org/repo",
        }
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_teams(ctx))

    def test_dispatch_teams_missing_webhook(self):
        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = ""
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_teams(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_discord(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 204
        mock_resp.read.return_value = b""
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = "https://discord.com/api/webhooks/XXX"
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_discord(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_discord_minimal_and_failure(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://discord.com",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=io.BytesIO(b"webhook not found"),
        )
        mock_urlopen.side_effect = err_resp
        env = {
            "INPUT_WEBHOOK_URL": "https://discord.com/api/webhooks/XXX",
            "GH_REPO": "org/repo",
        }
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_discord(ctx))

    def test_dispatch_discord_missing_webhook(self):
        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = ""
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_discord(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_webhook(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"status": "received"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = "https://events.example.com/deploy"
        ctx = notify.parse_context(env)
        self.assertTrue(notify.dispatch_webhook(ctx))

    @patch("urllib.request.urlopen")
    def test_dispatch_webhook_failure(self, mock_urlopen):
        err_resp = urllib.error.HTTPError(
            url="https://events.example.com/deploy",
            code=500,
            msg="Server Error",
            hdrs={},
            fp=io.BytesIO(b"Internal Error"),
        )
        mock_urlopen.side_effect = err_resp
        env = {
            "INPUT_WEBHOOK_URL": "https://events.example.com/deploy",
            "GH_REPO": "org/repo",
        }
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_webhook(ctx))

    def test_dispatch_webhook_missing_url(self):
        env = self.base_env.copy()
        env["INPUT_WEBHOOK_URL"] = ""
        ctx = notify.parse_context(env)
        self.assertFalse(notify.dispatch_webhook(ctx))

    @patch("urllib.request.urlopen")
    def test_http_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("DNS resolution failed")
        success, code, _ = notify.send_http_request("https://invalid.example.com", {})
        self.assertFalse(success)
        self.assertEqual(code, 0)

    @patch("urllib.request.urlopen")
    def test_http_generic_exception(self, mock_urlopen):
        mock_urlopen.side_effect = RuntimeError("Socket timeout")
        success, code, _ = notify.send_http_request("https://invalid.example.com", {})
        self.assertFalse(success)
        self.assertEqual(code, 0)

    @patch.object(notify, "dispatch_telegram")
    def test_main_auto_detection_telegram(self, mock_telegram):
        mock_telegram.return_value = True
        env = {
            "INPUT_BOT_TOKEN": "123:ABC",
            "INPUT_CHAT_ID": "456",
            "GH_REPO": "org/repo",
        }
        with patch.dict(os.environ, env, clear=True):
            exit_code = notify.main()
            self.assertEqual(exit_code, 0)
            mock_telegram.assert_called_once()

    @patch.object(notify, "dispatch_telegram")
    def test_main_auto_detection_empty_defaults_to_telegram(self, mock_telegram):
        mock_telegram.return_value = False
        with patch.dict(os.environ, {"GH_REPO": "org/repo"}, clear=True):
            exit_code = notify.main()
            self.assertEqual(exit_code, 0)
            mock_telegram.assert_called_once()

    @patch.object(notify, "dispatch_slack")
    def test_main_auto_detection_slack(self, mock_slack):
        mock_slack.return_value = True
        env = {
            "INPUT_WEBHOOK_URL": "https://hooks.slack.com/services/XXX",
            "GH_REPO": "org/repo",
        }
        with patch.dict(os.environ, env, clear=True):
            exit_code = notify.main()
            self.assertEqual(exit_code, 0)
            mock_slack.assert_called_once()

    @patch.object(notify, "dispatch_discord")
    def test_main_auto_detection_discord(self, mock_discord):
        mock_discord.return_value = True
        env = {
            "INPUT_WEBHOOK_URL": "https://discord.com/api/webhooks/XXX",
            "GH_REPO": "org/repo",
        }
        with patch.dict(os.environ, env, clear=True):
            exit_code = notify.main()
            self.assertEqual(exit_code, 0)
            mock_discord.assert_called_once()

    @patch.object(notify, "dispatch_teams")
    def test_main_auto_detection_teams(self, mock_teams):
        mock_teams.return_value = True
        env = {
            "INPUT_WEBHOOK_URL": "https://webhook.office.com/webhookb2/XXX",
            "GH_REPO": "org/repo",
        }
        with patch.dict(os.environ, env, clear=True):
            exit_code = notify.main()
            self.assertEqual(exit_code, 0)
            mock_teams.assert_called_once()

    @patch.object(notify, "dispatch_webhook")
    def test_main_auto_detection_generic_webhook(self, mock_webhook):
        mock_webhook.return_value = True
        env = {
            "INPUT_WEBHOOK_URL": "https://api.example.com/webhook",
            "GH_REPO": "org/repo",
        }
        with patch.dict(os.environ, env, clear=True):
            exit_code = notify.main()
            self.assertEqual(exit_code, 0)
            mock_webhook.assert_called_once()

    def test_main_unsupported_channel(self):
        env = {
            "INPUT_CHANNEL": "unsupported_channel_xyz",
            "GH_REPO": "org/repo",
        }
        with patch.dict(os.environ, env, clear=True):
            exit_code = notify.main()
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
