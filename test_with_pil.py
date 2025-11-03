from ctypes import *
from PIL import Image

print("Loading Ultralight library...")
lib = cdll.LoadLibrary("./libultraembed.so")
print("Library loaded.")

# Initialize Ultralight
html = c_char_p(b"<html><body style='background-color:white; color:black;'><h1>Hello Ultralight!</h1></body></html>")
lib.init_ultra(512, 512, html)
print("Ultralight initialized.")

# Render one frame
lib.render_ultra()
print("Ultralight rendered.")

# Get pixel buffer info
width = c_int()
height = c_int()
stride = c_int()
print("Getting pixels...")
pixels = lib.get_ultra_pixels(byref(width), byref(height), byref(stride))
print(width.value, height.value, stride.value, pixels)

# Convert to Python bytes
w, h, s = width.value, height.value, stride.value
size = s * h
buf_ptr = cast(pixels, POINTER(c_ubyte * size))
data = bytes(buf_ptr.contents)

# Release Ultralight lock
lib.release_ultra_pixels()
print("Got here safely.")

# Destroy Ultralight instance
lib.destroy_ultra()
print("Ultralight destroyed.")

# --- Now interpret and display with PIL ---

# Try BGRA first (Ultralight default)
try:
    img = Image.frombuffer("RGBA", (w, h), data, "raw", "BGRA", s, 1)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)  # correct vertical flip
    img.show()
    print("Image displayed (BGRA).")
except Exception as e:
    print("BGRA failed:", e)
    # Try RGBA fallback
    img = Image.frombuffer("RGBA", (w, h), data, "raw", "RGBA", s, 1)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.show()
    print("Image displayed (RGBA).")
