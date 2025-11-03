# Kivy–Ultralight HTML Renderer: Full Development & Testing Plan

## Phase 1: Core Embedding & Rendering

### Goal
Integrate the Ultralight rendering engine into a C++ shared library usable from Python.

### Tasks
1. **Setup Ultralight SDK**
   - Include Ultralight, AppCore, and WebCore headers.
   - Link against their respective `.a` or `.so` libraries.
   - Implement basic C API wrappers for Python use.

2. **Functions to implement**
   - `init_ultra(int width, int height, const char* html)`
   - `render_ultra()`
   - `get_ultra_pixels(int* width, int* height, int* stride)`
   - `release_ultra_pixels()`
   - `destroy_ultra()`

3. **Memory safety**
   - Ensure pixels are locked only while in use.
   - Prevent race conditions between render and read access.

### Tests
- Render static HTML and confirm valid pixel buffer.
- Validate buffer stride = width * 4 (for BGRA).
- Ensure no segfaults after repeated calls (memory leak test).

---

## Phase 2: Python Bindings

### Goal
Wrap the C functions with `ctypes` in Python.

### Tasks
- Define argument and return types explicitly in Python.
- Test calling `init_ultra`, `render_ultra`, and pixel retrieval.
- Convert pixel buffer into an image using Pillow (PIL).

### Tests
- Confirm pixel data converts to correct image dimensions.
- Display the image via PIL to confirm rendering.
- Check for consistent memory cleanup after multiple renders.

---

## Phase 3: Integration with Kivy

### Goal
Render Ultralight output onto a Kivy `Texture`.

### Tasks
- Create a `Texture` with `colorfmt='bgra'`.
- Upload new pixel data each frame using `blit_buffer()`.
- Use `Clock.schedule_interval` to update regularly.

### Tests
- Display a webpage and confirm dynamic updates.
- Verify correct aspect ratio, scaling, and alpha handling.
- Check that FPS setting (e.g. 30 FPS) matches render rate.

---

## Phase 4: Input Handling (Mouse & Keyboard)

### Goal
Allow full interactivity in rendered HTML.

### Tasks
- Forward Kivy mouse/touch/keyboard events to Ultralight via new C functions:
  - `dispatch_mouse_move(x, y)`
  - `dispatch_mouse_down(x, y, button)`
  - `dispatch_mouse_up(x, y, button)`
  - `dispatch_key_event(type, keycode)`

### Tests
- Clickable buttons respond as expected.
- Typing in input fields works.
- Verify coordinate mapping consistency between Kivy and Ultralight.

---

## Phase 5: JS–Python Bridge

### Goal
Enable JavaScript to call Python functions and vice versa.

### Tasks
- Expose C functions for evaluating JS (`evaluate_script`).
- Add a callback registry to handle JS → Python calls.
- Handle UTF-8 string passing safely between layers.

### Tests
- Run JS from Python and confirm return values.
- Trigger Python callbacks from HTML events.
- Test multiple concurrent callbacks safely.

---

## Phase 6: Performance Optimisation

### Tasks
- Cache textures when only partial updates occur.
- Consider threading for rendering separate from UI loop.
- Test memory footprint and frame latency.

### Tests
- Benchmark render time vs frame rate.
- Ensure zero frame tearing or flickering.
- Stress test with large HTML/CSS content.

---

## Phase 7: Packaging & Distribution

### Tasks
- Create `setup.py` or `pyproject.toml` for the Python wrapper.
- Include precompiled binaries for Linux, Windows, and macOS.
- Document the build process with CMake.

### Tests
- Test installation on clean environments.
- Verify version compatibility with Kivy and Python 3.x.
- Validate import and usage in standalone script.

---

## Phase 8: Release QA

### Tasks
- Add automated integration tests.
- Include demo apps (HTML dashboard, YouTube embed, etc.).
- Final documentation and README with examples.

### Tests
- Run regression suite on all supported OS.
- Validate stability after prolonged runtime.
- Confirm full interactivity and accurate rendering.
