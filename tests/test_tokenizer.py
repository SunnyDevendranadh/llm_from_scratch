"""Behavioral tests for the local word tokenizer."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer import TinyClaudeTokenizer2


class TinyClaudeTokenizerTests(unittest.TestCase):
    def test_round_trip_preserves_registered_words(self):
        tokenizer = TinyClaudeTokenizer2()
        tokenizer.build_vocab(["Hello world", "hello again"])

        ids = tokenizer.encode("Hello world")

        self.assertEqual(ids[0], tokenizer.word_to_id["<BOS>"])
        self.assertEqual(ids[-1], tokenizer.word_to_id["<EOS>"])
        self.assertEqual(tokenizer.decode(ids), "hello world")

    def test_unknown_word_uses_reserved_id(self):
        tokenizer = TinyClaudeTokenizer2()
        tokenizer.build_vocab(["known"])
        self.assertEqual(tokenizer.encode("unknown", add_special_tokens=False), [1])

    def test_thinking_markers_survive_tokenization(self):
        tokenizer = TinyClaudeTokenizer2()
        text = "<THINK> reason </THINK> <ANSWER> done"
        tokenizer.build_vocab([text])

        ids = tokenizer.encode(text, add_special_tokens=False)

        self.assertEqual(tokenizer.decode(ids), "<THINK> reason </THINK> <ANSWER> done")


if __name__ == "__main__":
    unittest.main()
