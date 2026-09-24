# Learning From This Project

## Who this is for

This document is for someone who vibe-coded this repo, wants to actually understand it, and does not want the explanation to sound like a research paper.

If you only remember one sentence, remember this:

This repo is a small educational language-model stack that teaches the core pipeline of modern LLMs: data -> tokenizer -> transformer -> training loop -> checkpoint -> generation.

It is not how ChatGPT or Claude are built at full production scale, but it is absolutely the right kind of toy system for learning the moving parts.

---

## The big picture in plain English

You built a tiny version of a frontier-model workflow.

The repo contains two closely related training paths:

1. `TinyClaude2`
   A smaller local model that can train on a laptop with MPS/CPU and uses a simple word-level tokenizer.

2. `NanoCloud`
   A larger GPU-focused version meant for `vast.ai`, with a BPE tokenizer and streaming web datasets.

Both paths use the same core transformer model class in [model.py](model.py). The difference is mostly:

1. model size
2. tokenizer type
3. where data comes from
4. how training is scheduled

That means this repo is really teaching you one idea twice:

"How do I build a transformer language model from scratch, first in a small understandable way, then in a more realistic GPU-training way?"

---

## What this repo is trying to imitate

At a high level, frontier models are built with this rough pipeline:

1. Collect lots of text
2. Turn text into tokens
3. Train a transformer to predict the next token
4. Save checkpoints during training
5. Run inference to generate responses
6. Add extra post-training, evaluation, alignment, and serving systems

This repo covers steps 1 through 5 well enough to teach the fundamentals.

It only lightly touches step 6.

---

## The most important mental model

An LLM is basically:

1. a compression system for patterns in text
2. trained by next-token prediction
3. implemented with a transformer

In dumb-simple language:

1. You feed it lots of examples of text.
2. It learns statistical patterns about what token should come next.
3. At inference time, it keeps guessing one next token at a time.
4. Those guesses form a sentence.

That is the whole game.

Everything else in the repo exists to make that work.

---

## The repo end-to-end

Here is the real flow of this project:

1. Create training text
   Files: [data/reasoning_data.py](data/reasoning_data.py), [data/chain_of_thought.py](data/chain_of_thought.py), [data/instruction_data.py](data/instruction_data.py), [data/math_data.py](data/math_data.py)

2. Build a tokenizer
   File: [tokenizer.py](tokenizer.py)

3. Convert text into training examples
   File: [dataset.py](dataset.py)

4. Build the transformer
   File: [model.py](model.py)

5. Train it
   File: [train.py](train.py)

6. Save checkpoints
   Folder: `checkpoints/`

7. Load checkpoint and generate answers
   Files: [generate.py](generate.py), [run.py](run.py)

8. Evaluate manually or with a simple test script
   File: [test_model.py](test_model.py)

9. For the bigger GPU run:
   Files: [scripts/vast_setup.sh](scripts/vast_setup.sh), [scripts/train_tokenizer.py](scripts/train_tokenizer.py), [scripts/benchmark.py](scripts/benchmark.py)

---

## The two model tracks in this repo

### Track 1: TinyClaude2

This is the easier one to understand first.

- Config lives in [config.py](config.py)
- Uses `TinyClaudeConfig`
- About `17,240,832` parameters
- Uses a word-level tokenizer
- Trains mostly on local hand-written and synthetic examples, plus some streamed Wikipedia
- Uses epoch-based training
- Saves checkpoints like `tinyclaude2_phase1.pt` and `tinyclaude2_best.pt`

This is the "learn the basics" path.

### Track 2: NanoCloud

This is the more realistic one.

- Config lives in [config.py](config.py)
- Uses `NanoCloudConfig`
- About `137,860,608` parameters
- Uses a byte-level BPE tokenizer
- Streams datasets from Hugging Face
- Uses step-based GPU training
- Is designed for `vast.ai`
- Can save checkpoints every N steps like `nanocloud_step2000.pt`

This is the "scale the same idea up" path.

---

## Stage 1: The data

## Why data matters

The model does not "know" things the way a human knows things.

It only sees examples and learns patterns from them.

So the shape of your data strongly controls the shape of your model.

That is one of the deepest lessons in this whole repo.

## Your local data sources

### 1. Hand-written reasoning data

File: [data/reasoning_data.py](data/reasoning_data.py)

- `77` examples
- Short question -> `<THINK>` -> `</THINK>` -> `<ANSWER>` format
- Tries to teach the model a visible "reason first, answer second" pattern

Example idea:

`question -> inner reasoning text -> final answer text`

Important note:

