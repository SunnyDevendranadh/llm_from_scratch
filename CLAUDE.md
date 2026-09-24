# TinyClaude — Project Context for Claude Code

## What This Project Is
A transformer-based language model built **completely from scratch** in Python/PyTorch.
Same architecture as GPT/Claude, just smaller. Built as a learning project — every component
was written by hand with no pretrained weights.

The model features a `<THINK>` reasoning token system that forces it to reason
before answering, similar to Claude's extended thinking.

---

## Project Structure
```
tinyclaude/
├── CLAUDE.md                  ← you are here
├── tokenizer.py               ← TinyClaudeTokenizer2 class
├── model.py                   ← TinyClaude, TinyClaudeEmbedding,
│                                 TinyClaudeAttention, TinyClaudeBlock
├── dataset.py                 ← TinyClaudeDataset, collate_fn
├── train.py                   ← training loop, scheduler, optimizer
├── generate.py                ← generate_v2(), SmartMemory, chat interface
├── data/
│   ├── reasoning_data.py      ← 56 hand-written reasoning examples
│   ├── chain_of_thought.py    ← 22 multi-step reasoning examples
│   └── math_data.py           ← make_math_examples() — auto-generated
├── checkpoints/
│   ├── tinyclaude_smart.pt    ← best model checkpoint (full save)
│   └── tinyclaude_final.pt    ← previous best
└── notebooks/
    └── tinyclaude_colab.ipynb ← original Google Colab notebook
```

---

## Architecture — Every Component

### Hyperparameters (current best)
```python
VOCAB_SIZE    = 5000
EMBED_DIM     = 256
NUM_HEADS     = 8
NUM_LAYERS    = 6
FF_DIM        = 1024
MAX_SEQ_LEN   = 256
DROPOUT       = 0.1
LEARNING_RATE = 3e-4
BATCH_SIZE    = 64
```

### Model Components (in order of data flow)

**1. TinyClaudeTokenizer2** (`tokenizer.py`)
- Word-level tokenizer with special token preservation
- Inherits from `TinyClaudeTokenizer`, overrides `clean_text()`
- Critical: uses placeholder swap to preserve `<THINK>` / `</THINK>` through cleaning
- Special tokens: `<PAD>=0, <UNK>=1, <BOS>=2, <EOS>=3, <THINK>=4, </THINK>=5`
- Bug we fixed: original `clean_text()` stripped `<>` symbols, destroying special tokens

**2. TinyClaudeEmbedding** (`model.py`)
- Word embeddings: `nn.Embedding(vocab_size, embed_dim)`
- Position embeddings: `nn.Embedding(max_seq_len, embed_dim)`
- Adds both together — each token vector contains meaning + position
- Dropout: 0.1

**3. TinyClaudeAttention** (`model.py`)
- Multi-head self-attention with causal masking
- Q, K, V projections: `nn.Linear(embed_dim, embed_dim)` × 3
- head_dim = embed_dim // num_heads = 32
- Causal mask via `torch.triu(..., diagonal=1)` — prevents future token peeking
- Scaled by `1/sqrt(head_dim)` — from "Attention is All You Need" paper
- Output projection combines all heads back

**4. TinyClaudeBlock** (`model.py`)
- Pre-norm transformer block (normalize BEFORE attention — modern style)
- Flow: `norm1 → attention → residual → norm2 → feedforward → residual`
- Feed forward: `Linear(256→1024) → GELU → Dropout → Linear(1024→256)`
- GELU activation (smoother than ReLU, used in GPT/Claude)
- Two residual connections prevent vanishing gradients

**5. TinyClaude** (`model.py`)
- Stacks: Embedding → 6× TransformerBlock → LayerNorm → OutputHead
- Weight tying: output_head.weight = embedding.word_embeddings.weight
- Weight init: normal(mean=0, std=0.02) for Linear/Embedding, zeros for bias

---

## Training History — What We Learned

