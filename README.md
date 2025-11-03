# WebSurface

A Kivy FloatLayout-based widget (WebSurface) that embeds an Ultralight-rendered web surface into a Kivy application. It uses a native shared library (`libwebsurface.so`) via `ctypes` to initialize Ultralight, render HTML to a pixel buffer, and dispatch mouse events back to the Ultralight view. Rendered pixels are uploaded into a Kivy `Texture` and drawn as a `Rectangle`.

## Key features
- Initializes an Ultralight view through a C shared library and sends HTML content as UTF-8 bytes.
- Pulls the rendered pixel buffer each frame, uploads it to a Kivy `Texture` (BGRA), and displays it in a `Rectangle`.
- Schedules regular rendering updates via Kivy's `Clock` at a configurable FPS.
- Translates Kivy touch events into Ultralight coordinates (Y axis inverted) and forwards them to the native library (mouse down / up).
- Provides a `destroy()` method for proper cleanup (unscheduling and native teardown).

## Public API (Python)
`WebSurface(width=200, height=200, html="<html>...</html>", fps=30, **kwargs)`

Parameters:
- `width, height`: initial pixel size of the view and texture.
- `html`: HTML string to load into Ultralight (sent as UTF-8 bytes to the native lib).
- `fps`: update rate for rendering via `Clock.schedule_interval`.

**To be Updated**

