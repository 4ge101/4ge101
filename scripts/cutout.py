import os
import sys

from PIL import Image
from rembg import new_session, remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1]
OUT = os.path.join(HERE, "..", "source-cutout.png")

session = new_session("u2netp")          # small model, about 5 MB
cut = remove(Image.open(INP).convert("RGB"), session=session)
cut.save(OUT)
print("wrote", OUT)