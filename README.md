# embed_texture_kivy.websurface

A Kivy FloatLayout-based widget (UltraWidget) that embeds an Ultralight-rendered web surface into a Kivy application. It uses a native shared library (`libultraembed.so`) via `ctypes` to initialize Ultralight, render HTML to a pixel buffer, and dispatch mouse events back to the Ultralight view. Rendered pixels are uploaded into a Kivy `Texture` and drawn as a `Rectangle`.

## Key features
- Initializes an Ultralight view through a C shared library and sends HTML content as UTF-8 bytes.
- Pulls the rendered pixel buffer each frame, uploads it to a Kivy `Texture` (BGRA), and displays it in a `Rectangle`.
- Schedules regular rendering updates via Kivy's `Clock` at a configurable FPS.
- Translates Kivy touch events into Ultralight coordinates (Y axis inverted) and forwards them to the native library (mouse down / up).
- Provides a `destroy()` method for proper cleanup (unscheduling and native teardown).

## Public API (Python)
`UltraWidget(width=200, height=200, html="<html>...</html>", fps=30, **kwargs)`

Parameters:
- `width, height`: initial pixel size of the view and texture.
- `html`: HTML string to load into Ultralight (sent as UTF-8 bytes to the native lib).
- `fps`: update rate for rendering via `Clock.schedule_interval`.

Important behavior:
- The `Texture` is created with `colorfmt='bgra'` and `flip_vertical()` is called to match Ultralight's coordinate convention.
- `on_size` recreates the `Texture` and resizes the `Rectangle`, but does not automatically reinitialize Ultralight (reinitialization is present in code but commented out).
- `on_touch_down` / `on_touch_up` map Kivy coordinates to Ultralight coordinates:
    - `ul_x = int(x - widget.x)`
    - `ul_y = int(widget_height - (y - widget.y))`  (Y axis inverted)
    - Calls native `dispatch_mouse_event` with small C-strings like `b"down"` or `b"up"`.

## Native library expectations (ctypes signatures)
The module expects a C shared library `libultraembed.so` exposing these functions:

C signatures (conceptual)
```c
void init_ultra(int width, int height, const char *html_bytes);
void render_ultra(void);
void *get_ultra_pixels(int *out_width, int *out_height, int *out_stride); // returns BGRA pointer
void release_ultra_pixels(void);
void destroy_ultra(void);
void dispatch_mouse_event(int x, int y, int button, const char *action); // action e.g. "down" or "up"
```

Python ctypes mappings used in the module match the above signatures (`c_int`, `c_char_p`, pointers, etc.).

## Rendering and memory details
- `get_ultra_pixels` returns a pointer to pixel data (BGRA) and fills `out_width`, `out_height`, and `out_stride`.
- The buffer is read using `ctypes.string_at(pixels, stride * height)` and uploaded to the Kivy `Texture` with:
    - `texture.blit_buffer(..., colorfmt='bgra', bufferfmt='ubyte')`
- After uploading, `release_ultra_pixels()` is called so the native side can free or recycle the buffer.
- The widget assumes the Texture matches width/height/stride reported by the native library.

## Usage example
- Place `libultraembed.so` in the application working directory.
- Create and add `UltraWidget` to a layout:
```python
uw = UltraWidget(width=400, height=700, html=open("test.html").read(), fps=40)
root.add_widget(uw)
# On application stop:
uw.destroy()
```

## Notes and caveats
- The module uses `ctypes` and depends on the correctness of the native shared library. Mismatched signatures or incorrect memory ownership on the native side can crash the application.
- Resizing recreates the Kivy `Texture` but does not reinitialize the Ultralight view on the native side by default; dynamic resizing may require reinitialization.
- Touch coordinate mapping assumes the widget's (0,0) corresponds to the lower-left of the Ultralight view (hence the Y inversion).
- Depends on `kivy.core.window`, `kivy.graphics`, and `kivy.clock`.

