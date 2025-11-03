# ultralight_widget.py
from ctypes import (
    byref,
    cdll,
    cast,
    create_string_buffer,
    c_char_p,
    c_int,
    c_void_p,
    POINTER,
    string_at,
)
import tracemalloc

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.app import App

# Load your shared library
lib = cdll.LoadLibrary("./libultraembed.so")
lib.init_ultra.argtypes = [c_int, c_int, c_void_p]  # html as const char*
lib.render_ultra.argtypes = []
lib.get_ultra_pixels.argtypes = [POINTER(c_int), POINTER(c_int), POINTER(c_int)]
lib.get_ultra_pixels.restype = c_void_p
lib.release_ultra_pixels.argtypes = []
lib.destroy_ultra.argtypes = []

class UltraWidget(FloatLayout):
    def __init__(self, width=200, height=200, html="<html><body><h1>Hi</h1></body></html>", fps=30, **kwargs):
        super().__init__(width=width, height=height, size_hint=[None,None], **kwargs)
        self.current_size = (width, height)

        self.uw = width # Texture width and...
        self.uh = height # ..height
        self.html = html
        self.fps = fps
        # self._destroyed = False

        self.init_ultralight()

    def init_ultralight(self):
        # init ultralight (pass bytes)
        # self.destroy()
        # lib.init_ultra(c_int(self.uw), c_int(self.uh), c_void_p(cast(create_string_buffer(self.html), c_void_p).value))
        lib.init_ultra(
            c_int(self.uw), 
            c_int(self.uh), 
            c_char_p(bytes(self.html, "utf8"))
        )
        
        self.texture = Texture.create(size=(self.uw, self.uh), colorfmt='bgra')
        print(dir(self.texture))
        self.texture.flip_vertical() 
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.texture)
    
        Clock.schedule_interval(self.update, 1/self.fps)

    def on_size(self, instance, value):
        if not hasattr(self, "rect"): return
        self.uw, self.uh = value
        self.texture = Texture.create(size=(self.uw, self.uh), colorfmt='bgra')
        self.rect.size = value
        # self.destroy()
        # self.init_ultralight()
    
    def on_pos(self, instance, value):
        if not hasattr(self, "rect"): return
        self.rect.pos = value

    def update(self, dt):
        lib.render_ultra()

        width = c_int()
        height = c_int()
        stride = c_int()
        pixels = lib.get_ultra_pixels(byref(width), byref(height), byref(stride))
        # print(pixels)
        if pixels:
            self.texture.blit_buffer(string_at(pixels, stride.value * height.value), colorfmt='bgra', bufferfmt='ubyte')
            self.rect.texture = self.texture

        lib.release_ultra_pixels()
 
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        x, y = touch.pos
        print(f"Touch at: {x}, {y}")
        print("Rect pos:", self.rect.pos, "Rect size:", self.rect.size, "Widget size:", self.size, "Widget pos:", self.pos)
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            # Translate Kivy touch coordinates to Ultralight coordinates
            ul_x = int(x - self.x)
            ul_y = int(self.uh - (y - self.y))  # Invert Y axis
            print(f"Dispatching to Ultralight at: {ul_x}, {ul_y}")

            lib.dispatch_mouse_event(c_int(ul_x), c_int(ul_y), c_int(1), create_string_buffer(b"down"))

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        x, y = touch.pos
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            ul_x = int(x - self.x)
            ul_y = int(self.uh - (y - self.y))  # Invert Y axis
            lib.dispatch_mouse_event(c_int(ul_x), c_int(ul_y), c_int(1), create_string_buffer(b"up"))

    def destroy(self):
        try:
            Clock.unschedule(self.update)
            lib.destroy_ultra()
            self.canvas.remove(self.rect)
        except Exception as err: print(err)
        # self._destroyed = True

# Minimal app for testing
if __name__ == "__main__":
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    class TApp(App):
        def build(self):
            root = BoxLayout()
            w, h = 400, 700

            self.uw = UltraWidget(
                width=w, 
                height=h, 
                html=open("test.html", "r").read(), fps=40)
            self.uw.pos = 200,200
            root.add_widget(self.uw)

            

            return root
        
        def on_stop(self):
            self.uw.destroy()

        def on_start(self):
            print("here")
            def move_view(dt):
                # self.uw.size = 500, 550
                self.uw.pos = 100,100 
                print(self.uw.pos, self.uw.size)
                print("View moved")

            Clock.schedule_once(move_view, 4)

    TApp().run()

