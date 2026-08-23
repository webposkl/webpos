import subprocess, sys, numpy as np
from PIL import Image
import importlib, overlays; importlib.reload(overlays)

t0, t1 = float(sys.argv[1]), float(sys.argv[2])
saves = [float(x) for x in sys.argv[3:]]
proc = subprocess.Popen(
    ["ffmpeg","-v","error","-i","original.mp4","-f","rawvideo","-pix_fmt","rgb24","-"],
    stdout=subprocess.PIPE)
FS = 720*1280*3
f0 = int(round(t0*30)); f1 = int(round(t1*30))
# skip to f0
saveset = {int(round(t*30)): t for t in saves}
fi = 0
while fi <= f1:
    buf = proc.stdout.read(FS)
    if not buf: break
    if fi < f0:
        fi += 1; continue
    img = np.frombuffer(buf, np.uint8).reshape(720,1280,3).copy()
    out = overlays.render_frame(img, fi)
    if fi in saveset:
        Image.fromarray(out).save(f"seq_{saveset[fi]}.png")
        print("saved seq_%s.png fi=%d"%(saveset[fi], fi))
    fi += 1
proc.stdout.close(); proc.wait()
