# -*- coding: utf-8 -*-

## goto_page.py - from comix
##
## $Id$
##

import sys
import gtk

_dialog = None

class _GotoPageDialog(gtk.Dialog):

  def __init__(self, window, page):
      self._win = window; self._page = page
      gtk.Dialog.__init__(self, 'Goto Page', window, 0,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
      self.set_resizable(False)
      self.connect('response', self.response)
      self.set_default_response(gtk.RESPONSE_OK)
      self.button_page_spin = gtk.SpinButton(gtk.Adjustment(1, 1, 1000, 1, 1, page_size=0),
                              climb_rate=0.0, digits=0)
      self.button_page_spin.set_range(1, page.num_pages())
      self.button_page_spin.set_value(page.cpage())
      self.button_page_spin.connect('activate', self.set_page)
      hbox = gtk.HBox(False, 0)
      hbox.set_border_width(5)
      self.vbox.pack_start(hbox, True, True, 10)
      self.set_has_separator(False)
      hbox.pack_start(self.button_page_spin, True, True, 0)
      go_to_page_label = gtk.Label()
      go_to_page_label.set_text(' of ' + str(page.num_pages()))
      go_to_page_label.set_alignment(0, 1)
      hbox.pack_start(go_to_page_label, False, False, 0)

      self.show_all()
      self.button_page_spin.grab_focus()

  def response(self, dialog, res):
    if res == gtk.RESPONSE_OK:
      self.set_page()      
    ##elif res == gtk.RESPONSE_CANCEL:
    ##  _close_dialog()
    else: ## Escape by escape key
      _close_dialog()

  def set_page(self, *args):
    self.button_page_spin.update()
    page = int(self.button_page_spin.get_value())
    self._page.goto_page(page)
    self._win.queue_draw()
    _close_dialog()

def open_dialog(win, page):
  """Create and display the about dialog."""
  global _dialog
  if _dialog is None:
    _dialog = _GotoPageDialog(win, page)
  else:
    _dialog.present()

def _close_dialog(*args):
  """Destroy the about dialog."""
  global _dialog
  if _dialog is not None:
    _dialog.destroy()
    _dialog = None
