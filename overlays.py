"""Overlay engine: rebrands the 3 full-screen cards and covers the two product
names everywhere they appear in the POS UI, matching field backgrounds and text
style. Backgrounds/text colours are sampled per-frame so dimmed (menu-open)
frames are matched automatically."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 30.0
RB = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/"

# ---- replacement product names ----
P1 = "Mineral Water 500ml"          # was "Coke Can 330ml"
P2 = "Mister Potato Chips BBQ 60g"  # was "Lays Cheese & Onion 325g"

# ---- brand cards (full-frame replacement) ----
_open  = np.array(Image.open("assets_open.png").convert("RGB"))
_title = np.array(Image.open("assets_title.png").convert("RGB"))
_close = np.array(Image.open("assets_close.png").convert("RGB"))

# time windows (seconds) -> frame index ranges [f0,f1)
def fr(a, b): return (int(round(a*FPS)), int(round(b*FPS)))
OPEN_R  = fr(0.0,   3.08)
TITLE_R = fr(3.08,  6.10)
CLOSE_R = fr(142.80, 1e9)

# barcode landmark template for form scroll-tracking
_BC = np.load("ref_barcode.npy").astype(np.float32)   # 50 x 90
_BC_Y0, _BC_Y1, _BC_X0, _BC_X1 = 335, 385, 1035, 1125

def _fit_font(text, weight, size, maxw):
    while size > 8:
        f = ImageFont.truetype(RB + f"Roboto-{weight}.ttf", size)
        bb = f.getbbox(text)
        if (bb[2]-bb[0]) <= maxw:
            return f, size
        size -= 1
    return f, size

class Cover:
    """A per-scene text cover. Pre-renders the replacement text to an alpha mask
    aligned so its cap-top sits at (tx, ty). At render time it fills the rect with
    the (optionally sampled) background colour and blends the text in a matched
    darker tone."""
    def __init__(self, t0, t1, rect, text, tx, ty, size, weight="Regular",
                 sample=None, ratio=0.34, fixed_bg=None, maxw=None):
        self.f0, self.f1 = int(round(t0*FPS)), int(round(t1*FPS))
        self.x0, self.y0, self.x1, self.y1 = rect
        self.sample = sample
        self.ratio = ratio
        self.fixed_bg = fixed_bg
        w = self.x1 - self.x0; h = self.y1 - self.y0
        maxw = maxw or (self.x1 - tx - 2)
        font, size = _fit_font(text, weight, size, maxw)
        # render text on a transparent tile the size of the rect
        tile = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(tile)
        bb = font.getbbox(text)          # (l,t,r,b) ink box; t = cap-top offset
        dx = (tx - self.x0) - bb[0]
        dy = (ty - self.y0) - bb[1]
        d.text((dx, dy), text, font=font, fill=255)
        self.alpha = (np.array(tile).astype(np.float32) / 255.0)[..., None]

    def active(self, fi): return self.f0 <= fi < self.f1

    def apply(self, img):
        if self.fixed_bg is not None:
            bg = np.array(self.fixed_bg, np.float32)
        else:
            sx, sy = self.sample
            bg = img[sy, sx].astype(np.float32)
        txt = np.clip(bg * self.ratio, 0, 255)
        region = img[self.y0:self.y1, self.x0:self.x1].astype(np.float32)
        filled = np.empty_like(region); filled[:] = bg
        out = filled * (1 - self.alpha) + txt * self.alpha
        img[self.y0:self.y1, self.x0:self.x1] = np.clip(out, 0, 255).astype(np.uint8)


HEADER_Y = 59        # scroll content starts below the fixed blue header
class TrackedFormCover:
    """Covers the Add Products name field, following the form as it scrolls.
    Uses the barcode-box landmark (rigidly attached to the form) to estimate the
    vertical scroll offset each frame, then places the cover on the name at
    captop = 188 + dy, clipped to the scroll area."""
    def __init__(self, t0, t1, text, size=22, ratio=0.30, maxw=300,
                 x0=482, x1=792, cap0=188, top_off=11, bot_off=23):
        self.f0, self.f1 = int(round(t0*FPS)), int(round(t1*FPS))
        self.x0, self.x1 = x0, x1
        self.cap0, self.top_off, self.bot_off = cap0, top_off, bot_off
        self.ratio = ratio
        font, _ = _fit_font(text, "Regular", size, maxw)
        w = x1 - x0; h = 60
        tile = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(tile)
        bb = font.getbbox(text)
        self.bl = bb[0]                     # ink left
        d.text(((484 - x0) - bb[0], 20 - bb[1]), text, font=font, fill=255)
        self.textalpha = np.array(tile).astype(np.float32) / 255.0   # cap-top at row 20
        self.prev = 0

    def active(self, fi):
        if fi == self.f0:
            self.prev = 0                   # form is at rest when window opens
        return self.f0 <= fi < self.f1

    def _dy(self, img):
        col = img[:, _BC_X0:_BC_X1].astype(np.float32).mean(axis=2)
        best = (1e18, self.prev)
        for dy in range(-240, 41):
            ys = _BC_Y0 + dy; ye = _BC_Y1 + dy
            if ys < 0 or ye > 720:
                continue
            d = _BC - col[ys:ye]
            ssd = (d*d).mean()
            s = ssd + 0.25 * (dy - self.prev) ** 2
            if s < best[0]:
                best = (s, dy, ssd)
        return best[1], best[2]

    def apply(self, img):
        dy, ssd = self._dy(img)
        if ssd > 500:                       # landmark lost -> form not trackable
            return
        self.prev = dy
        captop = self.cap0 + dy
        box_top = captop - self.top_off
        box_bot = captop + self.bot_off
        ct = max(HEADER_Y, box_top)
        if box_bot <= ct:                   # name fully under the header / gone
            return
        bg = np.array((252, 252, 252), np.float32)
        txt = np.clip(bg * self.ratio, 0, 255)
        # text alpha aligned so its cap-top (tile row 20) lands at `captop`
        a_y0 = ct - (captop - 20)
        a = self.textalpha[a_y0:a_y0 + (box_bot - ct)]
        region = np.empty((box_bot - ct, self.x1 - self.x0, 3), np.float32)
        region[:] = bg
        if a.shape[0] == region.shape[0]:
            region = region * (1 - a[..., None]) + txt * a[..., None]
        img[ct:box_bot, self.x0:self.x1] = np.clip(region, 0, 255).astype(np.uint8)

# ---------------- cover definitions ----------------
FORM_BG = (252, 252, 252)

# scroll-tracked Add Products name fields (follow the form as it scrolls)
TRACKED = [
    TrackedFormCover(41.0,  67.6,  P1, size=22, maxw=300),   # product 1
    TrackedFormCover(88.0, 108.0,  P2, size=22, maxw=300),   # product 2
]

COVERS = [
    # --- back-office product list, ONLY coke visible ---
    Cover(84.57, 87.33, (582, 115, 905, 138), P1, 584, 118, 23,
          weight="Regular", sample=(1005, 126), ratio=0.33),

    # --- back-office product list, BOTH products (incl. menu-dim + crossfade) ---
    Cover(129.50, 138.10, (582, 115, 905, 138), P1, 584, 118, 23,
          weight="Regular", sample=(1005, 126), ratio=0.33),
    Cover(129.50, 138.10, (582, 238, 905, 262), P2, 584, 241, 23,
          weight="Regular", sample=(1005, 250), ratio=0.33),

    # --- POS sale screen, both products (1-frame overlap at the crossfade) ---
    Cover(138.07, 142.80, (373, 104, 772, 140), P1, 378, 110, 23,
          weight="Regular", sample=(762, 120), ratio=0.33, maxw=360),
    Cover(138.07, 142.80, (373, 212, 772, 248), P2, 378, 218, 23,
          weight="Regular", sample=(762, 228), ratio=0.33, maxw=360),
]

def render_frame(img, fi):
    """img: HxWx3 uint8 (modified in place / returned)."""
    if OPEN_R[0] <= fi < OPEN_R[1]:
        return _open.copy()
    if TITLE_R[0] <= fi < TITLE_R[1]:
        return _title.copy()
    if CLOSE_R[0] <= fi < CLOSE_R[1]:
        return _close.copy()
    for c in TRACKED:
        if c.active(fi):
            c.apply(img)
    for c in COVERS:
        if c.active(fi):
            c.apply(img)
    return img
