import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from io import StringIO

from hello import greet, main


class GreetTests(unittest.TestCase):
    def test_greet_returns_expected_message(self):
        self.assertEqual(greet("OpenClaw"), "Hello, OpenClaw!")

    def test_main_prints_greeting_for_name_argument(self):
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["Yoo"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "Hello, Yoo!\n")

    def test_main_handles_missing_name_gracefully(self):
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = main([])
        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr.getvalue(), "Please provide a name.\n")


if __name__ == "__main__":
    unittest.main()
