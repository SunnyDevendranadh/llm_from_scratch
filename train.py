"""
Training script — supports both TinyClaude2 (epoch-based) and NanoCloud (step-based).

TinyClaude2 (local, MPS/CPU):
    python train.py
    python train.py --phase1-epochs 5
    python train.py --resume checkpoints/tinyclaude2_best.pt

NanoCloud (vast.ai GPU, streaming HuggingFace datasets):
    python train.py --nanocloud
    python train.py --nanocloud --resume checkpoints/nanocloud_step2000.pt
    python train.py --nanocloud --max-steps 76294 --checkpoint-every 2000
"""

import argparse
import math
import os
import random
import threading
import time

import torch
import torch.nn as nn
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import LambdaLR

from config import TinyClaudeConfig, NanoCloudConfig
from dataset import make_dataloader, make_streaming_dataloader
from model import TinyClaude2
from tokenizer import TinyClaudeTokenizer2, NanoCloudTokenizer

from data.reasoning_data import reasoning_data
from data.chain_of_thought import chain_of_thought_data
from data.instruction_data import instruction_data
from data.math_data import make_math_examples


# ---------------------------------------------------------------------------
# Device selection
# ---------------------------------------------------------------------------
def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ---------------------------------------------------------------------------
# Wikipedia data helpers (TinyClaude2 mode)
# ---------------------------------------------------------------------------
def load_wiki_chunks(num_articles: int = 8000, chunk_size: int = 64):
    """Stream Wikipedia and split into word-level chunks."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("WARNING: 'datasets' not installed — skipping Wikipedia.")
        return []

    print(f"Downloading {num_articles} Wikipedia articles...")
    wiki = load_dataset(
        "wikimedia/wikipedia", "20231101.en",
        split="train", streaming=True
    )
    articles = []
    for i, article in enumerate(wiki):
        if i >= num_articles:
            break
        articles.append(article["text"][:2000])
        if i % 2000 == 0 and i > 0:
            print(f"  Downloaded {i} articles...")

    print(f"Splitting {len(articles)} articles into chunks...")
    chunks = []
    for text in articles:
        words = text.lower().split()
        for i in range(0, len(words) - chunk_size + 1, chunk_size // 2):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk) > 20:
                chunks.append(chunk)

    print(f"Wikipedia chunks: {len(chunks)}")
    return chunks


# ---------------------------------------------------------------------------
# Data mixing (TinyClaude2 mode)
# ---------------------------------------------------------------------------
def build_training_data(cfg: TinyClaudeConfig, wiki_articles: int = 8000,
                        phase2: bool = False):
    """Build the smart training mix. phase2=True omits Wikipedia."""
    math_examples = make_math_examples()

    if phase2:
        data = (
            reasoning_data * 40
            + chain_of_thought_data * 50
            + instruction_data * 40
            + math_examples * 2
        )
        random.shuffle(data)
        print(f"Phase-2 data: {len(data)} examples (reasoning-only)")
        return data

    wiki = load_wiki_chunks(wiki_articles)

    reasoning_rep   = reasoning_data        * 40
    chain_rep       = chain_of_thought_data * 50
    instruction_rep = instruction_data      * 40
    math_rep        = math_examples         * 3

    wiki_sample = random.sample(wiki, min(8000, len(wiki))) if wiki else []
    data = wiki_sample + reasoning_rep + chain_rep + instruction_rep + math_rep
    random.shuffle(data)

    total = len(data)
    reasoning_total = len(reasoning_rep) + len(chain_rep) + len(instruction_rep)
    print(f"\nTraining data mix:")
    print(f"  Wikipedia        : {len(wiki_sample):,}  ({len(wiki_sample)/total*100:.0f}%)")
    print(f"  Reasoning (×40)  : {len(reasoning_rep):,}  ({len(reasoning_rep)/total*100:.0f}%)")
    print(f"  Chain-of-thought : {len(chain_rep):,}  ({len(chain_rep)/total*100:.0f}%)")
    print(f"  Instruction (×40): {len(instruction_rep):,}  ({len(instruction_rep)/total*100:.0f}%)")
    print(f"  Math (×3)        : {len(math_rep):,}  ({len(math_rep)/total*100:.0f}%)")
    print(f"  TOTAL            : {total:,}")
    print(f"  Reasoning share  : {reasoning_total/total*100:.0f}% (target ≥30%)")
    return data


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------
def save_checkpoint(model, tokenizer, cfg, path, step_or_epoch, loss):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    is_nano = isinstance(cfg, NanoCloudConfig)
    payload = {
        "model_state_dict": model.state_dict(),
        "config": {
            "embed_dim":   cfg.embed_dim,
            "num_heads":   cfg.num_heads,
            "num_layers":  cfg.num_layers,
            "ff_dim":      cfg.ff_dim,
            "max_seq_len": cfg.max_seq_len,
            "model_class": "NanoCloud" if is_nano else "TinyClaude2",
        },
        "loss": loss,
    }
    if is_nano:
        # NanoCloud: tokenizer is a file path
        tok_path = path.replace(".pt", "_tokenizer.json")
        tokenizer.save(tok_path)
        payload["tokenizer_path"] = tok_path
        payload["vocab_size"] = tokenizer.vocab_size
        payload["global_step"] = step_or_epoch
    else:
        payload["tokenizer_word_to_id"] = tokenizer.word_to_id
        payload["tokenizer_id_to_word"] = tokenizer.id_to_word
        payload["vocab_size"] = tokenizer.vocab_size
        payload["epoch"] = step_or_epoch

    torch.save(payload, path)
    tag = f"step {step_or_epoch}" if is_nano else f"epoch {step_or_epoch}"
    print(f"  Saved checkpoint: {path} ({tag}, loss {loss:.4f})")
    return path


def _upload_async(local_path, step, repo_id):
    """Fire-and-forget HuggingFace Hub upload (runs in daemon thread)."""
    try:
        from huggingface_hub import HfApi
        HfApi().upload_file(
            path_or_fileobj=local_path,
            path_in_repo=os.path.basename(local_path),
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"  HF upload complete: step {step}")
    except Exception as e:
        print(f"  HF upload failed (non-fatal): {e}")


def load_checkpoint(path, device):
    print(f"Loading checkpoint: {path}")
    return torch.load(path, map_location=device)


# ---------------------------------------------------------------------------
# LR scheduler
# ---------------------------------------------------------------------------
def cosine_with_warmup(optimizer, warmup_steps: int, total_steps: int,
                       min_lr: float, base_lr: float) -> LambdaLR:
    def lr_lambda(step):
        if step < warmup_steps:
            return step / max(1, warmup_steps)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return max(min_lr / base_lr, 0.5 * (1 + math.cos(math.pi * progress)))
    return LambdaLR(optimizer, lr_lambda)


# ---------------------------------------------------------------------------
# TinyClaude2 training loop (epoch-based)
# ---------------------------------------------------------------------------
def train_phase(model, dataloader, optimizer, scheduler, loss_fn,
                epochs, device, grad_accum, phase_name=""):
    best_loss = float("inf")
    best_state = None

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        n_batches = 0
        t0 = time.time()

        optimizer.zero_grad()

        for step, (inputs, targets) in enumerate(dataloader):
            inputs  = inputs.to(device)
            targets = targets.to(device)

            logits, _ = model(inputs)
            loss = loss_fn(
                logits.view(-1, logits.size(-1)),
                targets.view(-1)
            ) / grad_accum

            loss.backward()

            if (step + 1) % grad_accum == 0 or (step + 1) == len(dataloader):
                clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

            epoch_loss += loss.item() * grad_accum
            n_batches += 1

        avg_loss = epoch_loss / n_batches
        ppl = math.exp(min(avg_loss, 20))
        elapsed = time.time() - t0

        print(f"{phase_name} Epoch {epoch+1:3d}/{epochs} | "
              f"loss={avg_loss:.4f} ppl={ppl:.1f} | {elapsed:.0f}s")

        if avg_loss < best_loss:
            best_loss = avg_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}

    return best_state, best_loss


# ---------------------------------------------------------------------------
# NanoCloud training loop (step-based, mixed precision, streaming)
# ---------------------------------------------------------------------------
def train_nanocloud(model, cfg: NanoCloudConfig, tokenizer, device,
                    checkpoint_dir: str, resume_step: int = 0,
                    hf_repo_id: str = None):
    """
    Step-based training loop for NanoCloud.
    - bfloat16 mixed precision (no GradScaler needed)
    - torch.compile for ~20-30% speedup
    - Cosine LR with warmup
    - Step-level checkpointing + optional async HF Hub upload
    - CSV loss log
    """
    math_examples = make_math_examples()
    local_reasoning = (
        reasoning_data * 40
        + chain_of_thought_data * 50
        + instruction_data * 40
        + math_examples * 3
    )
    print(f"Local reasoning anchor: {len(local_reasoning)} examples")

    dataloader = make_streaming_dataloader(
        tokenizer, local_reasoning,
        batch_size=cfg.batch_size,
        max_seq_len=cfg.max_seq_len,
    )

    use_cuda = device.type == "cuda"

    # torch.compile — training only; do NOT compile for inference (KV-cache dynamic shapes)
    if use_cuda:
        print("Compiling model with torch.compile()...")
        compiled_model = torch.compile(model)
    else:
        compiled_model = model

    loss_fn = nn.CrossEntropyLoss(ignore_index=-100, label_smoothing=cfg.label_smoothing)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
        betas=(0.9, 0.95),
    )
    scheduler = cosine_with_warmup(
        optimizer,
        warmup_steps=cfg.warmup_steps,
        total_steps=cfg.max_train_steps,
        min_lr=cfg.min_lr,
        base_lr=cfg.learning_rate,
    )

    # Fast-forward scheduler if resuming
    if resume_step > 0:
        for _ in range(resume_step):
            scheduler.step()

    os.makedirs(checkpoint_dir, exist_ok=True)
    log_file = open(os.path.join(checkpoint_dir, "loss_log.csv"), "a", buffering=1)
    if resume_step == 0:
        log_file.write("step,loss,ppl,grad_norm,lr\n")

    global_step = resume_step
    accum_loss = 0.0
    optimizer.zero_grad()
    t0 = time.time()

    print(f"\nNanoCloud training: steps {global_step} → {cfg.max_train_steps}")
    print(f"  batch={cfg.batch_size}, seq={cfg.max_seq_len}, accum={cfg.grad_accum_steps}")
    print(f"  effective batch = {cfg.batch_size * cfg.max_seq_len * cfg.grad_accum_steps:,} tokens")

    data_iter = iter(dataloader)
    micro_step = 0

    while global_step < cfg.max_train_steps:
        compiled_model.train()

        try:
            inputs, targets = next(data_iter)
        except StopIteration:
            data_iter = iter(dataloader)
            inputs, targets = next(data_iter)

        inputs  = inputs.to(device)
        targets = targets.to(device)

        if use_cuda:
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits, _ = compiled_model(inputs)
                loss = loss_fn(logits.view(-1, logits.size(-1)),
                               targets.view(-1)) / cfg.grad_accum_steps
        else:
            logits, _ = compiled_model(inputs)
            loss = loss_fn(logits.view(-1, logits.size(-1)),
                           targets.view(-1)) / cfg.grad_accum_steps

        loss.backward()
        accum_loss += loss.item()
        micro_step += 1

        if micro_step % cfg.grad_accum_steps == 0:
            grad_norm = clip_grad_norm_(model.parameters(), 1.0)
            if grad_norm > 5.0:
                print(f"  WARNING: grad norm {grad_norm:.2f} at step {global_step}")

            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            global_step += 1
            avg_loss = accum_loss * cfg.grad_accum_steps  # unscale
            ppl = math.exp(min(avg_loss, 20))
            lr = scheduler.get_last_lr()[0]
            accum_loss = 0.0

            log_file.write(f"{global_step},{avg_loss:.4f},{ppl:.2f},{grad_norm:.3f},{lr:.6f}\n")

            if global_step % 100 == 0:
                elapsed = time.time() - t0
                tok_per_sec = (100 * cfg.batch_size * cfg.max_seq_len * cfg.grad_accum_steps) / elapsed
                print(f"  step {global_step:6d}/{cfg.max_train_steps} | "
                      f"loss={avg_loss:.4f} ppl={ppl:.1f} | "
                      f"lr={lr:.2e} gnorm={grad_norm:.2f} | "
                      f"{tok_per_sec:,.0f} tok/s")
                t0 = time.time()

            if global_step % cfg.checkpoint_every == 0:
                ckpt_path = os.path.join(checkpoint_dir,
                                         f"nanocloud_step{global_step}.pt")
                save_checkpoint(model, tokenizer, cfg, ckpt_path, global_step, avg_loss)
                # Async HF upload if repo configured
                if hf_repo_id:
                    threading.Thread(
                        target=_upload_async,
                        args=(ckpt_path, global_step, hf_repo_id),
                        daemon=True,
                    ).start()

    log_file.close()
    final_path = os.path.join(checkpoint_dir, "nanocloud_final.pt")
    save_checkpoint(model, tokenizer, cfg, final_path, global_step, avg_loss)
    print(f"\nTraining complete! Final checkpoint: {final_path}")
    return final_path


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Train TinyClaude2 or NanoCloud")
    parser.add_argument("--nanocloud", action="store_true",
                        help="Use NanoCloud config (138M, GPU streaming training)")

    # TinyClaude2 args
    parser.add_argument("--phase1-epochs", type=int, default=None)
    parser.add_argument("--phase2-epochs", type=int, default=None)
    parser.add_argument("--wiki-articles", type=int, default=8000)

    # Shared args
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints")

    # NanoCloud-only args
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--checkpoint-every", type=int, default=None)
    parser.add_argument("--hf-repo", type=str, default=None,
                        help="HuggingFace repo ID for async checkpoint upload")
    parser.add_argument("--tokenizer-path", type=str,
                        default="checkpoints/nanocloud_tokenizer.json",
                        help="Path to pre-trained NanoCloudTokenizer JSON")

    args = parser.parse_args()

    device = get_device()
    print(f"Device: {device}")

    random.seed(42)
    torch.manual_seed(42)

    # ══════════════════════════════════════════════════════════════════════
    # NANOCLOUD MODE
    # ══════════════════════════════════════════════════════════════════════
    if args.nanocloud:
        cfg = NanoCloudConfig()
        if args.max_steps is not None:
            cfg.max_train_steps = args.max_steps
        if args.checkpoint_every is not None:
            cfg.checkpoint_every = args.checkpoint_every

        print(f"\nNanoCloud config: embed={cfg.embed_dim} heads={cfg.num_heads} "
              f"layers={cfg.num_layers} ff={cfg.ff_dim} seq={cfg.max_seq_len}")

        # Load tokenizer (must be pre-trained with scripts/train_tokenizer.py)
        if not os.path.exists(args.tokenizer_path):
            print(f"ERROR: Tokenizer not found at {args.tokenizer_path}")
            print("Run: python scripts/train_tokenizer.py first")
            return

        print(f"Loading tokenizer from {args.tokenizer_path}...")
        tokenizer = NanoCloudTokenizer.load(args.tokenizer_path)
        print(f"Tokenizer loaded: {tokenizer.vocab_size} tokens")

        # Verify special tokens
        for tok in ["<THINK>", "</THINK>", "<ANSWER>"]:
            idx = tokenizer.word_to_id.get(tok, "MISSING")
            print(f"  {tok:12} → {idx}")

        # Build model
        resume_step = 0
        model = TinyClaude2(
            vocab_size  = tokenizer.vocab_size,
            embed_dim   = cfg.embed_dim,
            num_heads   = cfg.num_heads,
            num_layers  = cfg.num_layers,
            ff_dim      = cfg.ff_dim,
            max_seq_len = cfg.max_seq_len,
            dropout     = cfg.dropout,
        ).to(device)

        if args.resume:
            ckpt = load_checkpoint(args.resume, device)
            model.load_state_dict(ckpt["model_state_dict"])
            resume_step = ckpt.get("global_step", 0)
            print(f"Resumed from step {resume_step}")

        print(f"Parameters: {model.count_params():,}")

        try:
            train_nanocloud(
                model, cfg, tokenizer, device,
                checkpoint_dir=args.checkpoint_dir,
                resume_step=resume_step,
                hf_repo_id=args.hf_repo,
            )
        except KeyboardInterrupt:
            print("\nInterrupted! Saving emergency checkpoint...")
            emergency_path = os.path.join(
                args.checkpoint_dir, "nanocloud_interrupt.pt")
            save_checkpoint(model, tokenizer, cfg, emergency_path,
                            resume_step, 0.0)
            print(f"Emergency checkpoint saved to {emergency_path}")
        return

    # ══════════════════════════════════════════════════════════════════════
    # TINYCLAUDE2 MODE (epoch-based, local)
    # ══════════════════════════════════════════════════════════════════════
    cfg = TinyClaudeConfig()
    if args.phase1_epochs is not None:
        cfg.phase1_epochs = args.phase1_epochs
    if args.phase2_epochs is not None:
        cfg.phase2_epochs = args.phase2_epochs

    print("\nBuilding training data...")
    train_data = build_training_data(cfg, wiki_articles=args.wiki_articles)

    print("\nBuilding tokenizer...")
    tokenizer = TinyClaudeTokenizer2()

    ckpt = None
    if args.resume:
        ckpt = load_checkpoint(args.resume, device)
        tokenizer.word_to_id = ckpt["tokenizer_word_to_id"]
        tokenizer.id_to_word = ckpt["tokenizer_id_to_word"]
        tokenizer.vocab_size = ckpt["vocab_size"]
        print(f"Reusing tokenizer: {tokenizer.vocab_size} tokens")
    else:
        tokenizer.build_vocab(train_data, max_vocab=cfg.vocab_size)

    for tok in ["<THINK>", "</THINK>", "<ANSWER>"]:
        idx = tokenizer.word_to_id.get(tok, "MISSING")
        print(f"  {tok:12} → {idx}")

    print("\nBuilding model...")
    model = TinyClaude2(
        vocab_size  = tokenizer.vocab_size,
        embed_dim   = cfg.embed_dim,
        num_heads   = cfg.num_heads,
        num_layers  = cfg.num_layers,
        ff_dim      = cfg.ff_dim,
        max_seq_len = cfg.max_seq_len,
        dropout     = cfg.dropout,
    ).to(device)

    if ckpt is not None:
        model.load_state_dict(ckpt["model_state_dict"])
        print("Loaded weights from checkpoint.")

    print(f"Parameters: {model.count_params():,}")

    # Use max_seq_len=256 for local training (MPS/CPU speed)
    train_seq_len = min(cfg.max_seq_len, 256)
    dataloader = make_dataloader(
        train_data, tokenizer,
        batch_size=cfg.batch_size,
        max_seq_len=train_seq_len,
    )
    print(f"Dataloader: {len(dataloader)} batches/epoch (seq≤{train_seq_len})")

    loss_fn = nn.CrossEntropyLoss(ignore_index=-100, label_smoothing=cfg.label_smoothing)

    try:
        # ── PHASE 1 ──────────────────────────────────────────────────────────
        if cfg.phase1_epochs > 0:
            print(f"\n{'='*55}")
            print(f"PHASE 1: {cfg.phase1_epochs} epochs, LR={cfg.learning_rate}")
            print(f"{'='*55}")

            optimizer1 = torch.optim.AdamW(
                model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
            total_steps1 = math.ceil(len(dataloader) / cfg.grad_accum_steps) * cfg.phase1_epochs
            scheduler1 = torch.optim.lr_scheduler.OneCycleLR(
                optimizer1, max_lr=cfg.learning_rate,
                total_steps=total_steps1, pct_start=cfg.warmup_pct)

            best_state1, best_loss1 = train_phase(
                model, dataloader, optimizer1, scheduler1, loss_fn,
                cfg.phase1_epochs, device, cfg.grad_accum_steps, phase_name="[P1]")

            model.load_state_dict(best_state1)
            save_checkpoint(model, tokenizer, cfg,
                            f"{args.checkpoint_dir}/tinyclaude2_phase1.pt",
                            cfg.phase1_epochs, best_loss1)

        # ── PHASE 2 ──────────────────────────────────────────────────────────
        if cfg.phase2_epochs > 0:
            print(f"\n{'='*55}")
            print(f"PHASE 2: {cfg.phase2_epochs} epochs, LR={cfg.phase2_lr} (reasoning only)")
            print(f"{'='*55}")

            phase2_data = build_training_data(cfg, phase2=True)
            dataloader2 = make_dataloader(
                phase2_data, tokenizer,
                batch_size=cfg.batch_size, max_seq_len=train_seq_len)

            optimizer2 = torch.optim.AdamW(
                model.parameters(), lr=cfg.phase2_lr, weight_decay=cfg.weight_decay)
            total_steps2 = math.ceil(len(dataloader2) / cfg.grad_accum_steps) * cfg.phase2_epochs
            scheduler2 = torch.optim.lr_scheduler.OneCycleLR(
                optimizer2, max_lr=cfg.phase2_lr,
                total_steps=total_steps2, pct_start=cfg.warmup_pct)

            best_state2, best_loss2 = train_phase(
                model, dataloader2, optimizer2, scheduler2, loss_fn,
                cfg.phase2_epochs, device, cfg.grad_accum_steps, phase_name="[P2]")

            model.load_state_dict(best_state2)
            save_checkpoint(model, tokenizer, cfg,
                            f"{args.checkpoint_dir}/tinyclaude2_best.pt",
                            cfg.phase1_epochs + cfg.phase2_epochs, best_loss2)
    except KeyboardInterrupt:
        print("\nInterrupted! Saving emergency checkpoint...")
        emergency_path = os.path.join(
            args.checkpoint_dir, "tinyclaude2_interrupt.pt")
        # Use current model state (may be partial between epochs)
        save_checkpoint(model, tokenizer, cfg, emergency_path, 0, 0.0)
        print(f"Emergency checkpoint saved to {emergency_path}")

    print("\nTraining complete!")


if __name__ == "__main__":
    main()



# TODO: add Weights & Biases logging integration for remote training runs

# Resume logic: fast-forwards the scheduler to the correct step before continuing training

# Mixed precision: bfloat16 on CUDA gives ~2x speedup with no loss scaling needed