This is not the same thing as true hidden internal reasoning in frontier models.
It is a formatting trick that teaches the model to produce a reasoning-shaped response.

### 2. Chain-of-thought data

File: [data/chain_of_thought.py](data/chain_of_thought.py)

- `46` examples
- Longer multi-step reasoning
- Better for teaching structure than plain Q/A

### 3. Instruction data

File: [data/instruction_data.py](data/instruction_data.py)

- `40` examples
- Teaches the model to respond to "explain", "define", "describe", and similar prompts

### 4. Synthetic math data

File: [data/math_data.py](data/math_data.py)

- `1619` generated examples
- Programmatically creates arithmetic and percentage questions
- Useful because it cheaply creates many clean examples in a consistent format

This is a huge practical lesson:

When you do not have a massive dataset, synthetic data is one of the best tools you have.

## How the local mix works

In [train.py](train.py), the local training mix is intentionally repeated:

- reasoning data x40
- chain-of-thought data x50
- instruction data x40
- math data x3
- plus a sample of Wikipedia chunks

This repetition is not accidental.

It is trying to stop the model from forgetting how to reason.

Why?

Because if you drown a tiny model in generic text, it often becomes more fluent but less useful.

That is a miniature version of a real LLM training truth:

Data quality and data mixture often matter more than raw data quantity.

## The NanoCloud data mix

In [dataset.py](dataset.py), `WeightedMixDataset` streams:

1. FineWeb-Edu
2. OpenHermes + SlimOrca + MathInstruct
3. The Stack smol

with weights:

- `0.65` general educational text
- `0.25` reasoning / chat / math text
- `0.10` code text

Then it also injects local reasoning examples every few web examples as an anchor.

That anchor is important.

It tells you the author already learned this lesson:

"If I want the model to keep a specific response format, I need to keep feeding that format during training."

---

## Stage 2: The tokenizer

File: [tokenizer.py](tokenizer.py)

The tokenizer is the system that turns human text into integer IDs.

Models do not read words directly.
They read token IDs.

### TinyClaude tokenizer

`TinyClaudeTokenizer2` is word-level.

That means:

1. clean text
2. split into words
3. map each word to an integer

Special tokens:

- `<PAD>` = 0
- `<UNK>` = 1
- `<BOS>` = 2
- `<EOS>` = 3
- `<THINK>` = 4
- `</THINK>` = 5
- `<ANSWER>` = 6

The smart detail here is that `TinyClaudeTokenizer2` protects special tokens before cleaning text.

Why?

Because a naive cleaner would strip `<` and `>` and destroy your reasoning format.

This is one of the most educational bugs in the repo.

It looks tiny, but it completely changes whether the model can learn the intended structure.

### NanoCloud tokenizer

`NanoCloudTokenizer` is a byte-level BPE tokenizer using Hugging Face `tokenizers`.

That is much closer to what real systems do.

BPE idea in plain English:

1. start from small pieces
2. learn which character sequences appear often
3. merge them into reusable subword tokens

Why this matters:

Word-level tokenizers break badly on unknown words.
BPE tokenizers generalize better because they can break words into parts.

Example intuition:

- word-level: `"anthropic"` might become one unknown token
- BPE: `"anth" + "ropic"` or some other learned split

That is one reason the NanoCloud path is more realistic.

---

## Stage 3: The dataset and dataloader

File: [dataset.py](dataset.py)

This file turns tokenized text into the exact tensors the model needs for next-token prediction.

## The core training trick

Language modeling is trained like this:

- input: all tokens except the last one
- target: all tokens except the first one

If the sentence is:

`[BOS, what, is, gravity, EOS]`

then training pairs look like:

- input: `[BOS, what, is, gravity]`
- target: `[what, is, gravity, EOS]`

This teaches:

"Given everything so far, predict the next token."

That is the entire objective of a base language model.

## Local path

`TinyClaudeDataset`:

1. tokenizes each text
2. clips to max sequence length
3. stores token ID sequences

`collate_fn` pads batch items so tensors are the same length.

Important detail:

- input padding uses `0` which is `<PAD>`
- target padding uses `-100`

Why `-100`?

Because `CrossEntropyLoss(ignore_index=-100)` ignores those positions.

That means the model is not punished for predicting the padding area.

## NanoCloud path

`WeightedMixDataset` is an `IterableDataset`.

Instead of preloading everything, it streams data from Hugging Face.

Then it:

1. tokenizes incoming text
2. appends token IDs into a buffer
3. slices that buffer into fixed chunks of length `max_seq_len`

This is sequence packing.

It is an important practical idea because GPUs want dense, regular-shaped tensors.

