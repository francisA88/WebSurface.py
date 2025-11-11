#include <AppCore/AppCore.h>
#include <Ultralight/Ultralight.h>
#include <JavaScriptCore/JavaScript.h>
#include <iostream>

#define print std::cout<<

using namespace ultralight;
using namespace std;

// Keep handles globally for simplicity
static RefPtr<Renderer> g_renderer;
// static RefPtr<View> g_view;
static vector<RefPtr<View>> g_views;

void initPlatform() {
  Platform::instance().set_font_loader(GetPlatformFontLoader());

  Platform::instance().set_file_system(GetPlatformFileSystem("."));

  Platform::instance().set_logger(GetDefaultLogger("ultralight.log"));
}

// Initialize renderer and load HTML
extern "C"{

int initWebSurface(int width, int height, const char* html) {
    ViewConfig config;
    config.is_accelerated = false; // Ensure we use CPU renderer

    initPlatform();
    
    if (!g_renderer){
        print "Renderer created" <<endl;
        g_renderer = Renderer::Create();
    }
    
    auto view = g_renderer->CreateView(width, height, config, nullptr);

    g_views.push_back(view);

    view->LoadHTML(html);
    g_renderer->Update();
    g_renderer->Render();

    return g_views.size() - 1; // return index of the created view
}

// Force a redraw (useful when you change something)
void renderWebSurface() {
    g_renderer->Update();
    g_renderer->Render();
    g_renderer->RefreshDisplay(0);
}

// Retrieve the pixel buffer pointer (RGBA8)
const void* getSurfacePixels(int surface_id, int* width, int* height, int* stride) {
    // print "ID: " << surface_id;
    if (surface_id < 0 || surface_id >= g_views.size()){
        print g_views.size() <<endl;
        return nullptr;
    }
    
    RefPtr<View> view = g_views[surface_id];
    if (!view){
        std::cout<<"no vew?\n";
        return nullptr;
    }

    auto surface = view->surface();
    *width = surface->width();
    *height = surface->height();
    *stride = surface->row_bytes();

    // return surface->LoekPixels();
    BitmapSurface* bitmap_surface = (BitmapSurface*)(surface);
    RefPtr<Bitmap> bitmap = bitmap_surface->bitmap();
    return bitmap->LockPixels();
}

// Release the lock when done
void releaseSurfacePixels(int surface_id) {
    if (surface_id < 0 || surface_id >= g_views.size())
        return;
    
    RefPtr<View> view = g_views[surface_id];
    if (view)
        view->surface()->UnlockPixels();
}

void dispatchMouseEvent(int surface_id, int x, int y, int button, const char * evtype) {
    if (surface_id < 0 || surface_id >= g_views.size()) return;
    RefPtr<View> view = g_views[surface_id];

    if (view) {
        MouseEvent mouseEvent;
        
        string ev(evtype);
        if (ev == "down") {
            mouseEvent.type = MouseEvent::kType_MouseDown;
        } else if (ev == "up") {
            mouseEvent.type = MouseEvent::kType_MouseUp;
        } else if (ev == "move") {
            mouseEvent.type = MouseEvent::kType_MouseMoved;
        }
        else{
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

        view->FireMouseEvent(mouseEvent);
    }
}

void dispatchScrollEvent(int surface_id, int delta_x, int delta_y) {
    if (surface_id < 0 || surface_id >= g_views.size())
        return;

    RefPtr<View> view = g_views[surface_id];
    if (!view)
        return;

    ScrollEvent evt;
    evt.delta_x = delta_x;
    evt.delta_y = delta_y;
    evt.type = ScrollEvent::kType_ScrollByPixel;
    view->FireScrollEvent(evt);
}

void dispatchKeyEvent(int surface_id, const char* type, int keycode, int modifiers, const char* character){
    if (surface_id < 0 || surface_id >= g_views.size()) return;

    RefPtr<View> view = g_views[surface_id];
    if (!view->HasInputFocus()) return;
    if (!view) return;
    KeyEvent event;
    
    // std::cout << "mODS" << modifiers <<endl;
    if (string(type) == "down"){
        event.type = KeyEvent::kType_RawKeyDown;
        event.virtual_key_code = keycode;
        // event.native_key_code = 0;
    }
    else if (string(type) == "up"){
        event.type = KeyEvent::kType_KeyUp;
        event.virtual_key_code = keycode;
    }
    
    event.modifiers = modifiers;
    GetKeyIdentifierFromVirtualKeyCode(keycode, event.key_identifier);
    event.native_key_code = 0;
    view->FireKeyEvent(event);
    
}

void dispatchCharEvent(int surface_id, const char* utf8_text) {
    if (surface_id < 0 || surface_id >= g_views.size()) return;
    RefPtr<View> view = g_views[surface_id];
    if (!view->HasInputFocus()) return;
    if (!view) return;

    KeyEvent ev;
    ev.type = KeyEvent::kType_Char;
    // strncpy(ev.text, utf8_text, sizeof(ev.text) - 1);
    ev.text = utf8_text;
    ev.unmodified_text = "d";
    view->FireKeyEvent(ev);
}

bool loadURL(int surface_id, const char* url) {
    if (surface_id < 0 || surface_id >= g_views.size())
        return false;
    g_views[surface_id]->LoadURL(url);
    return true;
}

bool isFocused(int surface_id) {
    if (surface_id < 0 || surface_id >= g_views.size())
        return false;
    RefPtr<View> view = g_views[surface_id];
    if (!view) return false;

    return view->HasFocus();
}

void focusView(int surface_id) {
    if (surface_id < 0 || surface_id >= g_views.size()) return;
    RefPtr<View> view = g_views[surface_id];
    if (!view) return;
    view->Focus();
}

// Cleanup everything
void destroySurface(int surface_id) {
    if (surface_id < 0 || surface_id >= g_views.size()) return;
    RefPtr<View> view = g_views[surface_id];
    view = nullptr;
}

void destroyRenderer(){
    g_renderer = nullptr;
}

const char* evaluateScript(int surface_id, const char* script_text) {
    if (surface_id < 0 || surface_id >= g_views.size()) return nullptr;
    RefPtr<View> view = g_views[surface_id];
    if (!view) return nullptr;

    JSContextRef ctx = *view->LockJSContext();
    JSStringRef script = JSStringCreateWithUTF8CString(script_text);
    JSValueRef exception = nullptr;
    JSValueRef result = JSEvaluateScript(ctx, script, nullptr, nullptr, 1, &exception);
    JSStringRelease(script);

    const char* out_str = nullptr;
    JSStringRef resultStr = nullptr;

    if (exception) {
        resultStr = JSValueToStringCopy(ctx, exception, nullptr);
    } else {
        resultStr = JSValueToStringCopy(ctx, result, nullptr);
    }

    size_t max_size = JSStringGetMaximumUTF8CStringSize(resultStr);
    char* buffer = new char[max_size];
    JSStringGetUTF8CString(resultStr, buffer, max_size);
    JSStringRelease(resultStr);

    return buffer;
}

void free_cstring(const char* str) {
    delete[] str;
}

} // extern "C"
