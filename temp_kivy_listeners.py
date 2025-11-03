from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import BooleanProperty

class InputSurface(Widget):
    focused = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Register keyboard and scroll listeners
        Window.bind(on_key_down=self._on_key_down_global,
                    on_key_up=self._on_key_up_global,
                    on_scroll=self._on_scroll_global,
                    mouse_pos=self._on_mouse_over_global)

        # Track held buttons for mouse-move logic
        self._buttons_held = set()

    # --------------------------------------------------------
    # Focus logic placeholder
    # --------------------------------------------------------
    def has_focus(self):
        """Placeholder: determine if this widget currently has focus."""
        return self.focused

    def focus(self):
        """Give widget focus."""
        self.focused = True

    def blur(self):
        """Remove widget focus."""
        self.focused = False

    # --------------------------------------------------------
    # 1. Mouse move (while button held)
    # --------------------------------------------------------
    def on_touch_move(self, touch):
        # Detect left-button move (already handled by Kivy), or our custom
        if 'button' in touch.profile:
            btn = touch.button
            print(touch)
            if btn in ('left', 'middle') and touch.grab_current is self:
                self.on_mouse_move(touch.x, touch.y, btn)
        return super().on_touch_move(touch)

    def on_mouse_move(self, x, y, button):
        """Triggered when left/middle button held and mouse moves."""
        # Replace this print with your Ultralight dispatch
        print(f"Mouse move ({button}) at {x},{y}")

    # --------------------------------------------------------
    # 2. Mouse down (right or middle button)
    # --------------------------------------------------------
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Left button handled by Kivy/touch; handle right & middle here
            if 'button' in touch.profile:
                btn = touch.button
                if btn in ('right', 'middle'):
                    self._buttons_held.add(btn)
                    self.on_mouse_down(touch.x, touch.y, btn)
            # Focus this widget when clicked
            self.focus()
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if 'button' in touch.profile and touch.button in self._buttons_held:
            self._buttons_held.discard(touch.button)
        return super().on_touch_up(touch)

    def on_mouse_down(self, x, y, button):
        """Triggered when right or middle mouse button is pressed."""
        print(f"Mouse down: {button} at {x},{y}")

    # --------------------------------------------------------
    # 3. Key down (character / function / modifier)
    # --------------------------------------------------------
    def _on_key_down_global(self, window, key, scancode, codepoint, modifiers):
        if not self.has_focus():
            return False
        self.on_key_down(key, scancode, codepoint, modifiers)
        return True

    def on_key_down(self, key, scancode, codepoint, modifiers):
        """Triggered for any key press while focused."""
        print(f"Key down: key={key}, code={codepoint}, mods={modifiers}")

    # --------------------------------------------------------
    # 4. Key up
    # --------------------------------------------------------
    def _on_key_up_global(self, window, key, scancode):
        if not self.has_focus():
            return False
        self.on_key_up(key, scancode)
        return True

    def on_key_up(self, key, scancode):
        """Triggered when key is released while focused."""
        print(f"Key up: key={key}")

    # --------------------------------------------------------
    # 5. Scroll wheel
    # --------------------------------------------------------
    def _on_scroll_global(self, window, scroll_x, scroll_y, scroll_type):
        if not self.has_focus():
            return False
        self.on_scroll(scroll_x, scroll_y, scroll_type)
        return True

    def on_scroll(self, dx, dy, scroll_type):
        """Triggered by middle mouse wheel scroll."""
        print(f"Scroll event: dx={dx}, dy={dy}, type={scroll_type}")

    # --------------------------------------------------------
    # 6. Mouse hover (no buttons pressed)
    # --------------------------------------------------------
    def _on_mouse_over_global(self, window, pos):
        if not self.collide_point(*pos):
            return
        # Only trigger hover if no button held
        if not self._buttons_held:
            self.on_mouse_over(*pos)

    def on_mouse_over(self, x, y):
        """Triggered when mouse hovers over widget (no clicks)."""
        print(f"Hover at {x},{y}")