---

## Stage 4: The model architecture

File: [model.py](model.py)

This is the heart of the repo.

Both TinyClaude2 and NanoCloud use the same transformer implementation: `TinyClaude2`.

That is a useful lesson too:

You do not need a completely different codebase to scale up.
Often you keep the same architecture pattern and change config, tokenizer, and training setup.

## The model at a high level

The flow is:

1. token IDs go into an embedding layer
2. embeddings go through repeated transformer blocks
3. final hidden states go through an output head
4. output head produces logits for the next token

In code terms:

`tokens -> embeddings -> blocks -> norm -> logits`

## Important components

### 1. Embedding layer

`nn.Embedding(vocab_size, embed_dim)`

This turns each token ID into a dense vector.

Simple analogy:

The tokenizer turns words into integer labels.
The embedding layer turns those labels into learned meaning vectors.

### 2. Attention

Class: `TinyClaude2Attention`

This is the core transformer mechanism.

Attention lets each token look at previous tokens and decide what matters.

That is how the model can connect:

- pronouns to earlier nouns
- math questions to earlier numbers
- later words to earlier instructions

The code creates:

- Q = query
- K = key
- V = value

You do not need to memorize the math immediately.
The intuition is enough:

Each token asks, "Which earlier tokens should I pay attention to?"

### 3. RoPE

Class: `RoPEEmbedding`

This is Rotary Position Embedding.

Transformers need some notion of order because words arrive in sequence.

RoPE gives attention layers a way to understand token position without using a classic learned position embedding table.

Why this matters:

Without positional information, the model would not know the difference between:

- `dog bites man`
- `man bites dog`

### 4. SwiGLU feed-forward

Class: `SwiGLUFFN`

After attention, each token passes through a feed-forward network.

This is where the model does a lot of local nonlinear processing.

The repo uses `SwiGLU`, which is more modern than a plain ReLU MLP and closer to the style used in better transformer architectures.

### 5. Transformer block

Class: `TinyClaude2Block`

Each block does:

1. layer norm
2. attention
3. residual connection
4. layer norm
5. feed-forward
6. residual connection

Residual connections are a huge deal.

They help gradients flow and make deep training possible.

### 6. Weight tying

In `TinyClaude2`, the output head weight is tied to the embedding weight.

That means the same matrix is reused for input embeddings and output token scoring.

This is common in language models because it saves parameters and often helps performance.

### 7. KV cache

The attention code and [generate.py](generate.py) support a KV cache.

This matters during generation.

Without a KV cache, each new token would recompute attention over the whole prompt from scratch.

With a KV cache, the model reuses earlier key/value states and only processes the newest token.

That makes autoregressive generation much faster.

---

## Stage 5: The configs

File: [config.py](config.py)

This file answers the question:

"How big is the model, and how do we train it?"

## TinyClaudeConfig

- vocab size: `8000`
- embed dim: `384`
- heads: `6`
- layers: `8`
- FF dim: `1024`
- max seq len: `512`
- batch size: `16`
- grad accumulation: `4`

This becomes a roughly `17.2M` parameter model.

## NanoCloudConfig

- vocab size: `32000`
- embed dim: `768`
- heads: `12`
- layers: `12`
- FF dim: `3072`
- max seq len: `1024`
- batch size: `32`
- grad accumulation: `8`
- max train steps: `76294`

This becomes a roughly `137.9M` parameter model.

## Why these numbers matter

These settings control:

1. memory use
2. speed
3. model capacity
4. training cost

Frontier labs obsess over these tradeoffs.

This repo gives you a simplified place to feel those tradeoffs directly.

---

## Stage 6: Training

File: [train.py](train.py)

This is the single most important file after `model.py`.

It contains two separate training flows.

## Training flow A: TinyClaude2

This is the local path.

### What happens

1. Build mixed training data
2. Build or restore tokenizer
3. Build model
4. Make dataloader
5. Train phase 1
6. Save `tinyclaude2_phase1.pt`
7. Train phase 2 on reasoning-only data
8. Save `tinyclaude2_best.pt`

### Why two phases?

Phase 1 is broad learning.
Phase 2 is targeted sharpening.

That is a miniature version of a real training pattern:

1. first learn lots of general patterns
2. then specialize on the behavior you care about

### What the loss is doing

The model outputs logits for every token position.

`CrossEntropyLoss` compares those logits to the correct next tokens.

If the correct next token gets low probability, loss goes up.
If it gets high probability, loss goes down.

That is the learning signal.

### Gradient accumulation

This repo uses gradient accumulation.

Simple meaning:

