"""Regression checks for the dictionary consumed by translator_google.py.

Run from the repository root with:
    python -m unittest discover -s tests

By default the test reads dictionary.json, matching the translator's default
input_file. Set DICTIONARY_FILE to validate a dictionary at another path.
"""

import json
import os
import unittest
from pathlib import Path


EXPECTED_TERMS = 2_214
EXPECTED_DEFINITIONS = 2_249
COUNT_TOLERANCE = 10

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DICTIONARY_PATH = Path(
    os.environ.get("DICTIONARY_FILE", REPOSITORY_ROOT / "dictionary.json")
)


class DictionaryCountsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DICTIONARY_PATH.is_file():
            raise FileNotFoundError(
                f"Dictionary input file not found: {DICTIONARY_PATH}. "
                "Place dictionary.json in the repository root or set "
                "DICTIONARY_FILE to the input file path."
            )

        with DICTIONARY_PATH.open("r", encoding="utf-8") as dictionary_file:
            cls.dictionary = json.load(dictionary_file)

    def test_dictionary_is_an_array(self):
        self.assertIsInstance(
            self.dictionary, list, "The dictionary JSON root must be an array."
        )

    def test_entries_have_the_expected_structure(self):
        for index, entry in enumerate(self.dictionary):
            with self.subTest(entry=index):
                self.assertIsInstance(entry, dict)
                self.assertIn("sanskrit", entry)
                self.assertIn("name", entry)
                self.assertIn("definitions", entry)

                self.assertIsInstance(entry["sanskrit"], str)
                self.assertIsInstance(entry["name"], str)
                self.assertTrue(
                    entry["name"].islower() or not entry["name"],
                    f"Entry {index}: name must be lowercase.",
                )
                self.assertFalse(
                    any(character.isdigit() for character in entry["name"]),
                    f"Entry {index}: name must not contain numerical subscripts.",
                )

                self.assertIsInstance(entry["definitions"], list)
                for definition_index, definition in enumerate(entry["definitions"]):
                    with self.subTest(
                        entry=index, definition=definition_index
                    ):
                        self.assertIsInstance(definition, dict)
                        self.assertIn("definition", definition)
                        self.assertIn("isVerb", definition)
                        self.assertIn("isRootVerb", definition)
                        self.assertIsInstance(definition["definition"], str)
                        self.assertIsInstance(definition["isVerb"], bool)
                        self.assertIsInstance(definition["isRootVerb"], bool)

    def test_term_count_is_within_tolerance(self):
        actual_terms = len(self.dictionary)
        self.assertLessEqual(
            abs(actual_terms - EXPECTED_TERMS),
            COUNT_TOLERANCE,
            (
                f"Expected {EXPECTED_TERMS} ± {COUNT_TOLERANCE} terms, "
                f"found {actual_terms}."
            ),
        )

    def test_total_definition_count_is_within_tolerance(self):
        actual_definitions = sum(
            len(entry["definitions"]) for entry in self.dictionary
        )
        self.assertLessEqual(
            abs(actual_definitions - EXPECTED_DEFINITIONS),
            COUNT_TOLERANCE,
            (
                f"Expected {EXPECTED_DEFINITIONS} ± {COUNT_TOLERANCE} definitions, "
                f"found {actual_definitions}."
            ),
        )


if __name__ == "__main__":
    unittest.main()
