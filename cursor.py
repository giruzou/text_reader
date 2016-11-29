# -*- coding: utf-8 -*-

## cursor.py - from Comix
##
## $Id$
##

import gobject
import gtk

NORMAL, GRAB, WAIT = range(3)

class CursorHandler:

    def __init__(self, widget):
        self._widget = widget
        self._timer_id = None
        self._auto_hide = False
        self._current_cursor = NORMAL

    def set_cursor_type(self, cursor):
        if cursor == NORMAL:
            mode = None
        elif cursor == GRAB:
            mode = gtk.gdk.Cursor(gtk.gdk.FLEUR)
        elif cursor == WAIT:
            mode = gtk.gdk.Cursor(gtk.gdk.WATCH)
        else:
            mode = cursor
        self.set_cursor(mode)
        self._current_cursor = cursor
        if self._auto_hide:
            if cursor == NORMAL:
                self._set_hide_timer()
            else:
                self._kill_timer()

    def auto_hide_on(self):
        self._auto_hide = True
        if self._current_cursor == NORMAL:
            self._set_hide_timer()

    def auto_hide_off(self):
        self._auto_hide = False
        self._kill_timer()
        if self._current_cursor == NORMAL:
            self.set_cursor_type(NORMAL)

    def refresh(self):
        if self._auto_hide:
            self.set_cursor_type(self._current_cursor)

    def _set_hide_timer(self):
        self._kill_timer()
        self._timer_id = gobject.timeout_add(2000, self.set_cursor,
            self._get_hidden_cursor())

    def _kill_timer(self):
        if self._timer_id is not None:
            gobject.source_remove(self._timer_id)

    def _get_hidden_cursor(self):
        pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
        color = gtk.gdk.Color()
        return gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)

    def set_cursor(self, mode):
        self._widget.window.set_cursor(mode)
        return False
