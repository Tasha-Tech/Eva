
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

surface = None
brush_color = "red"

def clear_surface():
    global surface
    cr = cairo.Context(surface)
    cr.set_source_rgba(0, 0, 0, 0)
    cr.paint()    
    del cr


def configure_event_cb(wid,evt):
    global surface

    if surface is not None:
        del surface
        surface = None

    win = wid.get_window()
    width = wid.get_allocated_width()
    height = wid.get_allocated_height()

    
    surface = win.create_similar_surface(
       cairo.CONTENT_COLOR_ALPHA,
        width,
        height)        

    clear_surface()
    return True


def draw_cb(wid, cr):
    global surface
    cr.set_source_surface(surface,0,0)
    cr.paint()
    return False


def draw_brush(wid, x, y):
    global surface
    global brush_color

    cr = cairo.Context(surface)
    if brush_color == "red":
        cr.set_source_rgb(1, 0, 0)
    elif brush_color == "green":
        cr.set_source_rgb(0, 1, 0)
    elif brush_color == "blue":
        cr.set_source_rgb(0, 0, 1)
    else:
        cr.set_source_rgb(1, 1, 1)

    cr.rectangle(x-3, y-3, 6, 6)
    cr.fill()
   
    del cr

    wid.queue_draw_area(x-3, y-3, 6, 6)


def button_press_event_cb(wid,evt):
    global surface

    if surface is None:
        return False

    if evt.button == Gdk.BUTTON_PRIMARY:
        draw_brush(wid, evt.x, evt.y)
    elif evt.button == Gdk.BUTTON_SECONDARY:
        #clear_surface()
        configure_event_cb(wid, evt)
        wid.queue_draw()

    return True


def motion_notify_event_cb(wid,evt):
    global surface

    if surface is None:
        return False

    if evt.state & Gdk.EventMask.BUTTON_PRESS_MASK:
        draw_brush(wid, evt.x, evt.y)

    return True


def close_window(wid):
    global surface

    if surface is not None:
        del surface
        surface = None

    Gtk.main_quit()

def on_click_me_clicked(button, color):
    global brush_color
    print("Clicked", color)
    brush_color = color

if __name__ == '__main__':
    win = Gtk.Window()
    win.set_title('Drawing Area')
    win.set_position(Gtk.WindowPosition.CENTER)
    win.set_default_size(800, 600)
    #win.maximize()

    win.set_app_paintable(True)  
    screen = win.get_screen()        
    visual = screen.get_rgba_visual()       
    if visual != None and screen.is_composited():
        win.set_visual(visual)           
    
    win.connect('destroy',close_window)
    win.set_border_width(20)

    grid = Gtk.Grid(column_homogeneous=True, column_spacing=10, row_spacing=10)
    win.add(grid)

    frame = Gtk.Frame()
    frame.set_shadow_type(Gtk.ShadowType.IN)    

    da = Gtk.DrawingArea()
    da.set_size_request(800,600)    
    da.connect('draw',draw_cb)
    da.connect('configure-event',configure_event_cb)
    da.connect('motion-notify-event',motion_notify_event_cb)
    da.connect('button-press-event',button_press_event_cb)    
    da.set_events(da.get_events() | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK) 
    frame.add(da)

    grid.attach(frame, 0, 0, 10, 20)
    
    red_button = Gtk.Button.new_with_label(label="Red")
    red_button.connect("clicked", on_click_me_clicked, "red")    

    green_button = Gtk.Button.new_with_label(label="Green")
    green_button.connect("clicked", on_click_me_clicked, "green")    

    blue_button = Gtk.Button.new_with_label(label="Blue")
    blue_button.connect("clicked", on_click_me_clicked, "blue")    

    grid.attach(red_button,0, 21, 1, 1)
    grid.attach(green_button,1, 21, 1, 1)
    grid.attach(blue_button,2, 21, 1, 1)

    win.show_all()
    Gtk.main()