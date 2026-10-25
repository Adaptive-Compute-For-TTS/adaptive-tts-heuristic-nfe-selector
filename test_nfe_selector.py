"""Run with: python -m unittest discover -s Adaptive-Compute-For-TTS -v"""

import unittest

from nfe_selector import select_nfe


class TestNFESelector(unittest.TestCase):
    def test_three_demo_prompts(self) -> None:
        prompts = [
            ("Hello, how are you?", 4),
            ("Can you tell me what time the meeting starts on the following day?", 20),
            ("The AI model achieved 97.8% accuracy across 14,000 samples.", 32),
        ]
        for prompt, expected_nfe in prompts:
            with self.subTest(prompt=prompt):
                result = select_nfe(prompt)
                self.assertEqual(result["nfe"], expected_nfe)
                self.assertIsInstance(result["reason"], str)
                self.assertTrue(result["reason"])
                self.assertEqual(set(result), {"nfe", "reason"})

    def test_fallbacks_to_20(self) -> None:
        for invalid in ("", "  \n  ", "!!!", None, 42):
            with self.subTest(invalid=invalid):
                result = select_nfe(invalid)  # type: ignore[arg-type]
                self.assertEqual(result["nfe"], 20)
                self.assertIn("Fallback", result["reason"])

    def test_repeatable(self) -> None:
        prompt = "Please read this sentence naturally."
        self.assertEqual(select_nfe(prompt), select_nfe(prompt))

    def test_length_boundaries(self) -> None:
        self.assertEqual(select_nfe("word " * 8)["nfe"], 4)
        self.assertEqual(select_nfe("word " * 9)["nfe"], 20)
        self.assertEqual(select_nfe("word " * 24)["nfe"], 20)
        self.assertEqual(select_nfe("word " * 25)["nfe"], 32)

    def test_acronym_complexity(self) -> None:
        self.assertEqual(select_nfe("We are using GPU inference.")["nfe"], 32)


if __name__ == "__main__":
    unittest.main()
