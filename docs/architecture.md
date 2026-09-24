# Model architecture

`model.py` defines one decoder-only transformer implementation. `TinyClaudeConfig` and `NanoCloudConfig` choose different sizes for it. Both configurations use token embeddings, a stack of pre-normalized attention and feed-forward blocks, a final layer normalization, and an output projection tied to the input embedding weights.

Each attention block projects the hidden state to queries, keys, and values. Rotary position embeddings are applied to queries and keys. During training, scaled dot-product attention uses a causal mask. During incremental generation, the block appends new keys and values to the cache and attends over the accumulated sequence. The feed-forward path uses SwiGLU, followed by a projection back to the embedding width.

`TinyClaude2.forward` returns `(logits, present_kvs)`. The logits have shape `[batch, tokens, vocab_size]`; `present_kvs` holds one key/value pair per transformer block. `generate.py` feeds those cached values into later decoding steps. The cache avoids recomputing projections for previous tokens, but it grows with the generated sequence. `RoPEEmbedding` precomputes positions only through `max_seq_len`, so prompts plus generated tokens must fit that limit.

Configuration validation in `config.py` checks that the embedding width divides evenly across heads, the layer and feed-forward counts are positive, and the configured sequence length is at least 16. These checks catch shape errors before model construction.
