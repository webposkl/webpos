import subprocess, sys, numpy as np
from PIL import Image
import overlays

def get_frame(t):
    raw = subprocess.run(
        ["ffmpeg","-v","error","-ss",str(t),"-i","original.mp4",
         "-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],
        capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(720,1280,3).copy()

for t in [float(x) for x in sys.argv[1:]]:
    fi = int(round(t*30))
    img = get_frame(t)
    out = overlays.render_frame(img, fi)
    Image.fromarray(out).save(f"test_{t}.png")
    print("wrote test_%s.png (fi=%d)"%(t,fi))
