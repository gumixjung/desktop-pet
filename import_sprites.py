#!/usr/bin/env python3
"""Slice image.png + flood-fill remove background → sprites/ with transparency"""

from PIL import Image
import numpy as np
import os
from collections import deque

SRC = os.path.join(os.path.dirname(__file__), "image.png")
OUT = os.path.join(os.path.dirname(__file__), "sprites")
os.makedirs(OUT, exist_ok=True)


def remove_bg_floodfill(img: Image.Image, tolerance=40) -> Image.Image:
    """Flood-fill from all 4 edges to remove background."""
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    H, W = arr.shape[:2]
    visited = np.zeros((H, W), dtype=bool)
    mask    = np.zeros((H, W), dtype=bool)  # True = background

    # Background color = average of edge pixels
    edges = np.concatenate([
        arr[0,:,:3], arr[-1,:,:3],
        arr[:,0,:3], arr[:,-1,:3]
    ])
    bg = np.median(edges, axis=0).astype(np.int32)
    print(f"  Detected bg color: RGB{tuple(bg)}")

    def is_bg(r, c):
        return bool(np.abs(arr[r, c, :3].astype(np.int32) - bg).max() < tolerance)

    # Flood fill from all border pixels
    queue = deque()
    for c in range(W):
        if not visited[0, c]   and is_bg(0, c):   queue.append((0, c))
        if not visited[H-1, c] and is_bg(H-1, c): queue.append((H-1, c))
    for r in range(H):
        if not visited[r, 0]   and is_bg(r, 0):   queue.append((r, 0))
        if not visited[r, W-1] and is_bg(r, W-1): queue.append((r, W-1))

    while queue:
        r, c = queue.popleft()
        if visited[r, c]: continue
        visited[r, c] = True
        if is_bg(r, c):
            mask[r, c] = True
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < H and 0 <= nc < W and not visited[nr, nc]:
                    queue.append((nr, nc))

    arr[mask, 3] = 0  # set background pixels to transparent
    return Image.fromarray(arr, "RGBA")


img = Image.open(SRC).convert("RGBA")
W, H = img.size
fw   = W // 4
print(f"Loaded {W}x{H}, frame size {fw}x{H}")

for i in range(4):
    frame = img.crop((i*fw, 0, (i+1)*fw, H))
    frame = remove_bg_floodfill(frame)
    frame.save(os.path.join(OUT, f"walk_r_{i+1}.png"))
    frame.transpose(Image.FLIP_LEFT_RIGHT).save(os.path.join(OUT, f"walk_l_{i+1}.png"))
    print(f"  Saved walk_r_{i+1}.png + walk_l_{i+1}.png")

sit = remove_bg_floodfill(img.crop((0, 0, fw, H)))
sit.save(os.path.join(OUT, "sit_1.png"))
sit.save(os.path.join(OUT, "sit_2.png"))
print("Done!")
