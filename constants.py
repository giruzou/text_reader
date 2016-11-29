# -*- coding: utf-8 -*-

## constants.py
##
## $Id$
##

import os

## My name
APPLICATION_NAME='Text Reader'
## Top directory for config files
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.treader')
## Default configuration file
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')
## Directory for Functions
CONFIG_FUNCTION_DIR = os.path.join(CONFIG_DIR, 'Function')
## Directory for Font Matrixes
CONFIG_FONT_MATRIX_DIR = os.path.join(CONFIG_DIR, 'Font_Matrix')
## Directory for last status files
LAST_STATUS_DIR = os.path.join(CONFIG_DIR, 'status')
## Read size to guess encoding of file
DEFAULT_READIN_SIZE = 2048

## Command line options
COMMAND_LINE_OPTION = [
    [('h', 'help'), 'help', None, 'Show this help and exit'],
    [('c', 'config'), 'config_file', 'FILE', 'Specify configuration file'],
    [('ns', 'ignore-last-status'), 'ignore_last_status', [False],
     "Don't restore last status"],
    [('q', 'no-warning-message'), 'no_warning_message', [False],
     'Surpress warning messages'],
    [('B', 'background-process'), 'background_process', [False],
     'Background process'],
    [('fn', 'text-font'), 'text_font', 'FONT', 'Text font'],
    [('hfn', 'header-font'), 'header_font', 'FONT', 'Header font'],
    [('L', 'list-monospace-fonts'), 'monospace_fonts',
     None, 'Lists all available monospace fonts'],
    [('fg', 'text-color'), 'text_color', 'COLOR', 'Text color'],
    [('bg', 'background-color'), 'background_color', 'COLOR',
     'Background color'],
    [('hfg', 'header-color'), 'header_fg_color', 'COLOR', 'Header text color'],
    [('hbg', 'header-bg-color'), 'header_bg_color', 'COLOR',
     'Header background color'],
    [('rv?', 'reverse-video', 'r, -rv'), 'reverse_video', None,
     'Switch text and background color'],
    [('g', 'geometry'), 'geometry', '[ROWxCOL][+][X+Y]', 'Window geometry'],
    [('lsp', 'line-spacing'), 'line_gap', 'PIXELS',
     'Additional space to put between lines'],
    [('csp', 'char-spacing'), 'char_gap', 'PIXELS',
     'Additional space to put between chars'],
    [('tm', 'top-margin'), 'top_margin', 'PIXELS', 'Top margin'],
    [('bm', 'bottom-margin'), 'bottom_margin', 'PIXELS', 'Bottom margin'],
    [('rm', 'right-margin'), 'right_margin', 'PIXELS', 'Right margin'],
    [('lm', 'left-margin'), 'left_margin', 'PIXELS', 'Left margin'],
    [('fs', 'full-screen'), 'full_screen', None, 'Fullscreen mode'],
    ]

## Static variable in all over process scope
SESSION_ATTRIBUTES = {}
