#!/usr/bin/env python3
"""Render a fastfetch-style banner for a GitHub profile README: an ASCII-art
portrait beside a personal "system info" block, drawn as a terminal window.

    python3 make-fastfetch-banner.py --src path/to/headshot.jpg --out .

Optionally use a hand-made ASCII portrait instead of the auto-generated one
(the art's glyphs/spaces are authoritative; the photo only colours each cell):

    python3 make-fastfetch-banner.py --ascii-portrait my-art.txt --out .

Writes next to --out:
  fastfetch.png    wide terminal banner, sized 2x for a ~880px README column
  fastfetch.svg    same banner as vector text, crisp at any size
  fastfetch.txt    same banner as plain text, for embedding in a README code fence
  avatar.jpg       plain square headshot crop, for the profile picture itself
  avatar-ascii.png the same square crop through the ASCII-art pipeline

Needs Pillow and Source Code Pro. Edit FIELDS to change the info block; edit
PORTRAIT_CROP / AVATAR_CROP if you swap in a different headshot.
"""
import argparse, hashlib, os, pickle, tempfile
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, "headshot-pre.jpg")

FONT_DIRS = [HERE, "/usr/share/fonts", "/usr/local/share/fonts", "/Library/Fonts",
             os.path.expanduser("~/.local/share/fonts"), os.path.expanduser("~/.fonts"),
             r"C:\Windows\Fonts"]

def find_font(name):
    """Locate a font file by name; Source Code Pro lives in a different
    directory on every distro, so search rather than hardcode a path."""
    for root in FONT_DIRS:
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            if name in files:
                return os.path.join(dirpath, name)
    raise SystemExit(f"Could not find {name}. Install Source Code Pro "
                     "(Fedora: sudo dnf install adobe-source-code-pro-fonts; "
                     "Debian/Ubuntu: sudo apt install fonts-source-code-pro), "
                     f"or drop the .otf next to {os.path.basename(__file__)}.")

FONT_R = find_font("SourceCodePro-Regular.otf")
FONT_B = find_font("SourceCodePro-Bold.otf")

# Cell geometry is measured from the actual font, never assumed: CW is the
# real monospace advance, CH is ascent+descent (the real line height). Every
# layout decision below -- grid rows, canvas size, glyph placement -- derives
# from these two measured numbers, so the rendered glyph grid always matches
# the geometry the ASCII analysis assumes (no squash/stretch).
FS  = 25
font  = ImageFont.truetype(FONT_R, FS)
fontb = ImageFont.truetype(FONT_B, FS)
ASC  = font.getmetrics()[0]
CH   = ASC + font.getmetrics()[1]
CW   = max(1, round(font.getlength("M")))

ap = argparse.ArgumentParser()
ap.add_argument("--src", default=DEFAULT_SRC, help="source headshot")
ap.add_argument("--out", default=".", help="output directory")
ap.add_argument("--cache", default=None, help="dir for the background-mask cache (default: temp)")
ap.add_argument("--ascii-portrait", default=None,
                help="use a hand-made ASCII portrait instead of auto-converting the photo: "
                     "a .txt of glyphs, or an image (.png/.jpg) that gets pasted as-is "
                     "(the photo, if any, colours a .txt portrait; an image portrait is used verbatim)")
ap.add_argument("--debug", action="store_true", help="write debug-*.png pipeline images")
ARGS = ap.parse_args()
SRC = ARGS.src
HAS_PHOTO = os.path.exists(SRC)
if not HAS_PHOTO and not ARGS.ascii_portrait:
    raise SystemExit(f"Headshot not found: {SRC}\nPass one with --src path/to/headshot.jpg")
OUTDIR = os.path.abspath(ARGS.out)
os.makedirs(OUTDIR, exist_ok=True)
SP  = ARGS.cache or os.path.join(tempfile.gettempdir(), "fastfetch-mask-cache")
os.makedirs(SP, exist_ok=True)
if HAS_PHOTO:
    with open(SRC, "rb") as _f:
        SRC_HASH = hashlib.sha256(_f.read()).hexdigest()[:16]
else:
    SRC_HASH = "nophoto"
from collections import deque