| Version | Data | Vocab | Epochs | Perplexity | Notes |
|---------|------|-------|--------|------------|-------|
| v1 | 25 hand examples | 267 | 10 | 2723 | baseline |
| v2 | 56 examples | 267 | 10 | 2723 | more data |
| v3 | 56 examples | 487 | 50 | 45 | more epochs |
| v4 | 56 examples | 487 | 150 | 2.9 | best small |
| v5 | wiki 5k + math | 487 | 30 | 9.7 | added Wikipedia |
| v6 | wiki 5k + math + reasoning | 487 | 40 | 3.5 | **math works!** |
| v7 (bad) | wiki 50k | 8000 | 50 | 15.4 | reasoning drowned out |
| v8 (smart) | wiki 8k balanced | 5000 | 100 | TBD | current |

### Key Lessons Learned
1. **Special token bug**: `clean_text()` was stripping `<THINK>` tags → model never learned reasoning format
2. **Data balance matters more than data size**: 40k wiki + 460 reasoning = model forgot to reason
3. **Reasoning data needs 30%+ of training mix** to not get drowned out
4. **Perplexity 15 with bad mix > perplexity 3 with good mix** — lower isn't always better if reasoning breaks
5. **Two-phase training**: high LR broad learning → low LR fine-tuning

### Current Best Data Mix (Smart Strategy)
```python
wiki_smart      = 8,000   # Wikipedia chunks (background knowledge)
reasoning_smart = 2,240   # 56 examples × 40 (format learning)
chain_smart     = 1,100   # 22 examples  × 50 (deep reasoning)
math_smart      = 1,140   # 570 examples × 2  (arithmetic)
# Reasoning = ~35% of total — critical ratio!
```

---

## Key Classes and Functions

### Generation (`generate.py`)
```python
def generate_v2(model, tokenizer, prompt,
                max_new_tokens=100,
                temperature=0.7,
                top_k=30):
    # Top-k sampling with temperature
    # Returns dict: {thinking, answer, full}
    # Only decodes NEW tokens — prompt not repeated in output
    # Parses <THINK>...</THINK> tags automatically
```

### Memory (`generate.py`)
```python
class SmartMemory:
    # max_turns=3 — more than this confuses small models
    # Stores (question, short_answer) pairs
    # get_prompt(): "previously {last_answer} now {question}"
    # Key insight: only use LAST turn as context, not full history
```

### Dataset (`dataset.py`)
```python
class TinyClaudeDataset(Dataset):
    # Input  = tokens[:-1]  (all except last)
    # Target = tokens[1:]   (shifted by 1)
    # This is next-token prediction — standard LM training

def collate_fn(batch):
    # Pads shorter sequences with 0 (<PAD>)
    # Target padding uses -100 (CrossEntropyLoss ignores this)
```

---

## Current Capabilities

### Works well ✅
- Basic to intermediate arithmetic (addition, subtraction, multiplication)
- Word problems with clear structure
- Science questions (sky, gravity, water, photosynthesis, moon)
- History questions (Shakespeare, WWII, Apollo 11)
- Geography from training data (oceans, continents, mountains)
- Self-identification (name, capabilities)
- `<THINK>` reasoning before answering

### Known limitations ❌
- Questions far outside training distribution → hallucination
- Multi-turn memory is fragile (small models get confused by long context)
- No real-time information (knowledge cutoff = training data)
- Math with large numbers can still fail
- Invented facts sound confident — no uncertainty calibration

---

## How to Run Locally

### Setup
```bash
pip install torch numpy matplotlib datasets
```

### Quick start
```python
import torch
from model import TinyClaude
from tokenizer import TinyClaudeTokenizer2
from generate import generate_v2, SmartMemory

# Load checkpoint
device = "cuda" if torch.cuda.is_available() else "cpu"
ckpt   = torch.load('checkpoints/tinyclaude_smart.pt', map_location=device)

# Rebuild tokenizer
tokenizer = TinyClaudeTokenizer2()
tokenizer.word_to_id = ckpt['tokenizer_word_to_id']
tokenizer.id_to_word = ckpt['tokenizer_id_to_word']
tokenizer.vocab_size = ckpt['vocab_size']

# Rebuild model
cfg   = ckpt['config']
model = TinyClaude(
    vocab_size  = tokenizer.vocab_size,
    embed_dim   = cfg['embed_dim'],
    num_heads   = cfg['num_heads'],
    num_layers  = cfg['num_layers'],
    ff_dim      = cfg['ff_dim'],
    max_seq_len = cfg['max_seq_len'],
).to(device)
model.load_state_dict(ckpt['model_state_dict'])
model.eval()

# Chat
result = generate_v2(model, tokenizer, "what is gravity")
print(result['thinking'])
print(result['answer'])
```

