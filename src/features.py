"""DINOv2 feature extraction: CLS-token RTS and patch-token spatial maps."""

import numpy as np
import torch
from PIL import Image

STRETCH_MIN = 2000
STRETCH_MAX = 5500


def patch_to_pil(patch, stretch_min=STRETCH_MIN, stretch_max=STRETCH_MAX):
    """Convert a (H, W, 4) Sentinel-2 patch [B2,B3,B4,B8] into a stretched RGB PIL image."""
    rgb = patch[:, :, [2, 1, 0]]  # B4, B3, B2
    rgb_stretched = np.clip((rgb - stretch_min) / (stretch_max - stretch_min), 0, 1)
    return Image.fromarray((rgb_stretched * 255).astype(np.uint8))


def extract_feature(patch, model, processor, device):
    """CLS-token feature vector for a patch. Returns None if patch is None."""
    if patch is None:
        return None
    img = patch_to_pil(patch).resize((224, 224), Image.BILINEAR)
    inputs = processor(images=img, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()


def extract_patch_tokens(patch, model, processor, device):
    """Full patch-token grid (excludes CLS token), shape (N, D)."""
    img = patch_to_pil(patch).resize((224, 224), Image.BILINEAR)
    inputs = processor(images=img, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[0, 1:, :].cpu().numpy()


def cosine_distance(a, b):
    """1 - cosine similarity. Higher = more visually different. NaN if either is None."""
    if a is None or b is None:
        return np.nan
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


def compute_patch_heatmap(baseline_patch, pei_patch, model, processor, device):
    """Per-patch-token cosine distance grid between baseline and PEI-period patches."""
    tok_base = extract_patch_tokens(baseline_patch, model, processor, device)
    tok_pei = extract_patch_tokens(pei_patch, model, processor, device)

    dot = np.sum(tok_base * tok_pei, axis=1)
    norm_base = np.linalg.norm(tok_base, axis=1)
    norm_pei = np.linalg.norm(tok_pei, axis=1)
    dist = 1 - dot / (norm_base * norm_pei + 1e-8)

    grid_size = int(np.sqrt(len(dist)))
    return dist.reshape(grid_size, grid_size)