def subject(box, K=8, mw=340, protect=0.80):
    """Return (crop, mask) with the bokeh background removed."""
    cache = f"{SP}/cache_{SRC_HASH}_{'_'.join(map(str, box))}_{K}_{protect}.pkl"
    if os.path.exists(cache):
        with open(cache, "rb") as f: return pickle.load(f)
    crop = Image.open(SRC).convert("RGB").crop(box)
    MW = mw; MH = int(crop.height*MW/crop.width); N = MW*MH
    small = crop.resize((MW, MH), Image.LANCZOS)
    h, s, v = small.convert("HSV").split()
    H, S, V = map(lambda c: list(c.get_flattened_data()), (h, s, v))
    g = small.convert("L")
    D = list(ImageChops.difference(g, g.filter(ImageFilter.GaussianBlur(2.5)))
             .filter(ImageFilter.GaussianBlur(1.5)).get_flattened_data())
    PY_ = int(protect*MH) if protect else MH + 1
    def prot(i): return (i//MW) >= PY_
    def skin(i): return 3 <= H[i] <= 24 and S[i] >= 45
    def strict(i):
        if prot(i): return False
        if 25 <= H[i] <= 95 and S[i] >= 70 and V[i] >= 60: return True
        if 18 <= H[i] <= 100 and S[i] >= 45 and V[i] >= 90 and D[i] <= 4: return True
        if V[i] >= 165 and D[i] <= 4 and not skin(i): return True
        return False
    def loose(i):
        if prot(i): return False
        if 15 <= H[i] <= 110 and S[i] >= 30 and V[i] >= 40: return True
        if V[i] >= 140 and D[i] <= 7: return True
        return False
    st = [strict(i) for i in range(N)]; lo = [loose(i) for i in range(N)]
    border = [y*MW+x for x in range(MW) for y in (0, MH-1)] + [y*MW+x for y in range(MH) for x in (0, MW-1)]
    INF = 99; dist = [INF]*N; dq = deque()
    for i in border:
        if st[i] and dist[i]: dist[i] = 0; dq.appendleft(i)
    while dq:
        i = dq.popleft(); d = dist[i]; x, y = i % MW, i // MW
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if not (0 <= nx < MW and 0 <= ny < MH): continue
            j = ny*MW+nx
            if st[j]: nd = d
            elif lo[j]: nd = d+1
            else: continue
            if nd <= K and nd < dist[j]:
                dist[j] = nd; (dq.appendleft if nd == d else dq.append)(j)
    subj = [0 if d < INF else 1 for d in dist]
    best, seen = None, [0]*N
    for start in range(N):
        if subj[start] and not seen[start]:
            comp, q = [], deque([start]); seen[start] = 1
            while q:
                i = q.popleft(); comp.append(i); x, y = i % MW, i // MW
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < MW and 0 <= ny < MH:
                        j = ny*MW+nx
                        if subj[j] and not seen[j]: seen[j] = 1; q.append(j)
            if best is None or len(comp) > len(best): best = comp
    keep = [0]*N
    for i in best: keep[i] = 255
    m = Image.new("L", (MW, MH)); m.putdata(keep)
    # A radius-1 closing only bridges ~1px gaps -- too weak for a bright,
    # overexposed skin highlight (e.g. forehead glare) that the HSV+D
    # classifiers above mistake for smooth out-of-focus background: that
    # misclassification bites a real notch into the silhouette, connected
    # all the way out to the border, not just a few stray pixels. A much
    # larger closing radius bridges that notch shut while barely moving the
    # true (already-smooth) silhouette edge elsewhere.
    m = m.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.MinFilter(31)).filter(ImageFilter.GaussianBlur(1.2))
    out = (crop, m.resize(crop.size, Image.LANCZOS))
    with open(cache, "wb") as f: pickle.dump(out, f)
    return out

# ---- glyph ramps, measured from the actual font ----
ASCII_SET = " .'`,^:;~-_+=<>i!lI?/\\|()[]{}rcvunxzjftLCJUYXZOQ0mwqpdbkhao*#MW&8%B@$"
def ramps(cw, ch, fs):
    font = ImageFont.truetype(FONT_R, fs); asc = font.getmetrics()[0]
    def cov(c):
        im = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(im).text((cw/2, asc), c, font=font, fill=255, anchor="ms")
        return sum(im.get_flattened_data())/(255.0*cw*ch)
    a = sorted({c: cov(c) for c in ASCII_SET}.items(), key=lambda kv: kv[1])
    ev = lambda n: [min(a, key=lambda kv: abs(kv[1]-a[-1][1]*k/(n-1)))[0] for k in range(n)]
    return ev(16), ev(14) + ["░", "▒", "▓", "█"]

def tone_lut(gray, mask, head_frac=0.62, plo=0.04, phi=0.95, gamma=0.9,
             mode="anchor", skin_frac=0.90, skin_target=0.52):
    """Tone stretch driven by the HEAD region so the face keeps its range.

    mode="anchor" (default): map the dark percentile `plo` to black and the
    skin percentile `skin_frac` to `skin_target` (0..1 brightness). Anchoring
    on the skin value instead of the head's 95th percentile stops bright skin
    tones from clamping to pure white -- which is what previously flattened a
    whole face into the lightest glyphs.
    mode="percentile": old behaviour, lo..hi percentiles -> full range."""
    W, H = gray.size
    cut = int(H*head_frac)*W
    g = list(gray.get_flattened_data()); m = list(mask.get_flattened_data())
    vals = sorted(g[i] for i in range(cut) if m[i] >= 128)
    lo = vals[int(len(vals)*plo)]
    if mode == "anchor":
        skin = vals[min(len(vals)-1, int(len(vals)*skin_frac))]
        scale = skin_target/max(1.0, skin-lo)
        def f(i):
            v = max(0.0, (i-lo)*scale)
            return max(0, min(255, int((v**gamma)*255)))
        return [f(i) for i in range(256)], lo, skin
    hi = vals[int(len(vals)*phi)]
    return [max(0, min(255, int((max(0.0, (i-lo)/max(1, hi-lo))**gamma)*255))) for i in range(256)], lo, hi




# ---------------- geometry: sized 2x for a ~880px README column ----------------
COLS, ROWS = 164, 62
PAD_X, PAD_Y, TITLEBAR, MARGIN = 30, 26, 46, 22
PORTRAIT_CROP = (348, 90, 932, 810)      # head, neck and collar
AVATAR_CROP   = (270, 80, 1010, 820)     # square head-and-shoulders
PW, P_COL, P_ROW = 92, 1, 3              # ASCII portrait: columns and origin
PORTRAIT_MAX_ROWS = 55                   # banner height budget (P_ROW+PH+2 <= ROWS-1)
IC, LABW = 91, 14                        # info block: column and label width
USER = "mahmoud@github"                  # shell user@host, also fastfetch's title line
CWD  = "~/Documents/portfolio"

