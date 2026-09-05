import configparser
import shutil
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SYSTEMD_DIR = PROJECT_ROOT / "systemd"
SERVICE_FILE = SYSTEMD_DIR / "agent-test-backup.service"
TIMER_FILE = SYSTEMD_DIR / "agent-test-backup.timer"


def read_unit(path):
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read(path)
    return parser


class SystemdBackupTests(unittest.TestCase):
    def test_service_runs_existing_backup_as_user(self):
        service = read_unit(SERVICE_FILE)

        self.assertEqual(
            service["Unit"]["ConditionFileIsExecutable"],
            "%h/projects/agent-test/scripts/backup.sh",
        )
        self.assertEqual(service["Service"]["Type"], "oneshot")
        self.assertEqual(
            service["Service"]["ExecStart"],
            "/usr/bin/bash %h/projects/agent-test/scripts/backup.sh",
        )
        self.assertEqual(service["Service"]["UMask"], "0077")
        self.assertNotIn("User", service["Service"])
        self.assertNotIn("Environment", service["Service"])

    def test_timer_is_daily_persistent_and_enableable(self):
        timer = read_unit(TIMER_FILE)

        self.assertEqual(timer["Timer"]["OnCalendar"], "daily")
        self.assertEqual(timer["Timer"]["Persistent"], "true")
        self.assertEqual(timer["Timer"]["RandomizedDelaySec"], "15m")
        self.assertEqual(
            timer["Timer"]["Unit"], "agent-test-backup.service"
        )
        self.assertEqual(timer["Install"]["WantedBy"], "timers.target")

    @unittest.skipUnless(shutil.which("systemd-analyze"), "systemd is unavailable")
    def test_unit_files_pass_systemd_validation(self):
        result = subprocess.run(
            [
                "systemd-analyze",
                "--user",
                "verify",
                str(SERVICE_FILE),
                str(TIMER_FILE),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
