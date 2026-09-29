#!/usr/bin/env python3
import argparse
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import jev_classify_word_origins as classifier


class FakeClient:
    async def system_one(self, state, questions):
        if state["word"] == "failing-word":
            raise RuntimeError("request failed with secret-test-key")
        answer = SimpleNamespace(
            choice="compound_clipping",
            confidence=0.91,
            probabilities={"compound_clipping": 0.91, "uncertain": 0.09},
        )
        return SimpleNamespace(choices={"kind": answer}, model="jev-test-1.2")


class JevClassifierTests(unittest.IsolatedAsyncioTestCase):
    async def test_failures_keep_word_and_counts_and_successes_keep_model(self):
        items = [
            ("working-word", {"type": "B", "derivation": "one + two"}),
            ("failing-word", {"type": "B", "derivation": "unavailable"}),
        ]
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "secret-test-key"}):
            results, errors = await classifier.classify_items(FakeClient(), items, concurrency=2)

        report = classifier.build_report(
            items,
            results,
            errors,
            argparse.Namespace(model="jev-test-1.2"),
        )
        self.assertEqual(report["requested"], 2)
        self.assertEqual(report["succeeded"], 1)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["errors"][0]["word"], "failing-word")
        self.assertNotIn("secret-test-key", report["errors"][0]["error"])
        self.assertEqual(report["results"][0]["model"], "jev-test-1.2")
        self.assertEqual(report["metadata"]["model"]["requested"], "jev-test-1.2")
        self.assertEqual(report["metadata"]["model"]["resolved"], ["jev-test-1.2"])
        self.assertEqual(report["metadata"]["requested"], 2)
        self.assertEqual(report["metadata"]["succeeded"], 1)
        self.assertEqual(report["metadata"]["failed"], 1)

    def test_parser_pins_the_default_model_and_validates_positive_limits(self):
        args = classifier.build_parser().parse_args(["--output", str(ROOT / "out" / "test.json")])
        self.assertEqual(args.model, "jev-latest")
        self.assertEqual(classifier.positive_int("12"), 12)
        with self.assertRaises(argparse.ArgumentTypeError):
            classifier.positive_int("0")


if __name__ == "__main__":
    unittest.main()
