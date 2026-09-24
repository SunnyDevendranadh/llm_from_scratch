# LLM from scratch

An experimental PyTorch project for training small decoder-only language models. `TinyClaude2` is the local training path; `NanoCloud` is the larger, step-based path for a GPU machine. Both use rotary position embeddings, SwiGLU feed-forward blocks, and a key/value cache for generation. The model and training loop live in this repository; trained weights are not included.

## Run it

Use Python 3.9 or newer. From the repository root:

```bash
python3 -m pip install -e .
python3 run.py --help
python3 -m unittest discover -s tests -p 'test_*.py'
```

The local training command below skips the Wikipedia download and runs one phase-one epoch. It still builds a model and trains on the bundled examples, so it can take time on a CPU.

```bash
python3 run.py train --phase1-epochs 1 --phase2-epochs 0 --wiki-articles 0
python3 run.py summary checkpoints/tinyclaude2_phase1.pt
```

For the full local path, run `python3 run.py train`. That path streams Wikipedia data and writes the phase-one and phase-two checkpoints under `checkpoints/`. After training, `python3 run.py chat --checkpoint checkpoints/tinyclaude2_best.pt` loads the phase-two checkpoint. The `nanocloud` command uses the larger configuration and needs a suitable GPU and its own tokenizer/data setup; see `VAST_TRAINING_GUIDE.md` for those steps.

## Where to look

- `config.py` defines and validates the two model configurations.
- `model.py` implements the decoder blocks, rotary embeddings, and cached attention.
- `tokenizer.py` contains the local word tokenizer and NanoCloud tokenizer.
- `dataset.py` builds batches and streaming data loaders.
- `train.py` handles training, gradient accumulation, and checkpoints.
- `generate.py` loads checkpoints and generates text.

The [architecture notes](docs/architecture.md) explain the model path, and the [gradient clipping notes](docs/gradient_clipping.md) describe where clipping happens in training.

This is a training experiment, not a released language model. Results depend on the data, hardware, and checkpoints you produce. Start with the short local run to verify the pipeline before using the larger configuration.