FIELDS = [
    ("Name",       "Mahmoud Youssef"),
    ("Role",       "Junior Backend Developer"),
    ("Focus",      "Backend Systems · REST APIs · Distributed Systems"),
    None,
    ("Languages",  "Java · Python · C++ · C · C# · JavaScript"),
    ("Stack",      "Spring Boot · Spring Security · JPA · Hibernate"),
    ("Data",       "PostgreSQL · MySQL · Redis"),
    ("Tools",      "Docker · Git · GitHub Actions · Maven"),
    None,
    ("Projects",   "WhatsApp API · BloodBridge · ReadSphere"),
    ("More Projects", "AttendPro · Time-Table · URL Shortener"),
    None,
    ("Location",   "Cairo, Egypt (Open to Remote)"),
    None,
    ("GitHub",     "github.com/MahmoudYoussef-web"),
    ("LinkedIn",   "linkedin.com/in/mahmoud-youssef-ba30723bb"),
    ("Gmail",      "mahmoudyoussed29@gmail.com"),
]

# ---------------- palette: the portfolio's own tokens ----------------
BG, BAR, LINE = (15,19,23), (27,35,43), (42,52,62)
TEXT, MUTED   = (233,230,223), (152,162,171)
ACCENT, GREEN = (236,163,95), (127,168,139)
BLUE, RED, YEL= (122,165,196), (204,75,63), (224,164,60)
ANSI_N = [(27,35,43), RED, GREEN, YEL, (91,135,168), (160,127,168), (95,168,160), MUTED]
ANSI_B = [LINE, (224,101,90), (158,196,168), ACCENT, BLUE, (187,154,196), (127,196,188), TEXT]

TEXT_W, TEXT_H = COLS*CW, ROWS*CH
WIN_W, WIN_H = TEXT_W + 2*PAD_X, TEXT_H + TITLEBAR + 2*PAD_Y
CAN_W, CAN_H = WIN_W + 2*MARGIN, WIN_H + 2*MARGIN
MX, MY = MARGIN, MARGIN

tfont = ImageFont.truetype(FONT_R, 22)
# Recorded alongside the PIL drawing calls below so the SVG export (further down)
# can reproduce the exact same grid without redoing any pixel analysis: each
# entry is one visible glyph as (row, col, char, rgb_fill, bold).
CELLS = []
CURSORS = []  # (row, col) grid position of each blinking-cursor block

