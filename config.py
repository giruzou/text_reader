# -*- coding: utf-8 -*-

## Configuration for Text Reader
##
## $Id: text_reader.py,v 1.2 2010-02-21 19:03:45+09 takahasi Exp takahasi $
##
import sys
import re
import os
import hashlib
import types
import copy
import cairo
import pango
import pangocairo
import gtk
import pprint

from config_parse import ConfigParse
from constants import DEFAULT_CONFIG_FILE, LAST_STATUS_DIR
from util import *

class Config():

    class Window():

        def set_default_font(self):
            self._pango_ctx = gtk.Window().get_pango_context()
            df = self._pango_ctx.get_font_description()
            fam = df.get_family()
            monospace = filter(lambda f: f.is_monospace(),
                               self._pango_ctx.list_families())
            if len(monospace) == 0:
                raise AppException, \
                    ('Monospace font is not available on this system.', None)
            match = filter(lambda f: f.get_name() == fam, monospace)
            if not match:
                fam = monospace[0].get_name()
            default_font_size = 16
            self._default_text_font_size = default_font_size
            self._default_header_font_size = default_font_size - 2 
            self._default_text_font = ( '%s %d' %
                                        (fam, self._default_text_font_size) )
            self._default_header_font = ( '%s %d' %
                                          (fam, self._default_header_font_size) )
            self._default['text_font']['default'] = self._default_text_font
            self._default['header_font']['default'] = self._default_header_font
            self.text_font_family = fam
            self.text_font_size = default_font_size
            self.text_font_weight = cairo.FONT_WEIGHT_NORMAL
            self.text_font_style = cairo.FONT_SLANT_NORMAL

        ##
        _screen = gtk.gdk.Screen()
        (_root_width, _root_height) = (_screen.get_width(), _screen.get_height())
        _default_horizontal_margin = int(_root_width * 0.01)
        _default_vertical_margin = int(_root_height * 0.01)
        _max_horizontal_margin = int(_root_width * 0.05)
        _max_vertical_margin = int(_root_height * 0.05)
        _max_window_positon_x = int(_root_width * 0.9)
        _max_window_positon_y = int(_root_height * 0.9)
        _fontmap_resolution = int(pangocairo.cairo_font_map_get_default().get_resolution())
        gtk.settings_get_default().set_long_property('gtk-xft-dpi',
                                                     1024*_fontmap_resolution, '')
        _min_font_size = int(_fontmap_resolution / 12)
        _max_font_size = int(_fontmap_resolution * 0.5)

        _default = {
            'text_font': {'default': None,
                          'check_func': 'check_font'},
            'text_color': {'default': '#000000', 'type': gtk.gdk.Color,
                           'check_func': 'check_color'},
            'background_color': {'default': '#FFFFFF', 'type': gtk.gdk.Color,
                                 'check_func': 'check_color'},
            'header_font': {'default': None,
                            'check_func': 'check_font'},
            'header_fg_color': {'default': '#000000', 'type': gtk.gdk.Color,
                                'check_func': 'check_color'},
            'header_bg_color': {'default': '#FFFFFF', 'type': gtk.gdk.Color,
                                'check_func': 'check_color'},
            'header_format': {'default': u'%f %p/%P'},
            'lpp': {'default': 1, 'type': int,
                     'check_func': 'check_range', 'func_args': (1, None)},
            'cpl':  {'default': 1, 'type': int,
                     'check_func': 'check_range', 'func_args': (1, None)},
            'saved_position':  {'default': 0, 'type': int},
            'line_gap': {'default': 2, 'type': int,
                         'check_func': 'check_range', 'func_args': (1, None)},
            'char_gap': {'default': 2, 'type': int,
                         'check_func': 'check_range', 'func_args': (1, None)},
            'top_margin':    {'default': _default_vertical_margin,
                              'type': int, 
                              'check_func': 'check_range',
                              'func_args': (0, _max_vertical_margin)},
            'bottom_margin': {'default': _default_vertical_margin,
                              'type': int,
                              'check_func': 'check_range',
                              'func_args': (0, _max_vertical_margin)},
            'left_margin':   {'default': _default_horizontal_margin,
                              'type': int, 
                              'check_func': 'check_range',
                              'func_args': (0, _max_horizontal_margin)},
            'right_margin':  {'default': _default_horizontal_margin,
                              'type': int, 
                              'check_func': 'check_range',
                              'func_args': (0, _max_horizontal_margin)},
            'win_x': {'default': 0, 'type': int,
                      'check_func': 'check_range',
                      'func_args': (-(_max_window_positon_x),
                                     _max_window_positon_x)},
            'win_y': {'default': 0, 'type': int,
                      'check_func': 'check_range',
                      'func_args': (-(_max_window_positon_y),
                                     _max_window_positon_y)},

            }

        def __init__(self):
            self.set_default_font()

    ## Config class
    ##
    def __init__(self, opts):
        self._config = None
        self.opts = opts; self.window = self.Window()
        self.line_head_wrap = None; self.line_tail_wrap = None
        self.font_matrix_dict = []; self.functions = []
        self.config_file = ( opts['config_file']
                             if 'config_file' in opts else DEFAULT_CONFIG_FILE )
        self.load()
        # window configuration
        self._config_vars = {}
        self.set_window_config()
        # restore last status
        self.text_file = opts['text_file']
        self._file_text = load_file(self.text_file)
        if not opts['ignore_last_status']:
            self.load_status()
        # parse other options
        self.proc_opts()
        # from Pango to Cairo format
        self.convert_font_description()
        # adjust window size
        ##self.adjust_window_size()
        ##pp = pprint.PrettyPrinter(indent=4)
        ##pp.pprint(self._config_vars)

    def load(self):
        f = self.config_file; buf = None; cfg = None
        msg = ', use default setting.'
        if not file_readable(f):
            warn_msg("Config file '%s' is not found or not regular file or not readable%s"
                     % (f, msg))
            return
        try:
            buf = read_file(f)
        except AppException:
            warn_msg("Can not read config file '%s'%s" % (f, msg))
            return
        if buf is None: return
        try:
            buf = convert_encoding(buf)
        except AppException:
            warn_msg("Can not convert encodig of config file '%s'%s" % (f, msg))
            return
        if buf is None: return
        self._config = ConfigParse(buf)
        if self._config:
            self.load_line_break() ; self.load_functions(); self.load_font_matrix()
        else:
            warn_msg("Fail to load config file '%s'%s" % (f, msg))

    # Load window config
    def load_line_break(self):
        cfg = self._config; key = 'Line Break'
        if not cfg.has_section(key): return
        for (name, var) in ( ('Line Head Break', 'line_head_wrap'),
                             ('Line Tail Break', 'line_tail_wrap') ):
            reg = None
            item = cfg.get_section(key).get_item(var)
            if item: reg = item.get_value()
            if not reg: continue
            reg = reg.strip("'")
            if len(reg) > 0:
                try:
                    reg = re.compile(reg)
                    setattr(self, var, reg)
                except Exception, err:
                    warn_msg(("[Config] '%s': " % name) +
                             'is invalid regexp, ignored.', err)
                    setattr(self, var, None)

    # Load window config
    def set_window_config(self):
        default = self.window._default; name = 'DEFAULT'
        # set default value
        for var in default:
            val = default[var]['default']
            if default[var].has_key('type'):
                try:
                    val = default[var]['type'](val)
                except:
                    raise AppException, ((
                            "[%s] '%s(%s) = %s' is invalid value type"
                            % (name, var, default[var]['type'], val)), None)
            setattr(self.window, var, val)
            self._config_vars[var] = (name, val)
        #
        if self._config:
            cfg = {}
            for item in self._config.get_section('Window'):
                cfg[item.get_var()] = item.get_value()
            self.load_config('CONFIG', cfg)

    def load_config(self, name, data):
        dft = self.window._default
        for var in data:
            val = ( data[var].strip("'")
                    if isinstance(data[var], basestring) else data[var] )
            if ( ( isinstance(val, basestring) and len(val) <= 0 ) or
                 not dft.has_key(var) ):
                continue
            ditem = dft[var]
            # type check
            if ditem.has_key('type'):
                try:
                    val = ditem['type'](val)
                except:
                    warn_msg(("[%s] %s: '%s' is invalid " +
                              "value type, use current value('%s').")
                             % (name, var, val,
                                getattr(self.window, var, None)))
                    continue
            # value check
            if not ditem.has_key('check_func'):
                setattr(self.window, var, val)
                self._config_vars[var] = (name, val)
                continue
            func = getattr(self, ditem['check_func'], None)
            if not func:
                warn_msg(("[%s] Check function '%s' for '%s'" +
                          "does not exist, use default.")
                         % (name, ditem['check_func'], var))
                continue
            args = ( ditem['func_args']
                     if ditem.has_key('func_args') else None )
            try:
                ret = func(val, args)
                setattr(self.window, var, val)
                self._config_vars[var] = (name, val)
            except ConfigValueException, err:
                warn_msg("[%s] %s: %s, use current value('%s')."
                         % (name, var, err, getattr(self.window, var, None)))

    ## Convert font description from pango format to cairo's one
    def convert_font_description(self):
        w_cfg = self.window
        f = pango.FontDescription(w_cfg.text_font)
        if f is None: return
        if f.get_family():
            w_cfg.text_font_family = f.get_family()
        s = f.get_style()
        if s == pango.STYLE_NORMAL:
            w_cfg.text_font_style = cairo.FONT_SLANT_NORMAL
        elif s == pango.STYLE_ITALIC:
            w_cfg.text_font_style = cairo.FONT_SLANT_ITALIC
        elif s == pango.STYLE_OBLIQUE:
            w_cfg.text_font_style = cairo.FONT_SLANT_OBLIQUE
        w = f.get_weight()
        if w == pango.WEIGHT_NORMAL:
            w_cfg.text_font_weight = cairo.FONT_WEIGHT_NORMAL
        elif w == pango.WEIGHT_BOLD:
            w_cfg.text_font_weight = cairo.FONT_WEIGHT_BOLD

        size = f.get_size()
        if size is None or size <= 0:
            warn_msg("[%s] font size(%s) is invalid, use default size('%d')"
                     % (self._config_vars['text_font'][0],
                        size, w_cfg.text_font_size))
        else:
            try:
                size = int(size / pango.SCALE)
                self.check_range(
                    size, (w_cfg._min_font_size, w_cfg._max_font_size))
                w_cfg.text_font_size = size
            except ConfigValueException, err:
                warn_msg("[%s] text_font size: %s, use default size('%s')."
                         % (self._config_vars['text_font'][0],
                            err, w_cfg.text_font_size))

        f.set_size(w_cfg.text_font_size * pango.SCALE)
        w_cfg.text_font = f.to_string()

    def check_font(self, font, *args):
        fn = pango.FontDescription(font)
        fam = fn.get_family()
        if fam is None:
            raise ConfigValueException, \
                ("font '%s' is not found" % font)
        fam = fam.lower()
        match = filter(lambda (f): f.get_name().lower() == fam,
                       self.window._pango_ctx.list_families())
        if len(match) == 0:
            raise ConfigValueException, \
                ("font '%s' is not found" % font)
        if not match[0].is_monospace():
            raise ConfigValueException, \
                ("'%s' is not monospace font" % match[0].get_name())

        w_cfg = self.window; size = fn.get_size()
        if size is None or size < 0:
            raise ConfigValueException, \
                ("size of font '%s'(%s) is invalid"
                 % (font, size))
        else:
            try:
                size = int(size / pango.SCALE)
                self.check_range(
                    size, (w_cfg._min_font_size, w_cfg._max_font_size))
            except ConfigValueException, err:
                raise ConfigValueException, \
                    (("size of font '%s'('%s') is " +
                      "out of range(min=%d, max=%d)" )
                     % (font, size, w_cfg._min_font_size, w_cfg._max_font_size))

    def check_color(self, color, *args):
        if isinstance(color, gtk.gdk.Color):
            return
        try:
            return gtk.gdk.color_parse(color)
        except ValueError:
            raise ConfigValueException, \
                ("'%s' is invalid color" % color)

    def check_range(self, val, range):
        if not isinstance(val, int):
            raise ConfigValueException, \
                ("type of '%s' is not integer" % val)
        for v in range:
            if v is not None and not isinstance(v, int):
                raise ConfigValueException, \
                    "check range is not integer"
        (min, max) = range
        if min is None and max is None:
            raise ConfigValueException, "check range is none"
        if min is not None and max is not None:
            if min <= val <= max: return
            t = ( 'large' if val > max else 'small' )
            raise ConfigValueException, ("'%s' is too %s" % (val, t))
        if min is None:
            if val <= max: return
            raise ConfigValueException, ("'%s' is too large" % val)
        if max is None:
            if val >= min: return
            raise ConfigValueException, ("'%s' is too small" % val)

    # Load functons
    def load_functions(self):
        cfg = self._config; key = 'Functions'
        if not cfg.has_section(key): return
        for f in cfg.get_section(key):
            v = f.get_value().replace('\n', ' ')
            try:
                f = re.compile(f.get_var().strip("'"),
                               re.MULTILINE|re.DOTALL)
            except:
                warn_msg("[CONFIG] '%s': Invalid regexp '%s', ignored."
                         % (key, f))
                continue
            self.functions.append((f, v))

    # Load font Matrix
    def load_font_matrix(self):
        cfg = self._config; key = 'Font Matrix'
        if not cfg.has_section(key): return
        for f in cfg.get_section(key):
            v = f.get_value()
            try:
                f = re.compile(f.get_var().strip("'"))
            except:
                warn_msg("[CONFIG] '%s': Invalid regexp '%s', ignored."
                         % (key, f))
                continue
            self.font_matrix_dict.append((f, v))

    # Option procedure
    def proc_opts(self):
        opts = copy.deepcopy(self.opts)
        for opt in opts:
            func = getattr(self, 'opt_pre_' + opt, None)
            if func and isinstance(func, types.MethodType):
                func(opt, opts[opt])
        #
        self.load_config('CMD OPT', self.opts)
        #
        for var in self.opts:
            func = getattr(self, 'opt_post_' + var, None)
            if func and isinstance(func, types.MethodType):
                func(var, self.opts[var])

    def opt_pre_geometry(self, opt, args):
        m = re.compile('^((?P<lpp>\d+)x(?P<cpl>\d+))?' +
                       '(\+?(?P<X>\d+)\+(?P<Y>\d+))?$').match(args)
        if m:
            if m.group('X'): self.opts['win_x'] = int(m.group('X'))
            if m.group('Y'): self.opts['win_y'] = int(m.group('Y'))
            if m.group('lpp'): self.opts['lpp'] = int(m.group('lpp'))
            if m.group('cpl'): self.opts['cpl'] = int(m.group('cpl'))
            
    def opt_post_reverse_video(self, opt, args):
        w_cfg = self.window
        (w_cfg.text_color, w_cfg.background_color) = \
            (w_cfg.background_color, w_cfg.text_color)

    def opt_post_full_screen(self, opt, args):
        print 'fullscreen'

    ## Load status file
    def load_status(self):
        hash = hashlib.sha256(self._file_text).hexdigest()
        data = load_data(os.path.join(LAST_STATUS_DIR, hash))
        if ( data and data.has_key('file') and
             data['file'] == self.text_file ):
            self.load_config('Last Status', data)

    ## Save status file
    def save_status(self):
        attributes = {'file': self.text_file}
        for var in self.window._default:
            val = getattr(self.window, var, None)
            if val is not None:
                if isinstance(val, gtk.gdk.Color):
                    val = val.to_string()
                attributes[var] = val
        hash = hashlib.sha256(self._file_text).hexdigest()
        if not save_data(os.path.join(LAST_STATUS_DIR, hash), attributes):
            warn_msg('Can not save status data for %s' % self.text_file)
