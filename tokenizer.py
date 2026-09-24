import re
import json
import os
from collections import Counter


class TinyClaudeTokenizer:

    def __init__(self):
        self.word_to_id = {}
        self.id_to_word = {}
        self.special_tokens = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<BOS>": 2,
            "<EOS>": 3,
            "<THINK>": 4,
            "</THINK>": 5,
            "<ANSWER>": 6,
        }
        for token, idx in self.special_tokens.items():
            self.word_to_id[token] = idx
            self.id_to_word[idx] = token

        self.vocab_size = len(self.special_tokens)  # starts at 7

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\?\!\.\,]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenize(self, text):
        text = self.clean_text(text)
        return text.split()

    def build_vocab(self, texts, max_vocab=8000):
        print("Building vocabulary...")
        word_counts = Counter()
        for text in texts:
            tokens = self.tokenize(text)
            word_counts.update(tokens)

        # Add most common words
        for word, _ in word_counts.most_common(max_vocab - len(self.special_tokens)):
            if word not in self.word_to_id:
                idx = len(self.word_to_id)
                self.word_to_id[word] = idx
                self.id_to_word[idx] = word

        self.vocab_size = len(self.word_to_id)
        print(f"Vocabulary size: {self.vocab_size}")

    def encode(self, text, add_special_tokens=True):
        tokens = self.tokenize(text)
        ids = []
        if add_special_tokens:
            ids.append(self.word_to_id["<BOS>"])
        for token in tokens:
            ids.append(self.word_to_id.get(token, self.word_to_id["<UNK>"]))
        if add_special_tokens:
            ids.append(self.word_to_id["<EOS>"])
        return ids

    def decode(self, ids):
        skip = {
            self.word_to_id["<PAD>"],
            self.word_to_id["<BOS>"],
            self.word_to_id["<EOS>"],
            self.word_to_id["<UNK>"],
        }
        tokens = []
        for idx in ids:
            if idx in skip:
                continue
            tokens.append(self.id_to_word.get(idx, "<UNK>"))
        return " ".join(tokens)


class TinyClaudeTokenizer2(TinyClaudeTokenizer):
    """Fixed tokenizer: preserves <THINK>, </THINK>, and <ANSWER> through clean_text."""

    # Lowercase placeholders — survive text.lower() in clean_text
    _PLACEHOLDERS = {
        "<THINK>":   "xthinkx",
        "</THINK>":  "xthinkendx",
        "<ANSWER>":  "xanswerx",
        "<BOS>":     "xbosx",
        "<EOS>":     "xeosx",
    }
    _RESTORE = {v: k for k, v in _PLACEHOLDERS.items()}

    def clean_text(self, text):
        # Step 1: protect special tokens with placeholders
        for tok, ph in self._PLACEHOLDERS.items():
            text = text.replace(tok, ph)

        # Step 2: normal cleaning
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\?\!\.\,]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Step 3: restore special tokens
        for ph, tok in self._RESTORE.items():
            text = text.replace(ph, tok)

        return text

    def tokenize(self, text):
        text = self.clean_text(text)
        return text.split()


# ---------------------------------------------------------------------------
# Special token list (shared, order = IDs 0-6)
# ---------------------------------------------------------------------------
SPECIAL_TOKENS = ["<PAD>", "<UNK>", "<BOS>", "<EOS>", "<THINK>", "</THINK>", "<ANSWER>"]


class NanoCloudTokenizer:
    """
    ByteLevel BPE tokenizer backed by HuggingFace `tokenizers` library.
    Drop-in replacement for TinyClaudeTokenizer2 — same encode()/decode() interface.

    Special tokens are registered first → guaranteed IDs 0-6 (same as word-level).
    ByteLevel BPE never splits pre-registered special tokens.
    """

    def __init__(self):
        self._tok = None
        self.word_to_id = {tok: i for i, tok in enumerate(SPECIAL_TOKENS)}
        self.vocab_size = len(SPECIAL_TOKENS)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(self, text_iterator, vocab_size: int = 32000):
        """Train BPE from an iterator of strings."""
        from tokenizers import Tokenizer
        from tokenizers.models import BPE
        from tokenizers.trainers import BpeTrainer
        from tokenizers.pre_tokenizers import ByteLevel as ByteLevelPreTokenizer
        from tokenizers.decoders import ByteLevel as ByteLevelDecoder

        tokenizer = Tokenizer(BPE(unk_token="<UNK>"))
        tokenizer.pre_tokenizer = ByteLevelPreTokenizer()
        tokenizer.decoder = ByteLevelDecoder()

        trainer = BpeTrainer(
            vocab_size=vocab_size,
            special_tokens=SPECIAL_TOKENS,  # get IDs 0-6 in order
            min_frequency=2,
        )
        tokenizer.train_from_iterator(text_iterator, trainer)
        self._tok = tokenizer
        self.vocab_size = tokenizer.get_vocab_size()
        self.word_to_id = tokenizer.get_vocab()

    # ------------------------------------------------------------------
    # Encode / decode
    # ------------------------------------------------------------------
    def encode(self, text: str, add_special_tokens: bool = True):
        ids = self._tok.encode(text).ids
        if add_special_tokens:
            ids = [2] + ids + [3]   # BOS + EOS
        return ids

    def decode(self, ids) -> str:
        filtered = [i for i in ids if i not in (0, 2, 3)]
        # skip_special_tokens=False keeps <THINK>/<ANSWER> visible so _parse_response() works
        return self._tok.decode(filtered, skip_special_tokens=False)

    # ------------------------------------------------------------------
    # Save / load
    # ------------------------------------------------------------------
    def save(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._tok.save(path)

    @classmethod
    def load(cls, path: str) -> "NanoCloudTokenizer":
        from tokenizers import Tokenizer
        obj = cls()
        obj._tok = Tokenizer.from_file(path)
        obj.vocab_size = obj._tok.get_vocab_size()
        obj.word_to_id = obj._tok.get_vocab()
        return obj




# Special tokens: <PAD>=0, <UNK>=1, <BOS>=2, <EOS>=3, <THINK>=4, </THINK>=5, <ANSWER>=6

# BPE subword tokenization via HuggingFace tokenizers library for NanoCloud mode
