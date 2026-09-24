"""
Dataset and DataLoader utilities for TinyClaude2 and NanoCloud training.

TinyClaudeDataset:     Map-style dataset for local training with collation/padding.
WeightedMixDataset:    Streaming iterable dataset mixing FineWeb-Edu, OpenHermes,
                       SlimOrca, MathInstruct, and The Stack with weighted sampling.
"""

import random
import itertools

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, IterableDataset


class TinyClaudeDataset(Dataset):

    def __init__(self, texts, tokenizer, max_seq_len=512):
        self.examples = []
        skipped = 0

        for text in texts:
            ids = tokenizer.encode(text, add_special_tokens=True)
            if len(ids) < 4:
                skipped += 1
                continue
            if len(ids) > max_seq_len:
                ids = ids[:max_seq_len]
            self.examples.append(ids)

        lengths = [len(e) for e in self.examples]
        print(f"Dataset: {len(self.examples)} examples ({skipped} skipped) "
              f"| len min={min(lengths)} avg={sum(lengths)//len(lengths)} max={max(lengths)}")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ids = self.examples[idx]
        return (torch.tensor(ids[:-1], dtype=torch.long),
                torch.tensor(ids[1:],  dtype=torch.long))


def collate_fn(batch):
    inputs, targets = zip(*batch)
    max_len = max(len(x) for x in inputs)

    padded_inputs  = [F.pad(x, (0, max_len - len(x)), value=0) for x in inputs]
    padded_targets = [F.pad(t, (0, max_len - len(t)), value=-100) for t in targets]

    return torch.stack(padded_inputs), torch.stack(padded_targets)


def make_dataloader(texts, tokenizer, batch_size=16, max_seq_len=512, shuffle=True):
    dataset = TinyClaudeDataset(texts, tokenizer, max_seq_len)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=collate_fn,
        num_workers=0,   # required for MPS stability
    )


# ---------------------------------------------------------------------------
# NanoCloud: streaming weighted-mix dataset
# ---------------------------------------------------------------------------

def wrap_with_think(example):
    """
    Convert OpenHermes/SlimOrca ChatML conversations into <THINK> format.
    Splits long gpt turns at the first sentence boundary after 100 chars.
    """
    for msg in example.get("conversations", []):
        if msg.get("from") == "gpt" and len(msg.get("value", "")) > 150:
            text = msg["value"]
            split = next(
                (i for i, c in enumerate(text) if c in ".!\n" and i > 100),
                len(text) // 2,
            )
            msg["value"] = (
                f"<THINK> {text[:split + 1]} </THINK> "
                f"<ANSWER> {text[split + 1:].strip()}"
            )
    return example


class WeightedMixDataset(IterableDataset):
    """
    Streams from HuggingFace datasets with weighted sampling via interleave_datasets.

    Tier 1 (65%): FineWeb-Edu — general knowledge
    Tier 2 (25%): OpenHermes + SlimOrca + MathInstruct — reasoning/CoT
    Tier 3 (10%): The Stack smol — code for logic structure

    Hand-written reasoning data is injected alongside Tier 2 as a format anchor.
    CRITICAL: reasoning stays ≥ 25% of every batch.
    """

    def __init__(self, tokenizer, local_reasoning_texts=None,
                 max_seq_len: int = 1024, weights=(0.65, 0.25, 0.10)):
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len
        self.weights = weights
        self.local_reasoning_texts = local_reasoning_texts or []

    def _build_sources(self):
        from datasets import load_dataset, interleave_datasets

        fineweb = (load_dataset("HuggingFaceFW/fineweb-edu", name="sample-10BT",
                                streaming=True, split="train")
                   .shuffle(buffer_size=10000, seed=42))

        openhermes = (load_dataset("teknium/OpenHermes-2.5", streaming=True, split="train")
                      .shuffle(buffer_size=5000, seed=42)
                      .map(wrap_with_think))

        slimorca = (load_dataset("Open-Orca/SlimOrca", streaming=True, split="train")
                    .shuffle(buffer_size=5000, seed=42)
                    .map(wrap_with_think))

        def _wrap_mathinstruct(x):
            out = x.get("output", "")
            if not out:
                return x
            think_part = out[:200]
            answer_part = out[200:].strip()
            return {"conversations": [{"from": "gpt",
                                       "value": f"<THINK> {think_part} </THINK> <ANSWER> {answer_part}"}]}

        mathinstruct = (load_dataset("TIGER-Lab/MathInstruct", streaming=True, split="train")
                        .shuffle(buffer_size=5000, seed=42)
                        .map(_wrap_mathinstruct))

        stack = (load_dataset("bigcode/the-stack-v2-train-smol-ids",
                              streaming=True, split="train")
                 .shuffle(buffer_size=5000, seed=42))

        tier2 = interleave_datasets([openhermes, slimorca, mathinstruct])
        return [fineweb, tier2, stack]

    def _extract_text(self, example):
        """Pull text string out of a dataset example (handles all schema variants)."""
        text = example.get("text") or example.get("content") or ""
        if not text:
            parts = []
            for msg in example.get("conversations", []):
                parts.append(f"{msg.get('from', '')}: {msg.get('value', '')}")
            text = "\n".join(parts)
        return text

    def _local_reasoning_cycle(self):
        """Infinite cycle of hand-written reasoning texts."""
        while True:
            texts = list(self.local_reasoning_texts)
            random.shuffle(texts)
            yield from texts

    def __iter__(self):
        from datasets import interleave_datasets

        sources = self._build_sources()
        mixed = interleave_datasets(
            sources,
            probabilities=list(self.weights),
            seed=42,
            stopping_strategy="all_exhausted",
        )

        reasoning_cycle = self._local_reasoning_cycle()
        inject_every = 3   # inject 1 reasoning example every N web examples

        buffer = []
        web_count = 0
        for example in mixed:
            # Periodically inject hand-written reasoning as format anchor
            if self.local_reasoning_texts and web_count % inject_every == 0:
                r_text = next(reasoning_cycle)
                r_ids = self.tokenizer.encode(r_text, add_special_tokens=True)
                buffer.extend(r_ids)

            text = self._extract_text(example)
            if text:
                ids = self.tokenizer.encode(text, add_special_tokens=True)
                buffer.extend(ids)
                web_count += 1

            # Yield packed sequences of exactly max_seq_len
            while len(buffer) >= self.max_seq_len:
                yield buffer[:self.max_seq_len]
                buffer = buffer[self.max_seq_len:]


def make_streaming_dataloader(tokenizer, local_reasoning_texts=None,
                              batch_size: int = 32, max_seq_len: int = 1024):
    """DataLoader for NanoCloud streaming training."""
    dataset = WeightedMixDataset(tokenizer, local_reasoning_texts, max_seq_len)

    def _collate(batch):
        # batch is a list of token-ID lists of identical length (max_seq_len)
        tensors = [torch.tensor(seq, dtype=torch.long) for seq in batch]
        inputs  = torch.stack([t[:-1] for t in tensors])
        targets = torch.stack([t[1:]  for t in tensors])
        return inputs, targets

    return DataLoader(
        dataset,
        batch_size=batch_size,
        collate_fn=_collate,
        num_workers=0,
    )



# Streaming datasets: HuggingFace datasets with interleave_datasets for weighted mixing
