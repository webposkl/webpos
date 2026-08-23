"""WebPOS Software brand cards built around the customer's exact logo.
Renders 1280x720 opening / title / closing cards that fully replace the original
Sales Intellect branding. The logo artwork itself is used unmodified (only
tight-cropped from the supplied file and placed / scaled)."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
RB = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/"
def font(weight, size):
    return ImageFont.truetype(RB + f"Roboto-{weight}.ttf", size)

# palette derived from the logo
NAVY  = (38, 38, 74)      # WEBPOS wordmark navy
RED   = (226, 20, 26)     # logo red accent
GREY  = (120, 130, 150)
WHITE = (255, 255, 255)

LOGO_FULL = Image.open("webpos_full.png").convert("RGB")   # mark + WEBPOS
LOGO_MARK = Image.open("webpos_mark.png").convert("RGB")   # mark only

def paste_scaled(img, logo, target_w, cx, top):
    w, h = logo.size
    nh = int(h * target_w / w)
    l = logo.resize((target_w, nh), Image.LANCZOS)
    img.paste(l, (cx - target_w // 2, top))
    return top + nh

def center(draw, cx, y, text, fnt, fill, tracking=0):
    if tracking:
        widths = [draw.textbbox((0, 0), ch, font=fnt)[2] for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = cx - total // 2
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=fnt, fill=fill); x += w + tracking
        return
    bb = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (bb[2]-bb[0]) // 2 - bb[0], y), text, font=fnt, fill=fill)

def card_opening():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    bottom = paste_scaled(img, LOGO_FULL, 430, W // 2, 70)
    center(d, W // 2, bottom + 24, "SOFTWARE", font("Medium", 52), NAVY, tracking=20)
    d.line([W//2 - 220, bottom + 100, W//2 + 220, bottom + 100], fill=RED, width=3)
    center(d, W // 2, bottom + 116, "POINT OF SALE SOFTWARE", font("Regular", 24), GREY, tracking=8)
    img.save("assets_open.png")

def card_title():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    paste_scaled(img, LOGO_MARK, 190, W // 2, 60)
    center(d, W // 2, 320, "HOW TO ADD PRODUCTS IN", font("Medium", 60), NAVY, tracking=2)
    center(d, W // 2, 418, "WEBPOS SOFTWARE", font("Black", 84), NAVY, tracking=2)
    d.line([W//2 - 250, 540, W//2 + 250, 540], fill=RED, width=4)
    img.save("assets_title.png")

def card_closing():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    bottom = paste_scaled(img, LOGO_FULL, 360, W // 2, 70)
    center(d, W // 2, bottom + 20, "SOFTWARE", font("Medium", 46), NAVY, tracking=18)
    center(d, W // 2, bottom + 110, "Thanks For Watching! Don't Forget To Subscribe",
           font("Medium", 34), RED)
    img.save("assets_close.png")

if __name__ == "__main__":
    card_opening(); card_title(); card_closing()
    print("brand cards written with WebPOS logo")
