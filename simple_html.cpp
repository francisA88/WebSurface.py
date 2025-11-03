#include <AppCore/AppCore.h>
#include <Ultralight/Ultralight.h>
#include <iostream>

using namespace ultralight;
using namespace std;

// Keep handles globally for simplicity
static RefPtr<Renderer> g_renderer;
static RefPtr<View> g_view;

void initPlatform() {
  ///
  /// Use the OS's native font loader
  ///
  Platform::instance().set_font_loader(GetPlatformFontLoader());

  ///
  /// Use the OS's native file loader, with a base directory of "."
  /// All file:/// URLs will load relative to this base directory.
  ///
  Platform::instance().set_file_system(GetPlatformFileSystem("."));

  ///
  /// Use the default logger (writes to a log file)
  ///
  Platform::instance().set_logger(GetDefaultLogger("ultralight.log"));
}

// Initialize renderer and load HTML
void init_ultra(int width, int height, const char* html) {
    
    ViewConfig config;
    config.is_accelerated = false; // Ensure we use CPU renderer
    initPlatform();
    cout << "Test\n";
    g_renderer = Renderer::Create();
    cout << "Test2\n";
    g_view = g_renderer->CreateView(width, height, config, nullptr);

    g_view->LoadHTML(html);
    g_renderer->Update();
    g_renderer->Render();
}

// Force a redraw (useful when you change something)
void render_ultra() {
    g_renderer->Update();
    g_renderer->Render();
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

// Cleanup everything
void destroy_ultra() {
    g_view = nullptr;
    g_renderer = nullptr;
}

int main() {
    // Example usage
    init_ultra(800, 600, "<html><body><h1>Hello, world!</h1></body></html>");
    render_ultra();

    int width, height, stride;
    const void* pixels = get_ultra_pixels(&width, &height, &stride);
    std::cout<<"DID something here";
    if (pixels) {
        // Do something with the pixel data
        std::cout << "Got pixel data: " << width << "x" << height << " stride: " << stride << std::endl;
    }
    release_ultra_pixels();
    // destroy_ultra();

    return 0;
}