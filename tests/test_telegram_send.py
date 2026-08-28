import io
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add actions/telegram-notify to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "actions", "telegram-notify")
    ),
)

import send


class TestTelegramNotify(unittest.TestCase):
    def setUp(self):
        self.sample_env = {
            "INPUT_STATUS": "success",
            "INPUT_APP": "PaymentGateway",
            "INPUT_ENV": "Production",
            "INPUT_TAG": "v1.2.3",
            "INPUT_URL": "https://pay.example.com",
            "INPUT_CUSTOM": "Deployed hotfix for **order** processing `issue-42`.",
            "INPUT_THREAD_ID": "12345",
            "INPUT_BOT_TOKEN": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "INPUT_CHAT_ID": "-1001987654321",
            "GH_ACTOR": "octocat",
            "GH_SERVER_URL": "https://github.com",
            "GH_REPO": "octocat/hello-world",
            "GH_SHA": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d",
            "GH_RUN_ID": "987654321",
        }

    def test_parse_context(self):
        ctx = send.parse_context(self.sample_env)
        self.assertEqual(ctx["status"], "success")
        self.assertEqual(ctx["app"], "PaymentGateway")
        self.assertEqual(ctx["env_name"], "Production")
        self.assertEqual(ctx["tag"], "v1.2.3")
        self.assertEqual(ctx["actor"], "octocat")
        self.assertEqual(ctx["repo"], "octocat/hello-world")

    def test_parse_context_fallbacks(self):
        ctx = send.parse_context({})
        self.assertEqual(ctx["status"], "success")
        self.assertEqual(ctx["app"], "CI/CD Pipeline")
        self.assertEqual(ctx["env_name"], "Production")
        self.assertEqual(ctx["tag"], "")
        self.assertEqual(ctx["bot_token"], "")

    def test_status_metadata_deployment_success(self):
        h_emoji, label, e_emoji = send.get_status_metadata("success", "Production")
        self.assertEqual(h_emoji, "🚀")
        self.assertEqual(label, "Deployment Succeeded")
        self.assertEqual(e_emoji, "🟢")

    def test_status_metadata_ci_success(self):
        h_emoji, label, e_emoji = send.get_status_metadata("success", "CI / Tests")
        self.assertEqual(h_emoji, "🚀")
        self.assertEqual(label, "CI Pipeline Passed")
        self.assertEqual(e_emoji, "🟢")

    def test_status_metadata_ci_failure(self):
        h_emoji, label, e_emoji = send.get_status_metadata("failure", "CI / Tests")
        self.assertEqual(h_emoji, "❌")
        self.assertEqual(label, "CI / Test Suite Failed")
        self.assertEqual(e_emoji, "🔴")

    def test_status_metadata_cancelled(self):
        h_emoji, label, e_emoji = send.get_status_metadata("cancelled", "Production")
        self.assertEqual(h_emoji, "⚪️")
        self.assertEqual(label, "Run Cancelled")
        self.assertEqual(e_emoji, "⚪️")

    def test_status_metadata_timed_out(self):
        h_emoji, label, e_emoji = send.get_status_metadata("timed_out", "Production")
        self.assertEqual(h_emoji, "⏳")
        self.assertEqual(label, "Job Timed Out")
        self.assertEqual(e_emoji, "🟡")

    def test_build_messages_html_formatting(self):
        ctx = send.parse_context(self.sample_env)
        html_msg, plain_msg = send.build_messages(ctx)

        # Check HTML tags
        self.assertIn("<b>🚀 PaymentGateway — Deployment Succeeded</b>", html_msg)
        self.assertIn("🏷 <b>Environment:</b> 🟢 Production", html_msg)
        self.assertIn("📦 <b>Release:</b> <code>v1.2.3</code>", html_msg)
        self.assertIn("👤 <b>Triggered By:</b> octocat", html_msg)
        self.assertIn(
            '<a href="https://github.com/octocat/hello-world/commit/7fd1a60b01f91b314f59955a4e4d4e80d8edf11d">7fd1a60</a>',
            html_msg,
        )
        self.assertIn(
            '<a href="https://pay.example.com">https://pay.example.com</a>', html_msg
        )
        self.assertIn("<b>order</b> processing <code>issue-42</code>", html_msg)
        self.assertIn(
            '<a href="https://github.com/octocat/hello-world/actions/runs/987654321">View GitHub Actions Run</a>',
            html_msg,
        )

        # Check Plain Text
        self.assertIn("🚀 PaymentGateway — Deployment Succeeded", plain_msg)
        self.assertIn("Environment: Production", plain_msg)
        self.assertIn("Release: v1.2.3", plain_msg)
        self.assertIn("Triggered By: octocat", plain_msg)

    def test_html_escaping(self):
        env = {
            "INPUT_APP": "<Script>alert(1)</Script>",
            "INPUT_ENV": "Staging & Testing",
            "INPUT_CUSTOM": "Fix <xml> & 'quotes'",
            "INPUT_TAG": "<v1.0>",
        }
        ctx = send.parse_context(env)
        html_msg, _ = send.build_messages(ctx)
        self.assertNotIn("<Script>", html_msg)
        self.assertIn("&lt;Script&gt;alert(1)&lt;/Script&gt;", html_msg)
        self.assertIn("Staging &amp; Testing", html_msg)
        self.assertIn("&lt;v1.0&gt;", html_msg)

    @patch("urllib.request.urlopen")
    def test_send_telegram_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": {}}).encode(
            "utf-8"
        )
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        ok, res = send.send_telegram("fake_token", {"chat_id": "123", "text": "hello"})
        self.assertTrue(ok)
        self.assertIn('"ok": true', res)

    @patch("send.send_telegram")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_skip_when_no_credentials(self, mock_stdout, mock_send):
        with patch.dict(os.environ, {}, clear=True):
            code = send.main()
            self.assertEqual(code, 0)
            mock_send.assert_not_called()

    @patch("send.send_telegram")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_success_flow(self, mock_stdout, mock_send):
        mock_send.return_value = (True, '{"ok": true}')
        with patch.dict(os.environ, self.sample_env, clear=True):
            code = send.main()
            self.assertEqual(code, 0)
            self.assertEqual(mock_send.call_count, 1)

    @patch("send.send_telegram")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_fallback_to_plain_text(self, mock_stdout, mock_send):
        # First call fails (e.g. HTML parse error), second succeeds
        mock_send.side_effect = [
            (False, "Bad Request: can't parse entities"),
            (True, '{"ok": true}'),
        ]
        with patch.dict(os.environ, self.sample_env, clear=True):
            code = send.main()
            self.assertEqual(code, 0)
            self.assertEqual(mock_send.call_count, 2)


if __name__ == "__main__":
    unittest.main()
