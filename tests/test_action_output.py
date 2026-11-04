"""Behavioral tests for Agent-owned versus user-owned next-step output."""
import unittest
from core.action_output import output_mode


class ActionOutputTests(unittest.TestCase):
    def test_authorized_technical_action_allows_agent_instruction(self):
        x = output_mode(authorized=True)
        self.assertEqual(x["mode"], "AGENT_DECIDABLE")
        self.assertTrue(x["agent_instruction_allowed"])

    def test_recommendation_does_not_invent_permission(self):
        x = output_mode(authorized=False)
        self.assertEqual(x["mode"], "USER_DECISION_REQUIRED")
        self.assertFalse(x["agent_instruction_allowed"])

    def test_major_pivot_stop_and_user_tradeoff_require_choice(self):
        for kwargs in ({"major_task_change": True}, {"project_stop": True},
                       {"user_choice_required": True}):
            with self.subTest(kwargs=kwargs):
                x = output_mode(authorized=True, **kwargs)
                self.assertFalse(x["agent_instruction_allowed"])
                self.assertEqual(x["mode"], "USER_DECISION_REQUIRED")

    def test_manuscript_requires_both_provenance_conditions(self):
        for reviewed, writing in ((False, False), (True, False), (False, True)):
            x = output_mode(authorized=True, manuscript_work=True,
                            summary_reviewed=reviewed, explicit_writing_permission=writing)
            self.assertEqual(x["mode"], "USER_DECISION_REQUIRED")
        x = output_mode(authorized=True, manuscript_work=True,
                        summary_reviewed=True, explicit_writing_permission=True)
        self.assertTrue(x["agent_instruction_allowed"])

    def test_no_next_action_and_invalid_flags(self):
        self.assertEqual(output_mode(authorized=True, has_next_action=False)["mode"],
                         "NO_NEXT_ACTION")
        with self.assertRaises(TypeError):
            output_mode(authorized="yes")


if __name__ == "__main__":
    unittest.main()
