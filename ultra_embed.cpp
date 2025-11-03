#include <AppCore/AppCore.h>
#include <Ultralight/Ultralight.h>
#include <iostream>

using namespace ultralight;
using namespace std;

// Keep handles globally for simplicity
static RefPtr<Renderer> g_renderer;
static RefPtr<View> g_view;

void initPlatform() {
  Platform::instance().set_font_loader(GetPlatformFontLoader());

  Platform::instance().set_file_system(GetPlatformFileSystem("."));

  Platform::instance().set_logger(GetDefaultLogger("ultralight.log"));
}

// Initialize renderer and load HTML
extern "C"{

void init_ultra(int width, int height, const char* html) {
    ViewConfig config;
    config.is_accelerated = false; // Ensure we use CPU renderer

    initPlatform();
    
    g_renderer = Renderer::Create();
    g_view = g_renderer->CreateView(width, height, config, nullptr);

    g_view->LoadHTML(html);
    g_renderer->Update();
    g_renderer->Render();
}

// Force a redraw (useful when you change something)
void render_ultra() {
    g_renderer->Update();
    g_renderer->Render();
    g_renderer->RefreshDisplay(0);
}

// Retrieve the pixel buffer pointer (RGBA8)
const void* get_ultra_pixels(int* width, int* height, int* stride) {
    if (!g_view)
        return nullptr;

    auto surface = g_view->surface();
    *width = surface->width();
    *height = surface->height();
    *stride = surface->row_bytes();

    // return surface->LockPixels();
    BitmapSurface* bitmap_surface = (BitmapSurface*)(surface);
    RefPtr<Bitmap> bitmap = bitmap_surface->bitmap();
    return bitmap->LockPixels();
}

// Release the lock when done
void release_ultra_pixels() {
    if (g_view)
        g_view->surface()->UnlockPixels();
}

void dispatch_mouse_event(int x, int y, int button, const char * evtype) {
    if (g_view) {
        MouseEvent mouseEvent;
        
        string ev(evtype);
        if (ev == "down") {
            mouseEvent.type = MouseEvent::kType_MouseDown;
        } else if (ev == "up") {
            mouseEvent.type = MouseEvent::kType_MouseUp;
        } else {
            mouseEvent.type = MouseEvent::kType_MouseUp; // default/fallback
        }

        MouseEvent::Button buttons[4] = {
            MouseEvent::kButton_None,
            MouseEvent::kButton_Left,
            MouseEvent::kButton_Middle,
            MouseEvent::kButton_Right,
        };
        mouseEvent.button = buttons[button];
        mouseEvent.x = x;
        // Apply vertical flip considering the difference in Kivy's and Ultralight's (0,0) coordinate
        // On second thought, maybe I should do it within Kivy instead
        // mouseEvent.y = (g_view->height()) - y; 
        mouseEvent.y = y;

        g_view->FireMouseEvent(mouseEvent);
    }
}

void dispatch_scroll_event(int delta_x, int delta_y) {
    if (!g_view)
        return;

    ScrollEvent evt;
    evt.delta_x = delta_x;
    evt.delta_y = delta_y;
    evt.type = ScrollEvent::kType_ScrollByPixel;
    g_view->FireScrollEvent(evt);
}


// Cleanup everything
void destroy_ultra() {
    g_view = nullptr;
    g_renderer = nullptr;
}

} // extern "C"
