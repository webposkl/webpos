"""WebPOS Software brand assets: logo mark + opening / title / closing cards.
Clean blue-and-white visual identity for POS software.
Renders 1280x720 PNG cards used to fully replace the Sales Intellect branding."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
RB = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/"
def font(weight, size):
    return ImageFont.truetype(RB + f"Roboto-{weight}.ttf", size)

# Palette
PRIMARY = (0, 76, 166)      # #004CA6  (matches the POS app header blue)
ACCENT  = (25, 132, 225)    # #1984E1
DEEP    = (8, 42, 92)       # deep navy for wordmark
GREY    = (110, 130, 155)   # tagline grey
WHITE   = (255, 255, 255)

def _rounded(draw, box, r, **kw):
    draw.rounded_rectangle(box, radius=r, **kw)

def draw_logo(img, cx, cy, s):
    """Draw the WebPOS badge (rounded blue square + white shopping-cart) centred at
    (cx,cy). `s` is the badge side length. Drawn at 4x then downscaled for smooth AA."""
    S = s * 4
    tile = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    # badge with a subtle two-tone (accent bar on the left edge)
    _rounded(d, [0, 0, S - 1, S - 1], r=int(S * 0.22), fill=PRIMARY)
    _rounded(d, [0, 0, int(S * 0.5), S - 1], r=int(S * 0.22), fill=ACCENT)
    _rounded(d, [int(S * 0.16), 0, S - 1, S - 1], r=int(S * 0.22), fill=PRIMARY)
    # white shopping-cart glyph
    lw = int(S * 0.055)
    def L(p, q):
        d.line([p, q], fill=WHITE, width=lw)
    x0, y0 = int(S * 0.26), int(S * 0.30)   # handle start
    x1 = int(S * 0.40)                        # basket top-left
    xr = int(S * 0.78)                        # basket top-right
    ytop = int(S * 0.40)
    ybot = int(S * 0.62)
    # handle
    L((x0, y0), (x1, y0))
    L((x1, y0), (x1 + int(lw*0.1), ytop))
    # basket (trapezoid)
    L((x1, ytop), (xr, ytop))                 # top rail
    L((x1, ytop), (int(S*0.47), ybot))        # left slant
    L((xr, ytop), (int(S*0.71), ybot))        # right slant
    L((int(S*0.47), ybot), (int(S*0.71), ybot))  # bottom
    # vertical basket ribs
    for fx in (0.53, 0.59, 0.65):
        L((int(S*fx), ytop), (int(S*fx), ybot))
    # wheels
    wr = int(S * 0.045)
    for wx in (0.50, 0.68):
        wy = int(S * 0.70)
        d.ellipse([int(S*wx)-wr, wy-wr, int(S*wx)+wr, wy+wr], fill=WHITE)
    tile = tile.resize((s, s), Image.LANCZOS)
    img.paste(tile, (cx - s // 2, cy - s // 2), tile)

def _center(draw, cx, y, text, fnt, fill, tracking=0):
    if tracking:
        # manual letter spacing
        widths = [draw.textbbox((0,0), ch, font=fnt)[2] for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = cx - total // 2
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += w + tracking
        return
    bb = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (bb[2]-bb[0]) // 2 - bb[0], y), text, font=fnt, fill=fill)

def card_opening():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    draw_logo(img, W // 2, 250, 200)
    _center(d, W // 2, 380, "WebPOS", font("Black", 96), DEEP)
    # "Software" in accent, positioned right after via full-line centering
    _center(d, W // 2, 470, "SOFTWARE", font("Medium", 52), PRIMARY, tracking=18)
    d.line([W//2 - 210, 545, W//2 + 210, 545], fill=(210, 222, 236), width=2)
    _center(d, W // 2, 560, "POINT OF SALE SOFTWARE", font("Regular", 24), GREY, tracking=8)
    img.save("assets_open.png")

def card_title():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    draw_logo(img, W // 2, 175, 128)
    _center(d, W // 2, 300, "HOW TO ADD PRODUCTS IN", font("Medium", 60), PRIMARY, tracking=2)
    _center(d, W // 2, 400, "WEBPOS SOFTWARE", font("Black", 84), DEEP, tracking=2)
    d.line([W//2 - 250, 520, W//2 + 250, 520], fill=ACCENT, width=4)
    img.save("assets_title.png")

def card_closing():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    draw_logo(img, W // 2, 210, 168)
    _center(d, W // 2, 330, "WebPOS", font("Black", 82), DEEP)
    _center(d, W // 2, 425, "SOFTWARE", font("Medium", 44), PRIMARY, tracking=16)
    _center(d, W // 2, 520, "Thanks For Watching! Don't Forget To Subscribe",
            font("Medium", 34), PRIMARY)
    img.save("assets_close.png")

if __name__ == "__main__":
    card_opening()
    card_title()
    card_closing()
    print("brand cards written")
