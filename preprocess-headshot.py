#!/usr/bin/env python3
"""Photo-level preprocessing for the fastfetch banner pipeline.

Runs headshot.jpg through a levels adjustment (percentile autolevel anchored to
the head region, plus a mild shadow lift) and writes headshot-pre.jpg. This is
the recommended fix for the scattered/grainy ASCII render: the raw photo's
head-region contrast is healthy (p5-p95 span ~200), but the pipeline's
edge-blend darkens flat skin ~18% and the full-head crop adds dark hair/collar
pixels, so the face features compress into a narrow mid band that the ASCII
dither then renders as speckle. A levels+gamma pre-stretch widens that band so
the glyph coverage lands on denser characters.

The levels are computed from the SAME head mask the banner uses
(subject()/tone_lut() over PORTRAIT_CROP), so the stretch is anchored to the
face, not the background. It is applied to the photo's V channel only (HSV),
so hue/saturation are untouched.

Usage:  python3 preprocess-headshot.py [--src headshot.jpg] [--out headshot-pre.jpg]
The main script's DEFAULT_SRC points at the output file; run it as usual.
"""
import argparse, os, sys, tempfile, importlib.util

ap = argparse.ArgumentParser()
ap.add_argument("--src", default=None, help="source headshot (default: same as the banner script)")
ap.add_argument("--out", default=None, help="output image (default: headshot-pre.jpg next to this file)")
ARGS = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "make-fastfetch-banner.py")
OUT = ARGS.out or os.path.join(HERE, "headshot-pre.jpg")
CROP = (348, 90, 932, 810)   # PORTRAIT_CROP, must match the banner script
GAMMA = 0.45                 # midtone darkening after the autolevel (0.45 = darkest tested; 1.0 = none)

# Exec the banner script once with a throwaway --out so we can reuse its exact
# subject() mask (it shares the on-disk mask cache; the render itself is waste).
tmp = tempfile.mkdtemp(prefix="pre-head-")
sys.argv = [os.path.basename(SCRIPT), "--src", ARGS.src or os.path.join(HERE, "headshot.jpg"), "--out", tmp]
spec = importlib.util.spec_from_file_location("ff_banner", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from PIL import Image

src_path = ARGS.src or os.path.join(HERE, "headshot.jpg")
if not os.path.exists(src_path):
    raise SystemExit(f"Headshot not found: {src_path}")

# Same head region tone_lut() sees: crop, mask>=128.
crop, mask = mod.subject(CROP, protect=None)
mp = list(mask.get_flattened_data())
g = list(crop.convert("L").get_flattened_data())
hv = sorted(v for v, m in zip(g, mp) if m >= 128)

def pct(vals, p): return vals[int(len(vals)*p)]
lo, hi = pct(hv, 0.02), pct(hv, 0.98)
scale = 255.0 / (hi - lo)

im = Image.open(src_path).convert("RGB")
h, s, v = im.convert("HSV").split()
V = [float(x) for x in v.get_flattened_data()]
out = []
for x in V:
    if x <= lo:      st = 0.0
    elif x >= hi:    st = 255.0
    else:            st = (x - lo) * scale
    out.append(int(min(255, max(0, 255 * (st / 255.0) ** GAMMA))))
v2 = v.copy(); v2.putdata(out)
im2 = Image.merge("HSV", (h, s, v2)).convert("RGB")
im2.save(OUT, quality=95)

n = len(hv)
print(f"preprocessed {src_path} -> {OUT}")
print(f"  head region: {n} px  p2={lo} p98={hi}  autolevel + gamma {GAMMA}")
print(f"  run: python {os.path.basename(SCRIPT)} --src {OUT}")
