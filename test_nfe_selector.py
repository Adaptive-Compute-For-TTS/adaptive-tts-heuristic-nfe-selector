"""Run from this directory: python -m unittest -v"""

import unittest
from nfe_selector import select_nfe


class TestNFESelector(unittest.TestCase):
    def assert_nfe(self, text: str, expected: int) -> None:
        result = select_nfe(text)
        self.assertEqual(result["nfe"], expected, msg=text)
        self.assertEqual(set(result), {"nfe", "reason"})
        self.assertIsInstance(result["reason"], str)
        self.assertTrue(result["reason"])

    def test_three_demo_tiers(self) -> None:
        self.assert_nfe("The kettle is already on the stove.", 4)
        self.assert_nfe("Your total comes to $42.75.", 20)
        self.assert_nfe(
            "Our GPU cluster runs CUDA 12, and the ML team wants an API "
            "endpoint for the TTS model by Q4.",
            32,
        )

    def test_short_simple_and_punctuation(self) -> None:
        self.assert_nfe("Hello, how are you?", 4)
        self.assert_nfe("Wait, you're leaving already?", 4)
        self.assert_nfe("word " * 8, 4)
        self.assert_nfe("word " * 9, 20)

    def test_digits_and_acronyms_do_not_automatically_get_32(self) -> None:
        self.assert_nfe("We are using GPU inference.", 20)
        self.assert_nfe("Call me at 555-0147.", 20)
        self.assert_nfe("NASA delayed the launch again.", 20)
        self.assert_nfe("The CEO joined the call at noon.", 20)

    def test_unusual_characters_route_to_default(self) -> None:
        self.assert_nfe("Siobhan met Joaquín in Reykjavík.", 20)
        self.assert_nfe("Pay $5 today.", 20)

    def test_very_long_boundary(self) -> None:
        self.assert_nfe("word " * 39, 20)
        self.assert_nfe("word " * 40, 32)

    def test_long_with_complexity_marker_boundary(self) -> None:
        self.assert_nfe("word " * 23 + "GPU", 20)  # 24 words, one marker
        self.assert_nfe("word " * 24 + "GPU", 32)  # 25 words, one marker
        self.assert_nfe("word " * 25, 20)          # length alone under 40 -> default

    def test_medium_with_many_markers(self) -> None:
        self.assert_nfe("word " * 15 + "GPU CPU NASA", 32)  # 18 words, three markers
        self.assert_nfe("word " * 14 + "GPU CPU NASA", 20)  # 17 words, three markers
        self.assert_nfe("word " * 18 + "GPU CPU", 20)       # 20 words, two markers

    def test_fallback(self) -> None:
        for invalid in ("", " \n ", "!!!", None, 42):
            with self.subTest(value=invalid):
                result = select_nfe(invalid)  # type: ignore[arg-type]
                self.assertEqual(result["nfe"], 20)
                self.assertIn("Fallback", result["reason"])

    def test_deterministic(self) -> None:
        text = "Please read this sentence naturally."
        self.assertEqual(select_nfe(text), select_nfe(text))


if __name__ == "__main__":
    unittest.main()
