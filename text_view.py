# -*- coding: utf-8 -*-

## main_window.py
##
## $Id$
##

import sys
import pango
import gtk
import pangocairo

from constants import APPLICATION_NAME
from event import EventHandler
from util import *

## 
##
class TView(gtk.Window):

    def __init__(self, page, cfg):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.w_cfg = w_cfg = cfg.window
        self.set_title(APPLICATION_NAME)
        ## Header
        box = gtk.EventBox()
        box.modify_bg(gtk.STATE_NORMAL, w_cfg.header_bg_color)
        self.header = gtk.Label()
        header_font = pango.FontDescription(w_cfg.header_font)
        self.header.modify_font(header_font)
        self.header.modify_fg(gtk.STATE_NORMAL, w_cfg.header_fg_color)
        self.header.set_padding(0, int((header_font.get_size()/pango.SCALE)*0.2))
        box.add(self.header)
        ## Separator
        separator = gtk.HSeparator()
        separator.set_size_request(-1, 0)
        separator.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#000000'))
        ## Text area
        self.drawingarea = gtk.DrawingArea()
        self.drawingarea.modify_bg(gtk.STATE_NORMAL, w_cfg.background_color)
        ## Layout
        self.vbox = gtk.VBox()
        self.vbox.pack_start(box, expand=False, fill=False)
        self.vbox.pack_start(separator, expand=False, fill=False)
        self.vbox.pack_start(self.drawingarea)
        self.add(self.vbox)
        ## Resize
        line_1 = w_cfg.text_font_size+w_cfg.line_gap
        char_1 = w_cfg.text_font_size+w_cfg.char_gap
        ## Decide window size
        self.win_width = (page.lpp*line_1-w_cfg.line_gap+
                          w_cfg.left_margin+w_cfg.right_margin)
        ## 禁則処理用に一列追加
        self.win_height = ((page.cpl+1)*char_1-w_cfg.char_gap+
                           w_cfg.top_margin+w_cfg.bottom_margin)
        ## 描画開始位置
        self.draw_start_positon = (
            self.win_width-(w_cfg.text_font_size+w_cfg.right_margin),
            w_cfg.top_margin+w_cfg.text_font_size )
        ## Resize hints
        base_width = w_cfg.left_margin+w_cfg.right_margin-w_cfg.line_gap
        base_height = w_cfg.top_margin+w_cfg.bottom_margin-w_cfg.char_gap
        screen = gtk.gdk.Screen()
        max_width = screen.get_width()
        max_height = screen.get_height()-self.header.size_request()[1]
        max_lpp = int((max_width-(w_cfg.left_margin+w_cfg.right_margin)+w_cfg.line_gap)/line_1)
        max_cpl = int((max_height-(w_cfg.top_margin+w_cfg.bottom_margin)+w_cfg.char_gap)/char_1)-1
        self.max_width = max_lpp*line_1+base_width
        self.max_height = max_cpl*char_1+base_height
        self.min_width = int(max_lpp*0.25)*line_1+base_width
        self.min_height = int(max_cpl*0.25)*char_1+base_height
        self.set_geometry_hints(self.drawingarea,
                                self.min_width, self.min_height,
                                self.max_width, self.max_height,
                                base_width, base_height, line_1, char_1)
        self.drawingarea.set_size_request(self.win_width, self.win_height)
        ## Event handler
        EventHandler(self, page, cfg)
        ## Show all
        self.show_all()
        self.move(w_cfg.win_x, w_cfg.win_y)

    def save_status(self):
        w_cfg = self.w_cfg
        (w_cfg.win_x, w_cfg.win_y) = self.get_position()
