#!/bin/bash
# NanoCloud vast.ai RTX 5090 setup script.
# Run once after instance creation before starting training.
#
# IMPORTANT: Set HF_TOKEN in vast.ai Dashboard → Instance → Env Vars.
# NEVER hardcode the token in this script.
#
# Usage:
#   bash scripts/vast_setup.sh
#   python scripts/train_tokenizer.py   # ~20 min
#   python scripts/benchmark.py         # verify >80k tok/sec
#   python train.py --nanocloud         # full training

set -e   # exit on first error

echo "=== NanoCloud vast.ai setup ==="
echo "PyTorch version check..."
python -c "import torch; print(f'  PyTorch: {torch.__version__}')"
python -c "import torch; print(f'  CUDA: {torch.version.cuda}')"
python -c "import torch; print(f'  GPU: {torch.cuda.get_device_name(0)}')"

echo ""
echo "Installing dependencies..."
pip install --quiet torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu128

pip install --quiet \
    transformers \
    datasets \
    tokenizers \
    numpy \
    matplotlib \
    tqdm \
    huggingface_hub

echo ""
echo "Installing FlashAttention-2..."
pip install flash-attn --no-build-isolation

echo ""
echo "Verifying bfloat16 + CUDA autocast..."
python -c "
import torch
x = torch.randn(2, 10, 768).cuda()
with torch.autocast('cuda', dtype=torch.bfloat16):
    y = x @ x.transpose(-1, -2)
    print(f'  autocast dtype: {y.dtype}')
assert y.dtype == torch.bfloat16, 'bfloat16 not active!'
print('  bfloat16: OK')
"

echo ""
echo "Verifying torch.compile..."
python -c "
import torch
m = torch.nn.Linear(768, 768).cuda()
m = torch.compile(m)
x = torch.randn(2, 10, 768).cuda()
with torch.autocast('cuda', dtype=torch.bfloat16):
    y = m(x)
print(f'  compile output dtype: {y.dtype}')
print('  torch.compile: OK')
"

echo ""
if [ -n "$HF_TOKEN" ]; then
    echo "Logging in to HuggingFace Hub..."
    huggingface-cli login --token "$HF_TOKEN"
else
    echo "WARNING: HF_TOKEN not set — skipping HuggingFace login."
    echo "  Set it in: vast.ai Dashboard → Instance → Env Vars"
fi

echo ""
echo "Creating checkpoints directory..."
mkdir -p checkpoints

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. python scripts/train_tokenizer.py   # ~20 min, saves checkpoints/nanocloud_tokenizer.json"
echo "  2. python scripts/benchmark.py          # verify throughput >80k tok/sec"
echo "  3. python train.py --nanocloud          # start full training (~55h for 20B tokens)"
echo ""
echo "Enable auto-snapshots in vast.ai Dashboard (every 4-6h) before starting training!"