def qcolor(c, step=8):
    """Round an RGB tuple to a coarser grid so adjacent near-identical portrait
    pixels collapse into the same SVG <tspan> run instead of each getting one."""
    return tuple(min(255, ((int(v) + step//2)//step)*step) for v in c)

img = Image.new("RGB", (CAN_W, CAN_H), (8,10,13)); d = ImageDraw.Draw(img)
d.rounded_rectangle([MX, MY, MX+WIN_W-1, MY+WIN_H-1], radius=16, fill=BG, outline=LINE, width=1)
d.rounded_rectangle([MX, MY, MX+WIN_W-1, MY+TITLEBAR+16], radius=16, fill=BAR)
d.rectangle([MX, MY+TITLEBAR-1, MX+WIN_W-1, MY+TITLEBAR-1], fill=LINE)
for i, c in enumerate((RED, YEL, GREEN)):
    cx = MX + 26 + i*24
    d.ellipse([cx-7, MY+TITLEBAR//2-7, cx+7, MY+TITLEBAR//2+7], fill=c)
d.text((MX+WIN_W//2, MY+TITLEBAR//2), f"{USER}: {CWD}", font=tfont, fill=MUTED, anchor="mm")

OX, OY = MX+PAD_X, MY+TITLEBAR+PAD_Y
def put(col, row, text, fill=TEXT, bold=False):
    f = fontb if bold else font
    for k, c in enumerate(text):
        # Always record into CELLS, even spaces: drawing a space glyph is a
        # no-op for the PNG, but CELLS is the only data source for the SVG
        # export -- skipping spaces there means the SVG's <tspan> text joins
        # words together (e.g. "Pacifique Mugisho" -> "PacifiqueMugisho")
        # even though each glyph still gets its own correct x.
        d.text((OX+(col+k)*CW+CW/2, OY+row*CH+ASC), c, font=f, fill=fill, anchor="ms")
        CELLS.append((row, col+k, c, fill, bold))

def prompt(row, cmd=None, cursor=False):
    c = 1
    put(c, row, USER, GREEN, bold=True); c += len(USER)
    put(c, row, ":", MUTED); c += 1
    put(c, row, CWD, BLUE, bold=True); c += len(CWD)
    put(c, row, "$", MUTED); c += 2
    if cmd: put(c, row, cmd, TEXT); c += len(cmd) + 1
    if cursor:
        d.rectangle([OX+c*CW, OY+row*CH+4, OX+c*CW+CW-3, OY+row*CH+CH-4], fill=ACCENT)
        CURSORS.append((row, c))

# ---------------- ASCII-art rendering pipeline (shared by the banner portrait and the standalone avatar) ----------------

# Density ramp measured from the real font at the real cell size. Every
# printable-ASCII candidate is rendered once and its ink coverage is measured;
# candidates are sorted darkest-first and thinned to levels whose coverage
# differs by a perceptible step. That keeps the tone->glyph mapping smooth and
# monotonic (dark pixel -> dense glyph, bright pixel -> light glyph) instead of
# picking arbitrary near-identical glyphs -- which is what turns a portrait into
# "random text". Regular and bold weight both feed the ramp so the dense end
# reaches further than a single weight can.
def _curated_ramp():
    chars = (" .'`^,:;-_+=<>i!lI?/\\|()[]{}rcvunxzjftLCJUYXZOQ0mwqpdbkhao"
             "*#MW&8%B@$")
    def cov(c, f):
        # Filled-pixel ratio, binarized at 64/255: anti-aliased sub-pixel ink
        # contributes a whole pixel. This tracks perceived darkness better than
        # summed alpha coverage (a thin stroke that antialiases lightly scores
        # far lower against a "l", and ordering like "<" vs "," vs "#" is
        # decided by the real font, never assumed).
        im = Image.new("L", (CW, CH), 0)
        ImageDraw.Draw(im).text((CW/2, ASC), c, font=f, fill=255, anchor="ms")
        px = im.get_flattened_data()
        return sum(1 for v in px if v >= 64)/float(CW*CH)
    glyphs = [(cov(c, font), c, False) for c in chars]
    glyphs += [(cov(c, fontb), c, True) for c in chars]
    glyphs.sort(key=lambda t: t[0])
    maxc = glyphs[-1][0]
    step = maxc*0.012
    sel, prev = [], -1.0
    for cv, c, bold in glyphs:
        if cv - prev >= step:
            sel.append((cv, c, bold)); prev = cv
    sel.sort(reverse=True)                  # darkest-first
    ramp = [(c, bold) for _, c, bold in sel]
    covs = [cv for cv, _, _ in sel]
    return ramp, covs, covs[0]

RAMP, RAMP_COV, RAMP_MAXC = _curated_ramp()

def frame_box(crop_box, margin=0.06):
    """(crop, mask, framed_box): background removal plus subject framing.

    The framed box is the subject's mask bounding box padded by `margin`,
    then padded again to the SOURCE crop's own aspect ratio (centered on the
    subject). Keeping the source aspect is what stops a square crop from
    turning into a tall narrow ASCII column: the grid's cols:rows then match
    the source proportions and the max_rows cap rescales proportionally.
    Clamping to the source bounds means a subject that already fills the
    whole crop keeps that (correct) frame instead of getting decapitated."""
    crop, mask = subject(crop_box, protect=None)
    bb = mask.getbbox()
    if bb is None:
        return crop, mask, (0, 0, crop.width, crop.height)
    m = int(max(bb[2]-bb[0], bb[3]-bb[1]) * margin)
    x0, y0 = max(0, bb[0]-m), max(0, bb[1]-m)
    x1, y1 = min(crop.width, bb[2]+m), min(crop.height, bb[3]+m)
    fw, fh = x1-x0, y1-y0
    src_ar = crop.height/crop.width          # target: source proportions
    if fh/fw > src_ar:                       # too tall -> widen (pad sides)
        nw = int(round(fh/src_ar)); cx = (x0+x1)/2.0
        x0, x1 = int(round(cx-nw/2)), int(round(cx+nw/2))
    elif fh/fw < src_ar:                     # too wide -> raise (pad top/bottom)
        nh = int(round(fw*src_ar)); cy = (y0+y1)/2.0
        y0, y1 = int(round(cy-nh/2)), int(round(cy+nh/2))
    # Clamp to the source bounds, then shift the whole box back so clamping on
    # one side doesn't leave the subject off-centre (which also distorts the
    # frame's aspect).
    over_r = x1 - crop.width
    if over_r > 0: x0, x1 = x0 - over_r, crop.width
    over_l = -x0
    if over_l > 0: x0, x1 = 0, x1 - over_l
    over_r = x1 - crop.width
    if over_r > 0: x1 = crop.width
    over_b = y1 - crop.height
    if over_b > 0: y0, y1 = y0 - over_b, crop.height
    over_t = -y0
    if over_t > 0: y0, y1 = 0, y1 - over_t
    over_b = y1 - crop.height
    if over_b > 0: y1 = crop.height
    return crop.crop((x0, y0, x1, y1)), mask.crop((x0, y0, x1, y1)), (x0, y0, x1, y1)

def render_ascii_raster(used, rows, IDX, C, M, bg=(8, 10, 13)):
    """Draw a grid of RAMP glyphs (one per cell) to a PIL raster."""
    im = Image.new("RGB", (used*CW, rows*CH), bg)
    dd = ImageDraw.Draw(im)
    for i, k in enumerate(IDX):
        if M[i] < 40: continue
        c, glyph_bold = RAMP[k]
        if c == " ": continue
        col = ramp_color(k, C[i])
        acol, arow = i % used, i // used
        dd.text((acol*CW+CW/2, arow*CH+ASC), c,
                font=(fontb if glyph_bold else font), fill=col, anchor="ms")
    return im

def ascii_grid(crop_box, cols, max_rows=None, margin=0.06, dither=False, debug=None):
    """Run subject()+tone_lut()+RAMP+optional dithering over crop_box laid out
    `cols` characters wide. `frame_box` frames the subject to the source crop's
    own aspect ratio (see there) so the grid keeps the source proportions and
    the head fills the width instead of floating in empty space; `max_rows`
    caps the grid height (banner layout) by scaling down, never by squashing.
    Returns (rows, IDX, C, M, used_cols): IDX[i] indexes into RAMP, C[i] is the
    enhanced RGB for that cell, M[i]<40 means no glyph (outside the subject
    mask). `dither=False` disables Floyd-Steinberg error diffusion (direct
    per-cell quantization). `debug` collects intermediate images for the
    debug outputs."""
    crop, mask, framed = frame_box(crop_box, margin=margin)
    rows = round(cols*(crop.height/crop.width)*(CW/CH))
    if max_rows and rows > max_rows:
        cols = max(1, round(cols*max_rows/rows))
        rows = max_rows
    if debug is not None:
        debug["crop"] = crop
        debug["framed_box"] = framed

    sub = Image.new("RGB", crop.size, (0,0,0)); sub.paste(crop, (0,0), mask)
    sub = sub.filter(ImageFilter.GaussianBlur(2))
    sub.paste(Image.new("RGB", crop.size, (0,0,0)), (0,0), mask.point(lambda v: 255-v))

    # A light FIND_EDGES blend restores crisp hair/brow/jaw boundaries that the
    # smoothing blur above softens, without reintroducing pore/blemish noise.
    gray0 = sub.convert("L")
    # The blur also flattens fine feature contrast (eye sockets, nostrils,
    # lips). A gentle unsharp pass brings that back -- enough to keep the
    # features readable, light enough to stay below the glyph grid's noise.
    gray0 = gray0.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=3))
    edges = gray0.filter(ImageFilter.FIND_EDGES)
    gray = Image.blend(gray0, edges, 0.18)
    if debug is not None:
        debug["gray"] = gray

    # Tone: the head's own values drive the curve (see tone_lut). The anchor
    # mode maps the skin percentile to ~0.68 brightness so the face stays on
    # the light side of the glyph ramp and features (brows, eyes, nose, lips)
    # drop below it as darker glyphs instead of all landing on dense letters.
    gv, mv = list(gray.get_flattened_data()), list(mask.get_flattened_data())
    head_px = [v for v, m in zip(gv, mv) if m >= 128]
    head_mean = sum(head_px)/max(1, len(head_px))
    gamma = 1.15 if head_mean < 170 else 1.05   # bright heads need less darkening
    lut, _, _ = tone_lut(gray, mask, head_frac=0.70, plo=0.02, phi=0.95,
                         gamma=gamma, mode="anchor", skin_frac=0.90, skin_target=0.68)
    L = list(gray.point(lut).resize((cols, rows), Image.LANCZOS).get_flattened_data())
    if debug is not None:
        debug["tone"] = gray.point(lut)
    C = list(ImageEnhance.Color(sub.resize((cols, rows), Image.LANCZOS)).enhance(1.25).get_flattened_data())
    M = list(mask.resize((cols, rows), Image.LANCZOS).get_flattened_data())

    # Tone levels are the glyphs' *measured* density, not a uniform index grid:
    # equal density steps then equal visual darkness steps. Quantizing each
    # cell to its nearest RAMP level independently leaves visible banding;
    # Floyd-Steinberg diffuses the rounding error into not-yet-visited
    # neighbours (never across the mask boundary) to trade banding for a
    # smoother gradient. It is optional: some subjects look cleaner with
    # straight per-cell quantization (dither=False).
    def glyph_tone(k): return 255.0*(1.0 - RAMP_COV[k]/RAMP_MAXC)
    err = [0.0]*(cols*rows)
    IDX = [0]*(cols*rows)
    for y in range(rows):
        for x in range(cols):
            i = y*cols+x
            if M[i] < 40: continue
            v = max(0.0, min(255.0, L[i]+err[i]))
            target = RAMP_MAXC*(1.0 - v/255.0)
            k = min(range(len(RAMP)), key=lambda j: abs(RAMP_COV[j]-target))
            IDX[i] = k
            if dither:
                e = v - glyph_tone(k)
                if x+1 < cols and M[i+1] >= 40: err[i+1] += e*7/16
                if y+1 < rows:
                    if x > 0 and M[i+cols-1] >= 40: err[i+cols-1] += e*3/16
                    if M[i+cols] >= 40: err[i+cols] += e*5/16
                    if x+1 < cols and M[i+cols+1] >= 40: err[i+cols+1] += e*1/16
    return rows, IDX, C, M, cols

def ramp_color(k, rgb):
    r, g, b = rgb; mx = max(r, g, b, 1)
    col = tuple(min(255, int(v*min(1.45, 205/mx))) for v in (r, g, b))
    lum = 1.0 - RAMP_COV[k]/RAMP_MAXC              # 0 = darkest glyph, 1 = lightest
    col = tuple(int(v*(0.6+0.4*lum)) for v in col)          # shadows dim, highlights stay bright
    col = tuple(min(255, round(v/16)*16) for v in col)       # ANSI-ish quantization instead of a smooth photo gradient
    return col

# ---------------- ASCII portrait (banner) ----------------
_DEBUG = None
_IMG_PORTRAIT = None          # (x0, y0, w, h) when the portrait is a pasted image
if ARGS.ascii_portrait:
    if ARGS.ascii_portrait.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")):
        # Image mode: the portrait is a finished raster (e.g. from an external
        # ASCII-art converter). No glyph analysis here -- the art is pasted
        # pixel-perfect into the portrait box, centred and aspect-fitted, and
        # the chrome / prompt / info block are drawn around it as usual.
        PUSED, PH = PW, 50                # portrait box: 92 cols x 50 rows (tighter than auto so the square art hugs the panel height)
        POFF = 0
        try:
            pim = Image.open(ARGS.ascii_portrait).convert("RGB")
        except OSError as e:
            raise SystemExit(f"Could not open portrait image {ARGS.ascii_portrait}: {e}")
        pbox_w, pbox_h = PUSED*CW, PH*CH
        ar_img, ar_box = pim.width/pim.height, pbox_w/pbox_h
        if ar_img > ar_box:
            iw, ih = pbox_w, max(1, round(pbox_w/ar_img))
        else:
            ih, iw = pbox_h, max(1, round(pbox_h*ar_img))
        # Cap the raster so the pasted area stays small enough for a README
        # (the banner box is ~1380px wide, displayed at ~880px, so ~1200px is
        # already sharper than the page can show). ASCII-art rasters have a
        # small effective palette, so 128-colour PNG quantization keeps the
        # file ~300KB with none of JPEG's fringing on coloured text.
        cap = 1200
        if max(iw, ih) > cap:
            sc = cap/max(iw, ih)
            iw, ih = max(1, round(iw*sc)), max(1, round(ih*sc))
        shrink = 0.90
        iw, ih = max(1, round(iw*shrink)), max(1, round(ih*shrink))
        pim = pim.resize((iw, ih), Image.LANCZOS)
        pim = pim.quantize(colors=128, method=2)      # keep P-mode: palette PNG is ~4x smaller
        px0 = OX + P_COL*CW + (pbox_w-iw)//2
        py0 = OY + P_ROW*CH + (pbox_h-ih)//2
        img.paste(pim.convert("RGB"), (px0, py0))
        portrait_img_path = os.path.join(OUTDIR, "portrait.png")
        pim.save(portrait_img_path, optimize=True)
        _IMG_PORTRAIT = (px0, py0, iw, ih)
        print(f"portrait image {pim.width}x{pim.height} pasted at ({px0},{py0}) "
              f"-> {portrait_img_path}  (fastfetch.txt has no glyphs for it)")
    else:
        # Hand-made text art: the glyphs/spaces are the source of truth. The photo (if
        # one is given) is resampled to the art's own grid purely to colour each
        # cell, so the banner keeps the terminal screenshot look without letting
        # the auto-pipeline override the artist's shapes.
        try:
            art_lines = [ln.rstrip() for ln in open(ARGS.ascii_portrait, encoding="utf-8").read().splitlines()]
        except OSError as e:
            raise SystemExit(f"Could not read ASCII portrait {ARGS.ascii_portrait}: {e}")
        while art_lines and not art_lines[-1].strip():
            art_lines.pop()
        PH, PUSED = len(art_lines), max((len(ln) for ln in art_lines), default=0)
        if PUSED == 0:
            raise SystemExit(f"ASCII portrait {ARGS.ascii_portrait} is empty")
        if PUSED > PW:
            print(f"warning: portrait art is {PUSED} cols wide, the portrait area is {PW}; "
                  f"it may overlap the info block (col {IC})")
        if P_ROW + PH + 2 >= ROWS:
            print(f"warning: portrait art is {PH} rows tall, the window only fits {ROWS-P_ROW-3}; "
                  f"the bottom will be cut off")
        POFF = (PW - PUSED)//2
        if HAS_PHOTO:
            try:
                _csub, _cmask, _cframed = frame_box(PORTRAIT_CROP)
                _cpx = list(ImageEnhance.Color(_csub).enhance(1.25)
                            .resize((PUSED, PH), Image.LANCZOS).get_flattened_data())
            except Exception:
                _cpx = None
        else:
            _cpx = None
        _midk = len(RAMP)//2
        for r, ln in enumerate(art_lines):
            for xcol, ch in enumerate(ln):
                if ch == " ": continue
                pcol = P_COL + POFF + xcol
                prow = P_ROW + r
                if _cpx is None:
                    col = TEXT
                else:
                    j = (r*PUSED + xcol)*3
                    col = ramp_color(_midk, (_cpx[j], _cpx[j+1], _cpx[j+2]))
                d.text((OX+pcol*CW+CW/2, OY+prow*CH+ASC), ch, font=font, fill=col, anchor="ms")
                CELLS.append((prow, pcol, ch, qcolor(col), False))
else:
    _DEBUG = {} if ARGS.debug else None
    PH, IDX, C, M, PUSED = ascii_grid(PORTRAIT_CROP, PW, max_rows=PORTRAIT_MAX_ROWS, debug=_DEBUG)
    POFF = (PW - PUSED)//2
    for i, k in enumerate(IDX):
        if M[i] < 40: continue
        c, glyph_bold = RAMP[k]
        if c == " ": continue
        col = ramp_color(k, C[i])
        pcol, prow = P_COL + POFF + i%PUSED, P_ROW + i//PUSED
        d.text((OX+pcol*CW+CW/2, OY+prow*CH+ASC), c, font=(fontb if glyph_bold else font), fill=col, anchor="ms")
        CELLS.append((prow, pcol, c, qcolor(col), glyph_bold))

# ---------------- info block ----------------
info_h = 2 + 1 + len(FIELDS) + 1 + 2
IR = P_ROW + (PH - info_h)//2
put(IC, IR, USER, GREEN, bold=True)
put(IC, IR+1, "─"*len(USER), LINE)
r = IR + 3
for f in FIELDS:
    if f is None: r += 1; continue
    lab, val = f
    if lab: put(IC, r, lab, ACCENT, bold=True)
    put(IC+LABW, r, val, TEXT if lab else MUTED)
    r += 1
r += 1
for k, row in enumerate((ANSI_N, ANSI_B)):
    for j, c in enumerate(row):
        x0 = OX + (IC+j*4)*CW
        d.rectangle([x0, OY+(r+k)*CH+3, x0+4*CW-4, OY+(r+k)*CH+CH-4], fill=c)

prompt(1, "fastfetch")
prompt(P_ROW + PH + 2, cursor=True)

banner = os.path.join(OUTDIR, "fastfetch.png")
img.save(banner)

# ---------------- SVG export ----------------
# Same banner, but every glyph is a real <text>/<tspan> instead of a PIL glyph
# rasterized into a 15x31px cell. Vector text stays crisp at any render size
# instead of baking small glyphs into a fixed-resolution raster. None of the
# analysis changes here -- CELLS/CURSORS just record the same (row, col,
# char, color) decisions already made above.

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def hx(c):
    return "#%02x%02x%02x" % tuple(int(v) for v in c)

_GLYPH_W = {}
def glyph_width(ch, bold):
    key = (ch, bold)
    if key not in _GLYPH_W:
        _GLYPH_W[key] = d.textlength(ch, font=fontb if bold else font)
    return _GLYPH_W[key]

def svg_row(row_no, cells):
    """One <text> per grid row; same-color runs share a <tspan> with an
    explicit per-character x list, so glyphs stay grid-aligned regardless of
    the viewer's actual monospace font metrics, and colors change without
    needing a separate <text> per glyph. x is each glyph's own left edge
    (cell center minus half its measured width) with the default
    text-anchor="start" -- NOT text-anchor="middle" with a shared x list,
    which different SVG renderers resolve inconsistently (some center each
    character on its listed x, some don't), producing the left-shifted
    characters this was fixed for. Left-edge positioning has no such
    ambiguity: every renderer places character N's origin at xs[N], full stop."""
    cells = sorted(cells, key=lambda t: t[0])
    baseline = OY + row_no*CH + ASC
    parts = [f'<text y="{baseline}" font-size="{FS}" xml:space="preserve">']
    run_fill, run_bold, xs, chars = None, None, [], []
    def flush():
        if chars:
            weight = ' font-weight="bold"' if run_bold else ""
            parts.append(f'<tspan x="{" ".join(xs)}" fill="{hx(run_fill)}"{weight}>{esc("".join(chars))}</tspan>')
    for cell_col, ch, fill, bold in cells:
        if fill != run_fill or bold != run_bold:
            flush(); xs, chars = [], []
            run_fill, run_bold = fill, bold
        cell_center = OX + cell_col*CW + CW/2
        xs.append(str(round(cell_center - glyph_width(ch, bold)/2)))
        chars.append(ch)
    flush()
    parts.append("</text>")
    return "".join(parts)

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CAN_W}" height="{CAN_H}" '
    f'viewBox="0 0 {CAN_W} {CAN_H}" font-family="\'Source Code Pro\', monospace">',
    f'<rect width="{CAN_W}" height="{CAN_H}" fill="{hx((8,10,13))}"/>',
    f'<rect x="{MX}" y="{MY}" width="{WIN_W}" height="{WIN_H}" rx="16" ry="16" '
    f'fill="{hx(BG)}" stroke="{hx(LINE)}" stroke-width="1"/>',
    f'<rect x="{MX}" y="{MY}" width="{WIN_W}" height="{TITLEBAR+16}" rx="16" ry="16" fill="{hx(BAR)}"/>',
    f'<rect x="{MX}" y="{MY+TITLEBAR-1}" width="{WIN_W}" height="1" fill="{hx(LINE)}"/>',
]
for dot_i, dot_c in enumerate((RED, YEL, GREEN)):
    dot_cx = MX + 26 + dot_i*24
    svg.append(f'<circle cx="{dot_cx}" cy="{MY+TITLEBAR//2}" r="7.5" fill="{hx(dot_c)}"/>')
svg.append(
    f'<text x="{MX+WIN_W//2}" y="{MY+TITLEBAR//2}" text-anchor="middle" dominant-baseline="central" '
    f'font-size="22" fill="{hx(MUTED)}">{esc(f"{USER}: {CWD}")}</text>'
)

if _IMG_PORTRAIT is not None:
    ix, iy, iw, ih = _IMG_PORTRAIT
    svg.append(f'<image x="{ix}" y="{iy}" width="{iw}" height="{ih}" '
               f'href="portrait.png" preserveAspectRatio="xMidYMid meet"/>')

svg_rows = {}
for cell_row, cell_col, ch, fill, bold in CELLS:
    svg_rows.setdefault(cell_row, []).append((cell_col, ch, fill, bold))
for row_no in sorted(svg_rows):
    svg.append(svg_row(row_no, svg_rows[row_no]))

for swatch_k, swatch_row in enumerate((ANSI_N, ANSI_B)):
    for swatch_j, swatch_c in enumerate(swatch_row):
        sx0 = OX + (IC+swatch_j*4)*CW
        sy0 = OY + (r+swatch_k)*CH + 3
        svg.append(f'<rect x="{sx0}" y="{sy0}" width="{4*CW-3}" height="{CH-6}" fill="{hx(swatch_c)}"/>')

for cur_row, cur_col in CURSORS:
    cx0 = OX + cur_col*CW
    cy0 = OY + cur_row*CH + 4
    svg.append(f'<rect x="{cx0}" y="{cy0}" width="{CW-2}" height="{CH-7}" fill="{hx(ACCENT)}"/>')

svg.append("</svg>")
svg_path = os.path.join(OUTDIR, "fastfetch.svg")
with open(svg_path, "w", encoding="utf-8") as f:
    f.write("".join(svg))

# ---------------- plain-text export (no color, drops straight into a README code fence) ----------------
maxrow = max(cr for cr, *_ in CELLS) + 1
maxcol = max(cc for _, cc, *_ in CELLS) + 1
grid = [[" "]*maxcol for _ in range(maxrow)]
for cr, cc, ch, _fill, _bold in CELLS:
    grid[cr][cc] = ch
text_lines = ["".join(row).rstrip() for row in grid]
while text_lines and not text_lines[-1]:
    text_lines.pop()
txt_path = os.path.join(OUTDIR, "fastfetch.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(text_lines) + "\n")

# ---------------- plain avatar crop ----------------
if HAS_PHOTO:
    av = Image.open(SRC).convert("RGB").crop(AVATAR_CROP).resize((1000, 1000), Image.LANCZOS)
    avatar = os.path.join(OUTDIR, "avatar.jpg")   # JPEG: a photo as PNG runs ~900KB, near GitHub's 1MB cap
    av.save(avatar, quality=92, subsampling=0, optimize=True)

    # ---------------- ASCII-art avatar (same pipeline as the banner portrait, square crop, no window chrome) ----------------
    AV_COLS = 100
    av_rows, av_IDX, av_C, av_M, av_used = ascii_grid(AVATAR_CROP, AV_COLS)
    av_ascii = render_ascii_raster(av_used, av_rows, av_IDX, av_C, av_M)
    avatar_ascii_path = os.path.join(OUTDIR, "avatar-ascii.png")
    av_ascii.save(avatar_ascii_path)

    # ---------------- debug outputs ----------------
    # One of each stage of the ASCII pipeline, so a bad portrait can be traced to
    # the exact step where the features vanished (crop geometry, grayscale,
    # tone stretch, glyph mapping, or dithering).
    if _DEBUG is not None:
        dbg = os.path.join(OUTDIR, "debug-crop.png");      _DEBUG["crop"].save(dbg)
        dbg = os.path.join(OUTDIR, "debug-grayscale.png"); _DEBUG["gray"].save(dbg)
        dbg = os.path.join(OUTDIR, "debug-tone.png");      _DEBUG["tone"].save(dbg)

        # A/B: the same grid once dithered, once with direct per-cell quantization
        # (default output is no-dither; dithering only matters when the ramp is
        # too coarse to carry the gradient on its own).
        avD_rows, avD_IDX, avD_C, avD_M, avD_used = ascii_grid(AVATAR_CROP, AV_COLS, dither=True)
        imD = render_ascii_raster(avD_used, avD_rows, avD_IDX, avD_C, avD_M)
        dbg = os.path.join(OUTDIR, "debug-ascii-dither.png");    imD.save(dbg)
        dbg = os.path.join(OUTDIR, "debug-ascii-no-dither.png"); av_ascii.save(dbg)

        # Measured density ramp, rendered darkest -> lightest: the mapping each
        # portrait cell actually uses (ratios printed to the console below).
        strip = Image.new("RGB", ((len(RAMP)+1)*CW, 2*CH), (8, 10, 13))
        ds = ImageDraw.Draw(strip)
        for j, (c, bold) in enumerate(RAMP):
            ds.text(((j+1)*CW+CW/2, CH+ASC), c, font=(fontb if bold else font),
                    fill=(233, 230, 223), anchor="ms")
        dbg = os.path.join(OUTDIR, "debug-character-density.png"); strip.save(dbg)
        ascii_ramp = "".join(("\\u%04X" % ord(c)) if ord(c) > 127 else c for c, _ in RAMP)
        print("ramp(%d) darkest->lightest: %s" % (len(RAMP), ascii_ramp))
        print("ramp densities: %s" % " ".join("%.2f" % (v/RAMP_MAXC) for v in RAMP_COV))

print(f"banner {img.size} portrait {PUSED}x{PH} rows {P_ROW}-{P_ROW+PH-1} info {IR}-{r+1}"
      f"  {os.path.getsize(banner)//1024}KB")
print(f"portrait visual aspect {(PH*CH)/(PUSED*CW):.3f}  avatar visual aspect "
      f"{(av_rows*CH)/(av_used*CW):.3f}" if HAS_PHOTO
      else f"portrait visual aspect {(PH*CH)/(PUSED*CW):.3f}")
print(f"svg {CAN_W}x{CAN_H}  {os.path.getsize(svg_path)//1024}KB  -> {svg_path}")
print(f"txt {maxcol}x{len(text_lines)}  {os.path.getsize(txt_path)} bytes -> {txt_path}")
if HAS_PHOTO:
    print(f"avatar {av.size}  {os.path.getsize(avatar)//1024}KB")
    print(f"avatar-ascii {av_ascii.size}  {os.path.getsize(avatar_ascii_path)//1024}KB -> {avatar_ascii_path}")