### Training from scratch
```bash
python train.py --epochs 100 --wiki-articles 8000 --batch-size 64
```

---

## What Claude Code Should Know

### When editing model.py
- `TinyClaudeAttention.forward()` expects `x` shape: `[batch, seq_len, embed_dim]`
- Causal mask must be regenerated each forward pass (seq_len varies)
- Weight tying line must come AFTER both layers are defined
- `contiguous()` call before `view()` in attention is required — PyTorch memory layout

### When editing tokenizer.py
- `<THINK>` and `</THINK>` MUST survive `clean_text()` — use placeholder swap
- `build_vocab()` must be called before `encode()`/`decode()`
- `encode()` returns list of ints including BOS=2 and EOS=3
- `decode()` skips PAD, BOS, EOS but KEEPS `<THINK>` and `</THINK>`

### When editing train.py
- `collate_fn` uses `-100` for padding targets — CrossEntropyLoss `ignore_index=-100`
- `clip_grad_norm_(model.parameters(), 1.0)` — always keep this, prevents explosions
- `OneCycleLR` steps every BATCH not every epoch — call inside inner loop
- Save checkpoint with FULL dict (model + tokenizer + config) not just state_dict

### When editing generate.py
- `model.eval()` before generation — disables dropout
- `torch.no_grad()` — saves memory during inference
- Only decode `generated[prompt_len:]` — not the full sequence
- Temperature < 0.5 = repetitive, Temperature > 1.2 = incoherent, sweet spot = 0.7

### Data mixing rules (CRITICAL)
- Reasoning/chain-of-thought must be ≥ 30% of training data
- If Wikipedia dominates, model learns facts but loses reasoning format
- Repeat small datasets (×20 to ×50) rather than using raw counts
- Always verify `<THINK>` survives tokenization before training

---

## Next Improvement Ideas

### Easy wins (1-2 hours)
- Add division examples to math data
- Add more geography chain-of-thought examples
- Increase reasoning repeat multiplier to 60×

### Medium (half day)
- Implement beam search in `generate_v2()` for better outputs
- Add temperature annealing during generation
- Train on QA-format Wikipedia (question → answer pairs)

### Hard (multi-day)
- Implement RLHF-style feedback loop
- Add retrieval-augmented generation (RAG) for factual accuracy
- Scale to EMBED_DIM=512, NUM_LAYERS=8 with paid GPU

### Architecture upgrades
- Replace learned position embeddings with RoPE (Rotary Position Embedding)
- Add grouped-query attention (more efficient multi-head)
- Implement KV-cache for faster generation

---

## Parameter Count Reference
```
Current model (embed=256, heads=8, layers=6, vocab=5000):
  Embedding layer : ~1,280,000 params
  6× Transformer  : ~5,000,000 params
  Output head     : tied (free)
  TOTAL           : ~6,280,000 params

For reference:
  GPT-2 Small  : 117,000,000
  GPT-2 Medium : 345,000,000
  Real Claude  : ~100,000,000,000+
```

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `<UNK>` everywhere in output | Vocab mismatch between tokenizer versions | Always reload tokenizer from same checkpoint |
| `RuntimeError: view size not compatible` | Forgot `contiguous()` before `view()` | Add `.contiguous()` after `.transpose()` |
| Loss stays flat at log(vocab_size) | Special tokens not in vocab | Check `<THINK>` id in word_to_id |
| Gibberish after memory context | Memory context too long | Limit to 1 previous turn for small models |
| CUDA out of memory | Batch too large | Reduce batch_size, add `torch.cuda.empty_cache()` |
| Perplexity goes up with more data | Data imbalance | Ensure reasoning ≥ 30% of training mix |
