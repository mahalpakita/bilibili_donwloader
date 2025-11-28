from PIL import Image
import sys

src = r"c:\Users\My PC\Desktop\pypy\hakiri.jpeg"
dst = r"c:\Users\My PC\Desktop\pypy\hakiri.ico"

# Open and convert
im = Image.open(src).convert('RGBA')
# Create sizes list for .ico (Windows requires several sizes)
sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
# Resize and save as .ico
im.save(dst, sizes=sizes)
print('Saved', dst)
