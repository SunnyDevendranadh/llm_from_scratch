# NanoCloud Training on vast.ai — Complete Beginner Guide

## Overview

You'll do 4 things:
1. **Upload your code** to GitHub
2. **Rent a GPU** on vast.ai (~$22-30 for a full run)
3. **Run 4 commands** to set up and train
4. **Download the checkpoint** when done

Total time: ~55–60 hours of GPU time (you don't need to watch it — it runs overnight)

---

## PART 1: Upload Your Code to GitHub

This is how you get your code onto the GPU server.

### Step 1: Create a GitHub account
Go to github.com and create a free account if you don't have one.

### Step 2: Create a new repository
1. Click the **+** button (top right) → **New repository**
2. Name it: `nanocloud`
3. Set it to **Private** (your code stays private)
4. Click **Create repository**

### Step 3: Push your code from your Mac
Open Terminal on your Mac and run these commands one by one:

```bash
cd /Users/sunny/llm_from_scratch_project

git init
git add .
git add .gitignore 2>/dev/null || true
git commit -m "NanoCloud initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nanocloud.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

> **Note:** GitHub will ask for your username and password. Use your GitHub username and a **Personal Access Token** (not your regular password). To get one: GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → Generate new token → check "repo" → copy it.

### Step 4: Add a .gitignore to exclude junk files
Create a file called `.gitignore` in your project folder with this content:

```
checkpoints/
__pycache__/
*.pyc
.venv/
*.pt
loss_log.csv
```

This prevents uploading large checkpoint files (they won't fit on GitHub anyway).

---

## PART 2: Set Up vast.ai Account

### Step 1: Create account
Go to **vast.ai** and create an account. You'll need to add a credit card.

### Step 2: Add credits
Click **Billing** → Add $30 to start (the full 20B token run costs ~$22, so this covers you with buffer).

### Step 3: Set your HuggingFace token (needed to download training data)
1. Go to **huggingface.co** → create a free account if you don't have one
2. Click your avatar → Settings → Access Tokens → New token → name it "vast" → Role: **Read** → Create
3. Copy the token (starts with `hf_...`)

Back in vast.ai:
1. Click your avatar (top right) → **Account**
2. Find **API Keys** or **SSH Keys** section — for env vars you set these per-instance (explained below)

---

## PART 3: Rent a GPU on vast.ai

### Step 1: Find an RTX 5090
1. Go to **vast.ai** → click **Search** in the left sidebar
2. In the search filters:
   - **GPU:** type `RTX 5090` in the GPU filter
   - **Disk Space:** set minimum to **100 GB** (training data + checkpoints)
   - **CUDA:** 12.8 or higher
3. Look for instances around **$0.40–0.50/hour** — sort by price

### Step 2: Configure the instance before renting
Click **Rent** on an instance. A settings panel appears:

- **Disk:** Set to **100 GB minimum** (use the slider)
- **Docker image:** Keep the default (PyTorch image is fine) or use `pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel`
- **Environment Variables:** Click **+ Add** and add:
  ```
  Name: HF_TOKEN
  Value: hf_your_token_here
  ```
  (This is how the setup script logs in to HuggingFace without hardcoding your token)

Click **Rent** and wait ~2 minutes for it to start.

### Step 3: Connect to the instance
1. In vast.ai dashboard, your instance appears under **My Instances**
2. Click **Connect** → you'll see an SSH command like:
   ```
   ssh -p 12345 root@123.456.789.0
   ```
3. Open Terminal on your Mac and paste that command

You are now inside the GPU server. Everything from here runs on the server.

---

## PART 4: Get Your Code onto the Server

Once connected via SSH, run:

```bash
# Clone your code from GitHub
git clone https://github.com/YOUR_USERNAME/nanocloud.git
cd nanocloud
```

GitHub will ask for username + token again (same Personal Access Token from Part 1).

---

## PART 5: Setup — Run Once After Renting

This installs all dependencies and verifies the GPU works correctly.

```bash
bash scripts/vast_setup.sh
```

This takes about **5–10 minutes**. You'll see output like:
```
=== NanoCloud vast.ai setup ===
PyTorch version check...
  PyTorch: 2.6.0
  CUDA: 12.8
  GPU: NVIDIA GeForce RTX 5090
Installing dependencies...
Installing FlashAttention-2...
Verifying bfloat16 + CUDA autocast...
  autocast dtype: torch.bfloat16
  bfloat16: OK
Verifying torch.compile...
  torch.compile: OK
Logging in to HuggingFace Hub...
=== Setup complete ===
```

**If you see any errors**, paste them here and I'll help you fix them before proceeding.

---

## PART 6: Train the BPE Tokenizer

This builds the vocabulary your model will use. Run once, takes ~20 minutes.

```bash
python scripts/train_tokenizer.py
```

Expected output:
```
Training BPE tokenizer: vocab=32000, target=10,000,000 tokens
Streaming FineWeb-Edu...
  FineWeb-Edu: ~6,000,000 tokens seen so far
Streaming Wikipedia...
  Wikipedia: ~10,000,000 tokens seen total
Saved tokenizer to: checkpoints/nanocloud_tokenizer.json
Vocab size: 32000

Verifying special tokens...
  <THINK> → id 4: PASS
  </THINK> → id 5: PASS
  <ANSWER> → id 6: PASS

All checks passed. Tokenizer is ready for NanoCloud training.
```

**Critical:** All 3 must say PASS. If any say FAIL, do not proceed.

---

## PART 7: Benchmark (Verify GPU Speed)

This confirms FlashAttention and bfloat16 are working before committing to the full 55-hour run.

```bash
python scripts/benchmark.py
```

Expected output:
```
NanoCloud benchmark
  Model: embed=768 heads=12 layers=12 ff=3072
  Batch=32, seq=1024, steps=100
  torch.compile: enabled

  Parameters: 138,xxx,xxx

Verifying bfloat16...
  Output dtype: torch.bfloat16  (should be torch.bfloat16)

Warmup (10 steps)...
Benchmarking 100 steps...

Results:
  Throughput    :      100,000+ tok/sec
  10B tokens    :   27.8h  ($11.25)
  20B tokens    :   55.6h  ($22.50)

Throughput looks good. Recommended: aim for 20B tokens.

Token math check:
  max_train_steps=76294 × batch_tokens=262,144 = 20.0B tokens
```

**If throughput < 60,000 tok/sec:** Something is wrong. Check:
- Does `pip show flash-attn` show a version? If not: `pip install flash-attn --no-build-isolation`
- Re-run the benchmark

**If `Output dtype` is NOT `torch.bfloat16`:** The GPU doesn't support bfloat16. This shouldn't happen on RTX 5090.

---

## PART 8: Enable Auto-Snapshots (IMPORTANT — do this before training)

Auto-snapshots back up your GPU instance every few hours. If the instance crashes mid-training, you can restore from a snapshot instead of losing 40+ hours of training.

1. Go to vast.ai dashboard → **My Instances** → click your running instance
2. Find **Auto-snapshot** setting → set to **every 6 hours**
3. Click Save

> Your code also saves a checkpoint file every 2000 steps (~52 minutes), so you're doubly protected.

---

## PART 9: Start Training

```bash
python train.py --nanocloud
```

Training runs for ~55 hours. You'll see output every few steps:

```
NanoCloud training: 138M params, target 20.0B tokens (76294 steps)
Device: cuda | bfloat16: True | compile: True
Step     10/76294 | loss=10.8234 | ppl=50234 | lr=6.00e-06 | 98,234 tok/s
Step     20/76294 | loss=10.1234 | ppl=24891 | lr=1.20e-05 | 101,432 tok/s
...
Step   2000/76294 | loss=5.2341 | ppl=187  | lr=2.85e-04 | 99,871 tok/s
[Checkpoint saved: checkpoints/nanocloud_step2000.pt]
```

**What to expect:**
- First step is slow (torch.compile is compiling — takes 2–5 minutes)
- Loss starts very high (~10) and drops over thousands of steps
- By step 10,000: loss should be below 3.0
- By step 50,000: loss should be below 2.0

### Can I disconnect from SSH while it trains?

Yes! But you need to use `tmux` so training keeps running after you disconnect:

```bash
# Start a tmux session BEFORE running train.py
tmux new -s training

# Now run training inside tmux
python train.py --nanocloud

# To detach (training keeps running): press Ctrl+B, then D
# To reattach later: tmux attach -t training
```

Now you can close your laptop and training continues on the server.

---

## PART 10: Monitor Training (from your Mac)

### Check if it's still running
SSH back in and run:
```bash
tmux attach -t training
```

You'll see the live loss output. Press `Ctrl+B, D` to detach again without stopping it.

### Check the loss log
```bash
tail -20 checkpoints/loss_log.csv
```

Output:
```
step,epoch,loss,ppl,grad_norm,lr
10,0,10.8234,50234,2.341,0.000006
20,0,10.1234,24891,2.102,0.000012
...
```

### Check GPU usage
```bash
watch -n 5 nvidia-smi
```

You should see GPU at ~99% utilization. Press `Ctrl+C` to stop watching.

---

## PART 11: Download Your Checkpoint When Done

Training finishes automatically after 76,294 steps (~55 hours). The final checkpoint is at `checkpoints/nanocloud_step76294.pt` (or the last step it reached).

### Download to your Mac
Open a new Terminal window on your Mac (not SSH) and run:

```bash
# Replace the SSH details with your actual vast.ai connection info
scp -P 12345 root@123.456.789.0:/root/nanocloud/checkpoints/nanocloud_step76294.pt \
    /Users/sunny/llm_from_scratch_project/checkpoints/

# Also download the tokenizer (always needed alongside the checkpoint)
scp -P 12345 root@123.456.789.0:/root/nanocloud/checkpoints/nanocloud_step76294_tokenizer.json \
    /Users/sunny/llm_from_scratch_project/checkpoints/
```

The port number (`12345`) and IP come from your vast.ai dashboard Connect button.

### Test the downloaded model on your Mac
```python
from generate import load_model, generate_v3

model, tokenizer, device = load_model("checkpoints/nanocloud_step76294.pt")
result = generate_v3(model, tokenizer, "what is gravity")
print(result["thinking"])
print(result["answer"])
```

---

## PART 12: Stop the Instance When Done

**IMPORTANT:** vast.ai charges by the hour. Stop the instance after downloading your checkpoint.

1. Go to vast.ai → My Instances
2. Click **Stop** (not Delete — Stop saves your disk in case you need to go back)
3. Or click **Delete** if you're sure you have everything downloaded

---

## Quick Reference: All Commands in Order

```bash
# On vast.ai server (SSH):
git clone https://github.com/YOUR_USERNAME/nanocloud.git
cd nanocloud
bash scripts/vast_setup.sh          # ~10 min, run once
python scripts/train_tokenizer.py   # ~20 min, run once
python scripts/benchmark.py         # 2 min, verify >80k tok/sec
tmux new -s training                # create tmux session
python train.py --nanocloud         # ~55 hours
# Ctrl+B, D to detach

# If you need to resume after a crash:
python train.py --nanocloud --resume checkpoints/nanocloud_step2000.pt

# On your Mac (download):
scp -P PORT root@IP:/root/nanocloud/checkpoints/nanocloud_step76294.pt ./checkpoints/
scp -P PORT root@IP:/root/nanocloud/checkpoints/nanocloud_step76294_tokenizer.json ./checkpoints/
```

---

## What Could Go Wrong (and what to do)

| Problem | What it looks like | Fix |
|---|---|---|
| Loss stuck at 10+ after 5000 steps | No decrease at all | Check `<THINK>` tokens survived — run tokenizer verify command |
| OOM (out of memory) error | `CUDA out of memory` | Add `--batch-size 16` to the train command |
| Instance disconnected | tmux session gone | SSH back in, `tmux new -s training`, `python train.py --nanocloud --resume checkpoints/nanocloud_stepXXXX.pt` |
| Benchmark shows <60k tok/sec | `WARNING: Throughput below 60k` | Re-run `pip install flash-attn --no-build-isolation`, then benchmark again |
| HF_TOKEN not working | Dataset download fails with 401 error | Re-run `huggingface-cli login --token YOUR_TOKEN` manually |

---

If anything goes wrong at any step, paste the exact error message here and I'll fix it for you.