Instead of updating weights every mini-batch, it accumulates several mini-batches before stepping the optimizer.

Why do this?

Because it gives you a larger effective batch size without needing all that memory at once.

### Optimizer and scheduler

Local training uses:

- `AdamW`
- `OneCycleLR`

This is standard practical deep-learning plumbing.

You do not need to worship the exact optimizer name.
The important thing is understanding the role:

- optimizer changes weights
- scheduler changes learning rate over time

## Training flow B: NanoCloud

This is the bigger GPU path.

### What happens

1. Load a pretrained BPE tokenizer JSON
2. Build the larger model
3. Stream mixed datasets
4. Use bfloat16 autocast on CUDA
5. Optionally `torch.compile` the model
6. Train by global step instead of epoch
7. Save checkpoints every few thousand steps
8. Optionally upload checkpoints to Hugging Face in the background

### Why step-based instead of epoch-based?

When you stream giant web datasets, "one epoch" becomes fuzzy or impractical.

So you often train for a fixed number of steps or tokens instead.

That is much closer to real large-scale pretraining.

### Mixed precision

The NanoCloud path uses bfloat16 autocast.

Simple meaning:

Use smaller numerical formats where safe so training is faster and cheaper.

This is one of the main reasons modern LLM training is feasible on current hardware.

### `torch.compile`

The code compiles the model in GPU training mode.

This is a performance optimization.

The benchmark script exists partly to check that these speedups are actually happening.

---

## Stage 7: Checkpoints

Checkpoints are save files for model training.

Think of them as "save game" snapshots.

This repo saves:

1. model weights
2. config values
3. tokenizer data or tokenizer path
4. loss
5. training progress like epoch or global step

Why checkpoints matter:

1. resume after interruption
2. compare versions
3. run inference later
4. keep the best model instead of only the final one

This is exactly how serious training workflows behave, just at a smaller scale.

---

## Stage 8: Generation and chat

Files: [generate.py](generate.py), [run.py](run.py)

This is inference.

Inference means:

"The model is no longer learning. It is just generating."

## How generation works here

`generate_v3` does this:

1. encode prompt into token IDs
2. run prompt through model once to fill KV cache
3. repeatedly predict one next token
4. apply repetition penalty
5. apply temperature and top-k sampling
6. stop at EOS or max token count
7. decode tokens back into text

## Temperature

Lower temperature:

- safer
- more repetitive
- more predictable

Higher temperature:

- more creative
- more random
- more error-prone

## Top-k

Top-k means:

"Only sample from the k most likely next tokens."

That prevents total chaos.

## SmartMemory

`SmartMemory` keeps a tiny amount of previous conversation.

This is not true long-context memory.

It is a small prompt engineering trick that rewrites the next user question with a short bit of prior answer context.

That is useful to understand because many "memory" systems in AI products are actually extra prompt logic wrapped around the model.

---

## Stage 9: Evaluation

File: [test_model.py](test_model.py)

This script is a lightweight evaluation harness.

It is not a serious benchmark suite, but it teaches the right instinct:

Do not only look at training loss.
Actually ask the model questions and inspect the behavior.

This matters because a model can:

1. get better loss
2. become more fluent
3. still get worse at the behavior you care about

That is one of the most important practical truths in LLM work.

The project already hints at that in how it protects reasoning-heavy data mixture.

---

## The GPU helper scripts

### [scripts/vast_setup.sh](scripts/vast_setup.sh)

This is environment setup for GPU training.

It:

1. checks CUDA and GPU
2. installs PyTorch and dependencies
3. installs FlashAttention
4. verifies bfloat16
5. verifies `torch.compile`
6. optionally logs into Hugging Face

This file teaches a critical lesson:

Real ML work is not just model code.
It is also infrastructure and environment setup.

### [scripts/train_tokenizer.py](scripts/train_tokenizer.py)

This trains the BPE tokenizer for NanoCloud from:

1. FineWeb-Edu
2. Wikipedia

This is good repo design.

It separates tokenizer training from model training because tokenization is a distinct training stage.

### [scripts/benchmark.py](scripts/benchmark.py)

This measures tokens per second and estimates cost/time for training.

That is a very real pretraining concern.

At scale, you are constantly asking:

- how fast are we training?
- how much will it cost?
- are the performance optimizations actually active?

---

## What this project teaches correctly about real LLMs

This repo gets many important things right:

1. transformer-based autoregressive next-token prediction
2. tokenization as a separate design choice
3. model size controlled by config
4. data mixture matters a lot
5. sequence packing and padding matter
6. checkpoints are essential
7. inference uses sampling, not just argmax
8. GPU training needs mixed precision and throughput checks

