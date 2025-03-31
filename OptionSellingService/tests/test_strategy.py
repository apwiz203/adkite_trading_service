# tests/test_strategy.py
"""Unit tests for the strategy module."""

import unittest
from ..strategy import check_entry_conditions, select_strikes


class TestStrategy(unittest.TestCase):
    def test_check_entry_conditions(self):
        options_chain = {"iv": 30, "net_credit": 150, "events": False}
        self.assertTrue(check_entry_conditions(options_chain))

    def test_select_strikes(self):
        strikes = select_strikes(19000)
        self.assertEqual(strikes["sold_call"], 19150)


if __name__ == "__main__":
    unittest.main()