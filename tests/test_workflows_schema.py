import glob
import os
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


if __name__ == "__main__":
    unittest.main()
