# Gradient clipping

Both training paths in `train.py` call `clip_grad_norm_(model.parameters(), 1.0)` immediately before an optimizer step. The call scales gradients down when their combined norm exceeds 1.0. It does not change gradients whose norm is already below that threshold.

The local `train_phase` loop accumulates gradients over `grad_accum_steps` batches, then clips and steps the optimizer. The NanoCloud loop follows the same order. Clipping each microbatch separately would change the accumulated direction, so the call belongs at the optimizer boundary.

If a run still becomes unstable, inspect the loss and learning-rate schedule as well as the gradient norm. Clipping caps the update norm; it does not repair bad targets, non-finite losses, or an unsuitable learning rate.
