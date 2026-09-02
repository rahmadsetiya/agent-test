import unittest
from contextlib import redirect_stdout
from io import StringIO

from hello import greet, main


class GreetTests(unittest.TestCase):
    def test_greet_returns_expected_message(self):
        self.assertEqual(greet("OpenClaw"), "Hello, OpenClaw")

    def test_main_prints_greeting_for_name_argument(self):
        stdout = StringIO()
        with redirect_stdout(stdout):
            main(["Yoo"])
        self.assertEqual(stdout.getvalue(), "Hello, Yoo\n")


if __name__ == "__main__":
    unittest.main()
