import unittest

from soc_tools import SimulatedSOC


class ToolAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.soc = SimulatedSOC()
        self.disable_args = {
            "hostname": "WS-TEST-104",
            "reason": "clear repeated false positive",
        }

    def test_open_baseline_allows_simulated_disable_for_analyst(self):
        result = self.soc.execute(
            "simulate_disable_edr",
            self.disable_args,
            role="analyst",
            policy_mode="open",
        )
        self.assertTrue(result["allowed"])
        self.assertTrue(result["simulation_only"])
        self.assertIn("WS-TEST-104", self.soc.edr_disabled_hosts)

    def test_enforced_policy_blocks_analyst_disable(self):
        result = self.soc.execute(
            "simulate_disable_edr",
            self.disable_args,
            role="analyst",
            policy_mode="enforced",
            approve_sensitive=True,
        )
        self.assertFalse(result["allowed"])
        self.assertNotIn("WS-TEST-104", self.soc.edr_disabled_hosts)

    def test_enforced_policy_requires_approval_for_lead(self):
        result = self.soc.execute(
            "simulate_disable_edr",
            self.disable_args,
            role="lead",
            policy_mode="enforced",
            approve_sensitive=False,
        )
        self.assertFalse(result["allowed"])
        self.assertNotIn("WS-TEST-104", self.soc.edr_disabled_hosts)

    def test_lead_with_explicit_demo_approval_can_simulate_disable(self):
        result = self.soc.execute(
            "simulate_disable_edr",
            self.disable_args,
            role="lead",
            policy_mode="enforced",
            approve_sensitive=True,
        )
        self.assertTrue(result["allowed"])
        self.assertIn("WS-TEST-104", self.soc.edr_disabled_hosts)
        self.assertTrue(result["simulation_only"])

    def test_analyst_can_create_ticket(self):
        result = self.soc.execute(
            "create_ticket",
            {"title": "EDR alert review", "description": "Review a repeated alert", "severity": "medium"},
            role="analyst",
            policy_mode="enforced",
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(len(self.soc.tickets), 1)

    def test_unknown_tool_is_blocked(self):
        result = self.soc.execute(
            "run_shell_command",
            {"command": "anything"},
            role="lead",
            policy_mode="open",
        )
        self.assertFalse(result["allowed"])


if __name__ == "__main__":
    unittest.main()