If you understand those eight things deeply, you are already thinking much more like an actual LLM engineer.

---

## What this project does not cover yet

If your goal is "understand how ChatGPT or Claude are built for real", this repo is a strong start but not the full stack.

Missing or simplified pieces include:

1. distributed training across many GPUs/nodes
2. large-scale data filtering and deduplication
3. token-count accounting at massive scale
4. validation sets and serious eval suites
5. supervised fine-tuning at scale
6. preference tuning / RLHF / DPO / RLAIF
7. safety, refusal, policy, and red-teaming systems
8. retrieval systems
9. serving infrastructure and latency engineering
10. multimodal training
11. tool use
12. post-training for instruction-following quality

So the honest framing is:

This repo teaches the core pretraining skeleton, not the entire frontier-model company stack.

That is still extremely valuable.

---

## The single best way to read this repo

Read it in this order:

1. [LEARNING_FROM_THIS_PROJECT.md](LEARNING_FROM_THIS_PROJECT.md)
2. [config.py](config.py)
3. [tokenizer.py](tokenizer.py)
4. [dataset.py](dataset.py)
5. [model.py](model.py)
6. [train.py](train.py)
7. [generate.py](generate.py)
8. [run.py](run.py)
9. [test_model.py](test_model.py)
10. [scripts/train_tokenizer.py](scripts/train_tokenizer.py)
11. [scripts/benchmark.py](scripts/benchmark.py)

That order mirrors the real lifecycle of the system.

---

## A beginner-friendly glossary

### Token

A chunk of text turned into an integer ID.

### Tokenizer

The thing that converts text <-> token IDs.

### Vocabulary

The list of tokens the tokenizer knows about.

### Embedding

A learned vector representation of each token.

### Transformer

The neural-network architecture used here.

### Attention

The mechanism that lets each token focus on relevant previous tokens.

### RoPE

A method for encoding token position inside attention.

### Logits

Raw model scores for every possible next token.

### Softmax

Turns logits into probabilities.

### Loss

A number telling you how wrong the model was.

### Perplexity

A transformed version of loss that is often easier to discuss for language models.
Lower is usually better, but behavior still matters more than loss alone.

### Checkpoint

A saved training snapshot.

### Gradient

The signal showing how weights should change to reduce loss.

### Optimizer

The algorithm that updates weights using gradients.

### Learning rate

How big each weight update should be.

### Batch size

How many examples you process together before an update.

### Gradient accumulation

A way to simulate a larger batch size by accumulating gradients across smaller batches.

### Autoregressive generation

Generate one token at a time, feeding previous generated tokens back into the model.

---

## What to say if you interview at a frontier-model company

This project gives you real talking points.

You can truthfully say things like:

1. "I built and trained a transformer LM from scratch in PyTorch."
2. "I implemented tokenization, dataset packing, training loops, checkpointing, and inference."
3. "I worked with both a simple word-level tokenizer and a BPE tokenizer."
4. "I learned how data mixture affects model behavior, especially reasoning retention."
5. "I used gradient accumulation, learning-rate scheduling, mixed precision, and throughput benchmarking."
6. "I understand the difference between a small local training path and a larger streaming GPU-training path."

That is much stronger than saying "I used an API."

---

## What you should understand next

If you want to level up from this repo toward real LLM research/engineering, the next topics are:

1. attention math in detail
2. why next-token prediction creates useful world knowledge
3. BPE and SentencePiece tokenization
4. scaling laws
5. distributed training basics
6. instruction tuning and preference optimization
7. evaluation methodology
8. data curation and deduplication
9. inference optimization and serving

---

## Good "argue with the coding agent" questions

When you want to push a coding agent harder, ask questions like:

1. "What behavior are we optimizing for, and does the data mixture actually support it?"
2. "Why are these hyperparameters chosen, and what breaks if we double sequence length?"
3. "Is this tokenizer choice helping or hurting generalization?"
4. "What is the bottleneck: data quality, model size, or training duration?"
5. "Are we measuring the right thing, or only loss?"
6. "What failure modes should we expect from this architecture?"
7. "Which parts of this pipeline are toy simplifications versus real production practice?"

Those are high-value research/engineering questions.

---

## Final honest summary

This repo is best understood as:

An educational mini-LLM lab that teaches the real skeleton of language-model building, from raw text to tokenization to transformer training to checkpointed inference.

If you understand this repo deeply, you will not yet know everything a frontier-model engineer knows.

But you will understand the core machine much better than most people who only prompt APIs.

That is a real step toward doing serious model work.
