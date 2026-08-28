import glob
import os
import re
import unittest

import yaml


class TestWorkflowsSchema(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_all_workflows_valid_yaml(self):
        workflow_files = glob.glob(
            os.path.join(self.root_dir, ".github", "workflows", "*.yml")
        )
        self.assertTrue(len(workflow_files) > 0)
        for wf in workflow_files:
            with self.subTest(file=os.path.basename(wf)):
                with open(wf, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                self.assertIsInstance(data, dict)
                self.assertIn("name", data)
                has_on = "on" in data or True in data
                self.assertTrue(has_on, f"'on' trigger missing in {wf}")
                self.assertIn("jobs", data)
                self.assertIn(
                    "permissions",
                    data,
                    f"{wf} must explicitly specify permissions (least privilege)",
                )

    def test_no_unpinned_main_master_branches(self):
        all_yamls = (
            glob.glob(os.path.join(self.root_dir, ".github", "workflows", "*.yml"))
            + glob.glob(os.path.join(self.root_dir, "actions", "**", "*.yml"), recursive=True)
            + glob.glob(os.path.join(self.root_dir, "examples", "*.yml"))
        )
        for yml in all_yamls:
            with self.subTest(file=os.path.basename(yml)):
                with open(yml, "r", encoding="utf-8") as f:
                    content = f.read()
                for line in content.splitlines():
                    trimmed = line.strip()
                    if trimmed.startswith("uses:") and not trimmed.startswith("uses: ./"):
                        self.assertNotIn(
                            "@main",
                            trimmed,
                            f"Unpinned @main found in {yml}: {trimmed}",
                        )
                        self.assertNotIn(
                            "@master",
                            trimmed,
                            f"Unpinned @master found in {yml}: {trimmed}",
                        )

    def test_reusable_workflows_have_workflow_call(self):
        reusable_wfs = [
            "node-ci.yml",
            "python-ci.yml",
            "docker-build.yml",
            "deploy-ssh-docker.yml",
            "security-scan.yml",
            "telegram-notify.yml",
            "notify.yml",
            "release.yml",
        ]
        for wf_name in reusable_wfs:
            path = os.path.join(self.root_dir, ".github", "workflows", wf_name)
            self.assertTrue(os.path.exists(path), f"Workflow file {wf_name} missing")
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            on_data = data.get("on") or data.get(True) or {}
            self.assertIn(
                "workflow_call",
                on_data,
                f"{wf_name} must support workflow_call",
            )

    def test_deploy_ssh_docker_contracts(self):
        path = os.path.join(self.root_dir, ".github", "workflows", "deploy-ssh-docker.yml")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            data = yaml.safe_load(content)

        call_config = (data.get("on") or data.get(True))["workflow_call"]
        secrets = call_config.get("secrets", {})
        inputs = call_config.get("inputs", {})

        # DEPLOY_SSH_KNOWN_HOSTS must be required for strict verification
        self.assertIn("DEPLOY_SSH_KNOWN_HOSTS", secrets)
        self.assertTrue(secrets["DEPLOY_SSH_KNOWN_HOSTS"].get("required"))

        # rollback-on-failure must be defined
        self.assertIn("rollback-on-failure", inputs)
        self.assertTrue(inputs["rollback-on-failure"].get("default"))

        # Strict host checking must be enabled without runtime ssh-keyscan TOFU
        self.assertIn("StrictHostKeyChecking=yes", content)
        self.assertNotIn("ssh-keyscan", content)

    def test_deploy_input_validation_regex(self):
        service_regex = re.compile(r"^[A-Za-z0-9._-]*$")
        compose_dir_regex = re.compile(r"^[A-Za-z0-9._/~ -]+$")
        image_tag_regex = re.compile(r"^[A-Za-z0-9._/:-]*$")

        # Valid inputs
        self.assertTrue(service_regex.match("api-service"))
        self.assertTrue(service_regex.match("web_app.v1"))
        self.assertTrue(compose_dir_regex.match("/opt/app-production"))
        self.assertTrue(image_tag_regex.match("ghcr.io/org/repo:v1.0.0"))

        # Malicious / dangerous inputs must fail
        self.assertIsNone(service_regex.match("api; rm -rf /"))
        self.assertIsNone(service_regex.match("web$(whoami)"))
        self.assertIsNone(service_regex.match("app`id`"))
        self.assertIsNone(compose_dir_regex.match("/opt/app && echo hack"))
        self.assertIsNone(image_tag_regex.match("v1.0.0 | curl evil.com"))

    def test_node_ci_bun_handling(self):
        path = os.path.join(self.root_dir, ".github", "workflows", "node-ci.yml")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("bun test || echo", content)


if __name__ == "__main__":
    unittest.main()
