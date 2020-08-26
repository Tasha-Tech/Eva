
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import cv2
import numpy as np
import os
import getopt, sys
import time
from threading import Thread

surface = None
brush_color = "red"
monitor_width  = 0
monitor_height = 0
video_getter = None
step = 0
pattern = 'board_black'
window = None


class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self):        
        self.stream = cv2.VideoCapture(0, cv2.CAP_V4L)
       
        self.stream.set(3, 1600) # X
        self.stream.set(4, 1200) # Y
        #print('CAP_PROP_AUTO_EXPOSURE: ', self.stream.get(cv2.CAP_PROP_AUTO_EXPOSURE))
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) 
        #print('CAP_PROP_EXPOSURE: ', self.stream.get(cv2.CAP_PROP_EXPOSURE))
        self.stream.set(cv2.CAP_PROP_EXPOSURE, 60)

        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def __del__(self):
        print('Release camera')
        self.stream.release()

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True


def draw_checker_board(cr, first_white):
    x_color = first_white
    size = 80 
    for x in range(0, monitor_width, size):
        y_color = x_color
        for y in range(0, monitor_height, size):            
            if y_color:
                cr.set_source_rgba(1, 1, 1, 1)               
            else:
                cr.set_source_rgba(0, 0, 0, 1)               
                            
            cr.rectangle(x, y, size, size)
            cr.fill()
            y_color = not y_color

        x_color = not x_color

def clear_surface():
    global surface
    global monitor_width
    global monitor_height
    global pattern
    global window      

    cr = cairo.Context(surface)
    print('pattern: ', pattern)
    if pattern == 'board_black':
        draw_checker_board(cr, False)
    elif pattern == 'board_white':
        draw_checker_board(cr, True)        
    elif pattern == 'white':
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(0, 0, monitor_width, monitor_height)
        cr.fill()        
    elif pattern == 'black':
        cr.set_source_rgba(0, 0, 0, 1)
        cr.rectangle(0, 0, monitor_width, monitor_height)
        cr.fill()        
        
    del cr
    window.queue_draw_area(0, 0, monitor_width, monitor_height)

def configure_event_cb(wid, evt):
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


def button_press_event_cb(wid, evt):
    global surface
    global video_getter

    if surface is None:
        return False

    if evt.button == Gdk.BUTTON_PRIMARY:
        print('BUTTON_PRIMARY: ', evt.x, evt.y)
    elif evt.button == Gdk.BUTTON_SECONDARY:    
        configure_event_cb(wid, evt)
        wid.queue_draw()
        image = video_getter.frame
        cv2.imwrite('image.jpg', image)

    return True

def on_key_press_event(widget, event, wid):
    if Gdk.keyval_name(event.keyval) == 'Escape':
        close_window(wid)

def motion_notify_event_cb(wid,evt):
    global surface    

    if surface is None:
        return False

    if evt.state & Gdk.EventMask.BUTTON_PRESS_MASK:
        print('BUTTON_PRESS_MASK: ', evt.x, evt.y)

    return True

def timer():
    global step
    global window
    global pattern

    print('Step: ', step)
    if step == 0:
        pattern = 'board_black'
        clear_surface()
        step += 1      

    elif step == 1:        
        image = video_getter.frame
        cv2.imwrite('board_black.jpg', image)
        pattern = 'board_white'
        clear_surface()
        step += 1        

    elif step == 2:        
        image = video_getter.frame
        cv2.imwrite('board_white.jpg', image)
        step += 1        

    elif step == 3:
        close_window(window)
        
    return True


def close_window(wid):
    global surface    
    global video_getter

    if surface is not None:
        del surface
        surface = None
    
    video_getter.stop()
    del video_getter
    Gtk.main_quit()
    
def on_click_exit(button, wid):
    close_window(wid)

if __name__ == '__main__':
    os.system('sudo modprobe uvcvideo')    
    time.sleep(0.5)
    
    #os.system('v4l2-ctl -d /dev/video0 -c exposure_absolute=200')
    #os.system('v4l2-ctl -d /dev/video0 -c exposure_auto=1')
    #os.system('v4l2-ctl -d /dev/video0 -c white_balance_temperature_auto=0')
    #time.sleep(1)
    
    video_getter = VideoGet().start()

    win = Gtk.Window()
    win.set_title('Drawing Area')
    win.set_position(Gtk.WindowPosition.CENTER)
    win.fullscreen()

    win.set_app_paintable(True)  
    screen = win.get_screen()    

    monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
    scale = monitor.get_scale_factor()
    monitor_width = int(monitor.get_geometry().width / scale)
    monitor_height = int(monitor.get_geometry().height / scale)
    print('Resolution {}x{}'.format(monitor_width, monitor_height))

    visual = screen.get_rgba_visual()       
    if visual != None and screen.is_composited():
        win.set_visual(visual)           
    
    win.connect('destroy',close_window)
    win.connect("key-press-event", on_key_press_event, win)

    grid = Gtk.Grid(column_homogeneous=True, column_spacing=10, row_spacing=10)
    win.add(grid)

    frame = Gtk.Frame()
    frame.set_shadow_type(Gtk.ShadowType.IN)    

    da = Gtk.DrawingArea()
    da.set_hexpand(True)
    da.set_vexpand(True)
    da.set_halign(Gtk.Align.FILL)
    da.set_valign(Gtk.Align.FILL)

    da.connect('draw',draw_cb)
    da.connect('configure-event',configure_event_cb)
    da.connect('motion-notify-event',motion_notify_event_cb)
    da.connect('button-press-event',button_press_event_cb)    
    da.set_events(da.get_events() | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK) 
    frame.add(da)

    grid.attach(frame, 0, 0, 10, 20)

    window = win
    GLib.timeout_add(1000, timer)

    win.show_all()
    Gtk.main()