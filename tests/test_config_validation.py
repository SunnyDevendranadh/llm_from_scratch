"""Configuration validation tests that do not require a model runtime."""
import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NanoCloudConfig, TinyClaudeConfig


class TestConfigValidation(unittest.TestCase):
    def test_default_configs_are_valid(self):
        self.assertEqual(TinyClaudeConfig().embed_dim // TinyClaudeConfig().num_heads, 64)
        self.assertEqual(NanoCloudConfig().embed_dim // NanoCloudConfig().num_heads, 64)

    def test_invalid_dimensions_fail_with_clear_error(self):
        cases = [
            ({"vocab_size": 0}, "vocab_size"),
            ({"embed_dim": 0}, "embed_dim"),
            ({"num_heads": 0}, "num_heads"),
            ({"embed_dim": 385}, "divisible"),
            ({"ff_dim": 0}, "ff_dim"),
            ({"num_layers": 0}, "num_layers"),
            ({"max_seq_len": 15}, "max_seq_len"),
        ]
        for config_type in (TinyClaudeConfig, NanoCloudConfig):
            for overrides, message in cases:
                with self.subTest(config=config_type.__name__, overrides=overrides):
                    with self.assertRaisesRegex(ValueError, message):
                        config_type(**overrides)

if __name__ == "__main__":
    unittest.main()
