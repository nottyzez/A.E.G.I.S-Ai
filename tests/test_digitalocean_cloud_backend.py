"""
DigitalOcean deployment bundle checks (plan Task 4).

These assert the files exist and carry the settings a single-Droplet run needs:
one worker, a swapfile for the TensorFlow model, an Nginx proxy that can carry
the ESP32's command polling, and persistent mounts for state that must survive a
container rebuild.
"""

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestDigitalOceanDeploymentBundle(unittest.TestCase):

    def test_dockerfile_and_compose_enforce_single_worker_and_volumes(self):
        dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
        compose = (PROJECT_ROOT / "docker-compose.digitalocean.yml").read_text(encoding="utf-8")
        nginx = (PROJECT_ROOT / "deploy" / "digitalocean" / "nginx.conf").read_text(encoding="utf-8")
        setup_sh = (PROJECT_ROOT / "deploy" / "digitalocean" / "setup_droplet.sh").read_text(encoding="utf-8")

        self.assertIn("--workers", dockerfile)
        self.assertIn("1", dockerfile)
        self.assertIn("AEGIS_REQUIRE_AUTH", compose)
        self.assertIn("client_max_body_size 10M", nginx)
        self.assertIn("/api/command", nginx)
        self.assertIn("swapfile", setup_sh)

    def test_bundle_carries_the_paths_the_app_writes(self):
        """The container must persist the files the app writes (calibration.json,
        test_captures/) or a rebuild on the droplet silently resets them, plus
        the state DB the deferred cloud task queue will add."""
        compose = (PROJECT_ROOT / "docker-compose.digitalocean.yml").read_text(encoding="utf-8")
        for mount in ("server/runtime_state.db", "server/calibration.json", "test_captures"):
            self.assertIn(mount, compose, f"{mount} must be a persistent volume")

        setup_sh = (PROJECT_ROOT / "deploy" / "digitalocean" / "setup_droplet.sh").read_text(encoding="utf-8")
        # Docker turns a missing bind-mount source into a directory; pre-create
        # the files so the mounts stay files.
        self.assertIn("touch", setup_sh)
        self.assertIn("calibration.json", setup_sh)

    def test_dockerignore_keeps_the_build_context_small(self):
        """Without this the context is ~3 GB (venv + venv + .git) and every
        docker build on the droplet copies it over the wire first."""
        dockerignore = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")
        # ai-env312 is the 2.2 GB local venv; .git is 836 MB.
        for entry in (".git", "ai-env312", "node_modules", "__pycache__"):
            self.assertIn(entry, dockerignore)


if __name__ == "__main__":
    unittest.main()
