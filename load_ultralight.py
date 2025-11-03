from ctypes import *
import os
os.environ["KIVY_IMAGE"] = "sdl2"
from kivy.graphics.texture import Texture
from kivy.base import runTouchApp
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window

print("Loading Ultralight library...")
lib = cdll.LoadLibrary("./libultraembed.so")
print("Library loaded.")

html = c_char_p(b"<html><body><h1>Hello Ultralight!</h1></body></html>")
lib.init_ultra(400, 400, html)
print("Ultralight initialized.")

lib.render_ultra()

print("Ultralight rendered.")
width = c_int()
height = c_int()
stride = c_int()
print("Getting pixels...")
pixels = lib.get_ultra_pixels(byref(width), byref(height), byref(stride))
print(width.value, height.value, stride.value, pixels)
print(width.value, height.value, stride.value, pixels)

lib.release_ultra_pixels()
print("Got here safely.")
lib.destroy_ultra()
print("Ultralight destroyed.")

texture = Texture.create(size=(width.value, height.value), colorfmt='bgra')
texture.blit_buffer(string_at(pixels, stride.value * height.value), colorfmt='rgba', bufferfmt='ubyte')

image = CoreImage(texture)
image.save("./output.png")  

runTouchApp()