# WebPOS Software — "How To Add Products" tutorial (rebranded)

Rebranded/edited version of the original Sales Intellect tutorial for WebPOS Software.

**Deliverable:** `WebPOS_How_To_Add_Products.mp4`
(1280x720, H.264 + AAC stereo, 30 fps, ~2:25.8, web-optimized fast-start)

## What changed
- Sales Intellect branding replaced with WebPOS Software (opening logo, title card, closing screen).
- Product 1: "Coke Can 330ml" -> "Mineral Water 500ml" (form field incl. scroll, saved list, POS).
- Product 2: "Lays Cheese & Onion 325g" -> "Mister Potato Chips BBQ 60g" (same places).
- All categories, SKUs, prices, costs, stock and tutorial steps preserved.
- Original audio removed; new vocal-free corporate/tech instrumental (-20 LUFS, 1.5s fade-in, 2s fade-out).

## Reproduce the render
Requires: ffmpeg, python3 (pillow, numpy), Roboto fonts. Source: `original.mp4`.

```
python3 brand.py                     # -> assets_open/title/close.png
python3 music.py                     # -> music_raw.wav
ffmpeg -i music_raw.wav -af "loudnorm=I=-20:TP=-1.5:LRA=11,afade=t=in:st=0:d=1.5,afade=t=out:st=143.766667:d=2" \
       -t 145.766667 -ar 44100 -ac 2 final_audio.wav
ffmpeg -v error -i original.mp4 -f rawvideo -pix_fmt rgb24 - \
  | python3 process.py \
  | ffmpeg -f rawvideo -pixel_format rgb24 -video_size 1280x720 -framerate 30 -i - \
      -i final_audio.wav -map 0:v:0 -map 1:a:0 \
      -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 \
      -c:a aac -b:a 192k -ar 44100 -ac 2 -movflags +faststart -shortest \
      WebPOS_How_To_Add_Products.mp4
```

## Files
- `brand.py` — WebPOS logo + opening/title/closing cards
- `overlays.py` — overlay engine (scroll-tracked name covers, per-frame bg sampling, brand cards)
- `process.py` — streaming frame processor (stdin RGB -> stdout RGB), holds the list->POS dissolve frames
- `music.py` — synthesized instrumental track
- `ref_barcode.npy` — landmark template used to track the Add Products form scroll
- `verification/` — QC screenshots taken from the exported MP4
