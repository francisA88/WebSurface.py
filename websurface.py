# from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.properties import NumericProperty
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.app import App

import keyboard # for global key listening
from core import *


class WebSurface(FloatLayout):
    _renderer_is_being_updated = False # static value that must be checked to prevent updating the global ultralight renderer for each WebSurface instance. Only one is needed
    # index = NumericProperty(-1)
    invert_vertical_scroll = False # Property to invert vertical mouse scroll direction. Change as you please.
    scroll_delta = 20  # Amount to scroll per scroll event

    def __init__(self, width=200, height=200, html="<html><body><h1>Hi</h1></body></html>", fps=30, **kwargs):
        super().__init__(width=width, height=height, size_hint=[None, None], **kwargs)
        self.current_size = (width, height)

        self.uw = width # Texture width and...
        self.uh = height # ..height
        self.html = html
        self.fps = fps
        Window.bind(on_key_down=self._on_key_down_global,
                    on_key_up=self._on_key_up_global,
                    # on_scroll=self._on_scroll_global,
                    mouse_pos=self._on_mouse_over_global)

        # Track held buttons for mouse-move logic
        self._buttons_held = set()

        self.initWebSurface()

    def initWebSurface(self):
        self.index = lib.initWebSurface(
            c_int(self.uw), 
            c_int(self.uh), 
            c_char_p(bytes(self.html, "utf8"))
        )
        print("INdex: ", self.index)

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

    def focus(self):
        lib.focusView(c_int(self.index))

    def is_focused(self):
        return lib.isFocused(c_int(self.index))
    
    def on_pos(self, instance, value):
        if not hasattr(self, "rect"): return
        self.rect.pos = value

    def update(self, dt):
        if not WebSurface._renderer_is_being_updated:
            lib.renderWebSurface()
            # WebSurface._renderer_is_being_updated = True

        width = c_int()
        height = c_int()
        stride = c_int()
        pixels = lib.getSurfacePixels(self.index, byref(width), byref(height), byref(stride))
        if pixels:
            self.texture.blit_buffer(string_at(pixels, stride.value * height.value), colorfmt='bgra', bufferfmt='ubyte')
            self.rect.texture = self.texture

        lib.releaseSurfacePixels(self.index)
 
    def load_url(self, url):
        ''' Loads the given URL in the web surface. This url could be a file:// scheme or an http:// or https:// scheme '''
        return lib.loadURL(self.index, c_char_p(bytes(url, "utf8")))
    

    ## { Event handlers
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        x, y = touch.pos
        lib.focusView(self.index)
        if 'multitouch_sim' in touch.profile:
            touch.multitouch_sim = False  # Disable multitouch simulation for this touch
        print(f"Touch at: {x}, {y}")
        # print("Rect pos:", self.rect.pos, "Rect size:", self.rect.size, "Widget size:", self.size, "Widget pos:", self.pos)
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            # Translate Kivy touch coordinates to Ultralight coordinates
            ul_x = int(x - self.x)
            ul_y = int(self.uh - (y - self.y))  # Invert Y axis
            print(f"Dispatching to Ultralight at: {ul_x}, {ul_y}")

            btn = "left"  # Default to left button
            if 'button' in touch.profile:
                btn = touch.button
                if btn in button_codes:
                    self._buttons_held.add(btn) 
                    # Dispatch to ultralight         
                    lib.dispatchMouseEvent(self.index, c_int(ul_x), c_int(ul_y), c_int(button_codes[btn]), create_string_buffer(b"down"))
                
                
                elif touch.is_mouse_scrolling:
                    if touch.button == 'scrolldown':
                        dx, dy = 0, self.scroll_delta * ((-1) ** int(self.invert_vertical_scroll))
                    elif touch.button == 'scrollup':
                        dx, dy = 0, self.scroll_delta * ((-1) ** (1 - int(self.invert_vertical_scroll)))
                    elif touch.button == 'scrollleft':
                        dx, dy = -self.scroll_delta, 0
                    elif touch.button == 'scrollright':
                        dx, dy = self.scroll_delta, 0
                    else:
                        dx, dy = 0, 0
                    lib.dispatchScrollEvent(self.index, c_int(dx), c_int(dy))

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        x, y = touch.pos
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            ul_x = int(x - self.x)
            ul_y = int(self.uh - (y - self.y))  # Invert Y axis

            btn = "left"  # Default to left button
            # print(touch.profile)
            # print(touch.button)
            if 'button' in touch.profile:
                btn = touch.button
                # print("UP: ", btn)
                if btn in button_codes and btn in self._buttons_held:
                    self._buttons_held.remove(btn)
                    # Dispatch to Ultralight
                    lib.dispatchMouseEvent(self.index, c_int(ul_x), c_int(ul_y), c_int(button_codes[btn]), create_string_buffer(b"up"))

                # elif touch.is_mouse_scrolling:
                #     print("Touch up: scroll... what do I do with this?")
                    # lib.dispatchScrollEvent()
    
    def _on_key_down_global(self, window, key, scancode, codepoint, modifiers):
        if not self.is_focused():
            return False
        self.on_key_down(key, scancode, codepoint, modifiers)
        return True

    def on_key_down(self, key, scancode, codepoint, modifiers):
        """Triggered for any key press while focused."""
        print(f"Key down: key={key}, code={codepoint}, mods={modifiers}, scancode={scancode}")
        print("Down: ", chr(key))
        # Combines all modifiers and passes it to the Ultralight library
        self.current_mods = make_modmask(modifiers)
        newkey = kivy_to_ultralight_vk(key)
        print("translated key: ", newkey)
        lib.dispatchKeyEvent(c_int(self.index), create_string_buffer(b"down"), newkey, self.current_mods, create_string_buffer(bytes(chr(key), 'utf8')))
        
        if key not in non_printable_keycodes and codepoint is not None and key != 13: # 13 is for the "Enter" key. I have to handle that specially
            lib.dispatchCharEvent(self.index, codepoint)
            pass
        if key == 13:
            print("here")
            lib.dispatchCharEvent(self.index, b"\r\n")
        return True
    
    def _on_key_up_global(self, window, key, scancode):
        if not self.is_focused():
            return False
        self.on_key_up(key, scancode)
        return True

    def on_key_up(self, key, scancode, *args):
        """Triggered when key is released while focused."""
        print(f"Key up: key={key} scancode={scancode}")
        key = kivy_to_ultralight_vk(key)
        lib.dispatchKeyEvent(self.index, create_string_buffer(b"up"), key, self.current_mods, create_string_buffer(bytes(chr(key), 'utf8')))
        self.current_mods = 0

    def _on_scroll_global(self, window, scroll_x, scroll_y, pos):
        pass

    def on_mouse_move(self, x, y, btn):
        # Dispatch mouse event to ultralight with the held buttons
        ul_x = int(x - self.x)
        ul_y = int(self.uh - (y - self.y))  # Invert Y axis
        for b in self._buttons_held:
            lib.dispatchMouseEvent(self.index, c_int(ul_x), c_int(ul_y), c_int(button_codes), create_string_buffer(b"move"))

    def _on_mouse_over_global(self, window, pos):
        for btn in self._buttons_held:
            # Dispatch the mouse over event to Ultralight with the buttons held, if any.
            # For example, `lib.dispatchMouseEvent(tox, toy, button_codes[btn], b"move")`
            x, y = pos
            ul_x = int(x - self.x)
            ul_y = int(self.uh - (y - self.y))  # Invert Y axis
            lib.dispatchMouseEvent(self.index, c_int(ul_x), c_int(ul_y), c_int(button_codes[btn]), create_string_buffer(b"move"))
            

    ## } End Event handlers
    
    def destroy_self(self):
        ''' Destroys this WebSurface instance'''
        try:
            Clock.unschedule(self.update)
            lib.destroySurface(self.index)
            self.canvas.remove(self.rect)
        except Exception as err: print(err)
        # self._destroyed = True
    
    @staticmethod
    def destroy_renderer():
        '''Deactivates and removes the renderer.
        WARNING: If this method is called, you'll have to destroy and recreate all other websurfaces afterwards to reinitialize them!
        Only call this method when you are sure you won't need any other WebSurface instances anymore.'''
        WebSurface._renderer_is_being_updated = False
        lib.destroyRenderer()


# Minimal app for testing
if __name__ == "__main__":
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    class TApp(App):
        def build(self):
            root = FloatLayout()
            w, h = Window.size
            w,h = Window.size[0], int(Window.size[1] / 2)

            self.ws = WebSurface(
                width=w, 
                height=h, 
                pos=[0, Window.height/2],
                html=open("test.html", "r").read(), fps=40)
            # self.ws.pos = 200,200
            # self.ws1 = WebSurface(
            #     width=w,
            #     height=h,
            #     pos=[0,0],
            #     html=open("test.html", "r").read()
            # )
            root.add_widget(self.ws)
            # root.add_widget(self.ws1)
            self.ws1.load_url("https://www.wikipedia.org")

            return root
        
        def on_start(self):
            # self.ws.load_url("https://chatgpt.com/")
            pass

        def on_stop(self):
            self.ws.destroy_self()
            # self.ws1.destroy_self()
            WebSurface.destroy_renderer()


    TApp().run()

