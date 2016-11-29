# -*- coding: utf-8 -*-

## event.py
##
## $Id$
##

from math import pi as PI
import os
import sys
import gtk
import cairo

from cursor import CursorHandler
import goto_page

class EventHandler:

    def __init__(self, tview, page, cfg):
        self._tview = tview; self._page = page; self._cfg = cfg
        ## Event
        self.connect(tview.drawingarea, 'configure_event')
        self.connect(tview.drawingarea, 'expose_event')
        self.connect(tview, 'delete_event')
        tview.set_events( gtk.gdk.BUTTON1_MOTION_MASK | gtk.gdk.BUTTON2_MOTION_MASK |
                          gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK |
                          gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.KEY_PRESS_MASK )
                          ##gtk.gdk.ALL_EVENTS_MASK
        self.connect(tview, 'motion_notify_event')
        ## Shortcut key
        self.accel_key()
        ## Auto hide mouse cursor
        self._cursor_handler = CursorHandler(tview.vbox)
        self._cursor_handler.auto_hide_on()
        ## Font matrix
        self.default_font_matrix = None; self.font_extents = None
        self.font_matrix_cache = {}
        self.font_matrix_cache_max_size = 10000

    def connect(self, widget, event):
        func = getattr(self, event, None)
        if func: widget.connect(event, func)

    def delete_event(self, widget, event):
        self.quit()

    def motion_notify_event(self, widget, event):
        self._cursor_handler.refresh()

    # Resize
    def configure_event(self, widget, event):
        (width, height) = event.width, event.height
        w_cfg = self._cfg.window; tview = self._tview
        if width == tview.win_width and height == tview.win_height:
            return
        page = self._page; tview = self._tview
        ## 本来であれば必要のない処理
        if width < tview.min_width: width = tview.min_width
        if width > tview.max_width: width = tview.max_width
        if height < tview.min_height: height = tview.min_height
        if height > tview.max_height: height = tview.max_height
        if width != event.width or height != event.height:
            tview.win_width = width;tview.win_height = height
            widget.set_size_request(width, height)
            return
        ##
        inc_lpp = int((width-tview.win_width)/(w_cfg.text_font_size+w_cfg.line_gap))
        inc_cpl = int((height-tview.win_height)/(w_cfg.text_font_size+w_cfg.char_gap))
        if inc_lpp == 0 and inc_cpl == 0: return
        self._page.reset_page(page.lpp+inc_lpp, page.cpl+inc_cpl)
        (tview.win_width, tview.win_height) = (width, height)
        tview.draw_start_positon = (
            width-(w_cfg.text_font_size+w_cfg.right_margin),
            w_cfg.top_margin+w_cfg.text_font_size )
        widget.queue_draw()

    # Move page
    def page_callback(self, func0, *args):
        func = getattr(self._page, func0, None)
        if func is None:
            (m, f) = func0.split('.', 1)
            if len(m) > 0 and len(f) > 0 and m in sys.modules:
                func = getattr(eval(m), f, None)
        if func:
            func() if args is () else apply(func, args)
            self._tview.queue_draw()

    # Shortcut key
    def accel_key(self):
        p = self._page; tview = self._tview
        ag = gtk.AccelGroup(); tview.add_accel_group(ag)
        p_cb = self.page_callback
        ag.connect_group(gtk.keysyms.space, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('next_page'))
        ag.connect_group(gtk.keysyms.Left, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('next_page'))
        ag.connect_group(gtk.keysyms.b, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('prev_page'))
        ag.connect_group(gtk.keysyms.Right, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('prev_page'))
        ag.connect_group(gtk.keysyms.Page_Up, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('goto_page', p.cpage()-10))
        ag.connect_group(gtk.keysyms.Page_Down, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('goto_page', p.cpage()+10))
        ag.connect_group(gtk.keysyms.Home, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('goto_first_page'))
        ag.connect_group(gtk.keysyms.End, 0, gtk.ACCEL_VISIBLE,
                         lambda *args: p_cb('goto_last_page'))
        ag.connect_group(gtk.keysyms.g, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE,
                         (lambda *args: p_cb('goto_page.open_dialog', tview, p)))
        ag.connect_group(gtk.keysyms.q, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE,
                         self.quit)

    # Redraw
    def expose_event(self, widget, event):
        self.show_page(widget, event)

    # Show page
    def show_page(self, widget, event):
        w_cfg = self._cfg.window; tview = self._tview
        ctx = widget.window.cairo_create()
        ctx.select_font_face(w_cfg.text_font_family,
                             w_cfg.text_font_style, w_cfg.text_font_weight)
        ctx.set_font_size(w_cfg.text_font_size)
        ctx.set_source_color(w_cfg.text_color)
        if self.default_font_matrix is None:
            self.default_font_matrix = ctx.get_font_matrix()
        if self.font_extents is None:
            self.font_extents = ctx.font_extents()

        ## Set start position
        apply(ctx.translate, tview.draw_start_positon)
        ctx.move_to(0, 0)

        p = self._page; tbuf = p.get_buffer()
        h = w_cfg.text_font_size+w_cfg.char_gap
        w = w_cfg.text_font_size+w_cfg.line_gap
        ## Draw page text
        for (start, end) in p:
            if (end - start) > 0:
                for i, char in enumerate(tbuf[start:end]):
                    ctx.move_to(0, i*h)
                    self.set_font_matrix(ctx, char)
                    ctx.show_text(char)
            ctx.move_to(0, 0); ctx.translate(-w, 0); ctx.move_to(0, 0)
        self.update_header()

    def set_font_matrix(self, ctx, char):
        # Search cache
        if ( self.font_matrix_cache.has_key(char) ):
            ctx.set_font_matrix(self.font_matrix_cache[char])
            return
        # Set font matrix to default
        w_cfg = self._cfg.window
        font_matrix_dict = self._cfg.font_matrix_dict
        ctx.set_font_matrix(self.default_font_matrix)
        proc = None
        if font_matrix_dict:
            for (reg, proc) in font_matrix_dict:
                if reg.match(char): break
        if proc and len(proc) > 0:
            fs = w_cfg.text_font_size
            # Normalize with font size
            (x, y, w, h, addx, addy) = ctx.text_extents(char)
            (x, y, w, h, addx, addy) = (x/fs, y/fs, w/fs, h/fs, addx/fs, addy/fs)
            ##(x, y, w, h, addx, addy) = map(lambda t:t/fs, ctx.text_extents(char))
            m = apply(cairo.Matrix, self.default_font_matrix)
            proc = proc.replace('rot(','m.rotate(').replace('move(','m.translate(')
            try:
                exec(proc)
            except:
                pass
            ctx.set_font_matrix(m)
            # Caching
            if len(self.font_matrix_cache) < self.font_matrix_cache_max_size:
                self.font_matrix_cache[char] = m

    # Update header text
    def update_header(self):
        page = self._page; file = self._cfg.text_file
        header_fmt = self._cfg.window.header_format
        format = {'%p': lambda *x:page.cpage(),
                  '%P': lambda *x:page.num_pages(),
                  '%f': lambda *x:os.path.basename(file)}
        for fmt in format:
            header_fmt = header_fmt.replace(fmt, str(format[fmt]()))
        self._tview.header.set_text(header_fmt)

    def quit(self, *args):
        self._page.save_status()
        self._tview.save_status()
        self._cfg.save_status()
        gtk.main_quit()
