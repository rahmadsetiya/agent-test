import os
import re
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
BACKUP_SCRIPT = PROJECT_ROOT / "scripts" / "backup.sh"
BACKUP_FILES = {
    ".dockerignore",
    ".github/workflows/ci.yml",
    ".gitignore",
    "AGENTS.md",
    "Dockerfile",
    "README.md",
    "compose.staging.yml",
    "compose.yml",
    "hello.py",
    "scripts/backup.sh",
    "systemd/agent-test-backup.service",
    "systemd/agent-test-backup.timer",
    "test_backup.py",
    "test_hello.py",
    "test_systemd.py",
}


class BackupTests(unittest.TestCase):
    def run_backup(self, backup_dir, retention_count=7, check=True):
        environment = os.environ.copy()
        environment["BACKUP_DIR"] = str(backup_dir)
        environment["BACKUP_RETENTION_COUNT"] = str(retention_count)
        return subprocess.run(
            ["bash", str(BACKUP_SCRIPT)],
            cwd=PROJECT_ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=check,
        )

    def test_backup_can_be_listed_and_restored(self):
        with tempfile.TemporaryDirectory() as backup_dir:
            result = self.run_backup(backup_dir)
            archive_path = Path(result.stdout.strip())

            self.assertTrue(archive_path.is_file())
            self.assertRegex(
                archive_path.name,
                r"^agent-test-\d{8}T\d{6}Z\.tar\.gz$",
            )

            with tarfile.open(archive_path, "r:gz") as archive:
                self.assertEqual(set(archive.getnames()), BACKUP_FILES)
                with tempfile.TemporaryDirectory() as restore_dir:
                    archive.extractall(restore_dir, filter="data")
                    restored_root = Path(restore_dir)
                    for relative_path in BACKUP_FILES:
                        self.assertEqual(
                            (restored_root / relative_path).read_bytes(),
                            (PROJECT_ROOT / relative_path).read_bytes(),
                        )

    def test_retention_keeps_only_newest_matching_archives(self):
        with tempfile.TemporaryDirectory() as backup_dir:
            backup_path = Path(backup_dir)
            old_archives = [
                "agent-test-20000101T000000Z.tar.gz",
                "agent-test-20000101T000001Z.tar.gz",
                "agent-test-20000101T000002Z.tar.gz",
            ]
            for archive_name in old_archives:
                (backup_path / archive_name).write_bytes(b"old backup")
            unrelated_archive = backup_path / "unrelated.tar.gz"
            unrelated_archive.write_bytes(b"unrelated backup")

            result = self.run_backup(backup_dir, retention_count=2)
            new_archive = Path(result.stdout.strip()).name
            remaining = sorted(
                path.name for path in backup_path.glob("agent-test-*.tar.gz")
            )

            self.assertEqual(
                remaining,
                [old_archives[-1], new_archive],
            )
            self.assertTrue(unrelated_archive.is_file())

    def test_invalid_retention_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as backup_dir:
            result = self.run_backup(backup_dir, retention_count=0, check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("positive integer", result.stderr)
            self.assertEqual(list(Path(backup_dir).iterdir()), [])

    def test_backup_directory_inside_repository_is_rejected(self):
        backup_dir = PROJECT_ROOT / "backup-output"
        result = self.run_backup(backup_dir, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the repository", result.stderr)
        self.assertFalse(backup_dir.exists())


if __name__ == "__main__":
    unittest.main()
