import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = os.path.join(HERE, "..", "source-prepped.png")

GAMMA = 0.7         # lower = brighter face
BG_LEVEL = 30       # darker than this = background (0-255)
MARGIN = 40

gray = cv2.cvtColor(np.array(Image.open(INP).convert("RGB")), cv2.COLOR_RGB2GRAY)

# mask: 1 on the subject, 0 on the black background (so noise never survives)
blur = cv2.GaussianBlur(gray, (0, 0), 4).astype(np.float32)
mask = np.clip((blur - BG_LEVEL) / 25.0, 0, 1)
mask = cv2.GaussianBlur(mask, (0, 0), 2)

# gentle contrast, then brighten mid-tones
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
tone = clahe.apply(cv2.bilateralFilter(gray, 7, 40, 7)).astype(np.float32) / 255.0
tone = tone ** GAMMA

out = (tone * mask * 255).astype(np.uint8)

# square crop around the subject, black padding
ys, xs = np.where(mask > 0.5)
side = max(xs.max() - xs.min(), ys.max() - ys.min()) + MARGIN * 2
cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
canvas = np.zeros((side, side), np.uint8)
x0, y0 = cx - side // 2, cy - side // 2
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1]

Image.fromarray(canvas).save(OUT)
print("wrote", OUT, canvas.shape)