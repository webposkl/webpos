import sys, numpy as np
import overlays

FS = 720 * 1280 * 3
HOLD = {4141, 4142}          # the app's list->POS dissolve frames: hold prev clean frame
inp = sys.stdin.buffer
out = sys.stdout.buffer
fi = 0
last = None
while True:
    buf = inp.read(FS)
    if not buf or len(buf) < FS:
        break
    if fi in HOLD and last is not None:
        out.write(last.tobytes())
        fi += 1
        continue
    img = np.frombuffer(buf, np.uint8).reshape(720, 1280, 3).copy()
    res = overlays.render_frame(img, fi)
    res = np.ascontiguousarray(res, dtype=np.uint8)
    last = res
    out.write(res.tobytes())
    fi += 1
out.flush()
sys.stderr.write("processed %d frames\n" % fi)
