#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

## text_reader.py
##
## $Id: text_reader.py,v 1.2 2010-02-21 19:03:45+09 takahasi Exp takahasi $
##

import os
import sys
import re
import gtk

try:
    import chardet
except:
    print >>sys.stderr, \
        'Chardet package is not found, use poor encoding detection instead.'

from constants import COMMAND_LINE_OPTION, SESSION_ATTRIBUTES
from util import AppException, msg, err_msg, check_file, list_monospace_fonts
from config import Config
from text_page import TPage
from text_view import TView

class NullDevice:
    def write(self, s): pass

## Parse command line options
##
def parse_option(argv):

    opt_list = COMMAND_LINE_OPTION

    def usage():
        print 'Usage: %s [OPTION...] [FILENAME]' % cmd
        print '\nShow texts in vertical direction.\n'
        print 'Options:'
        for ((opt), x, arg_type, exp) in opt_list:
            short_opt = (opt[0] if len(opt) < 3 else opt[2])
            long_opt = (opt[1] if len(opt) < 4 else opt[3])
            arg_type = ((' ' + arg_type) if isinstance(arg_type, basestring) else '')
            print ('  -%s, --%s%s%s%s' %
                   (short_opt, long_opt, arg_type,
                    ' '*(30-(len(short_opt)+len(long_opt)+len(arg_type))), exp))

    def usage_and_exit(exit_status):
        usage(); sys.exit(exit_status)

    ##
    cmd = os.path.basename(argv[0])
    nonopt_regexp = re.compile('^[^-]')
    argv = argv[1:]; argc = len(argv)
    # None option and text file
    if argc == 0: usage_and_exit(0)

    # set default value
    opts = {}
    for i, (x, var, val, y) in enumerate(opt_list):
        if isinstance(val, list):
            opts[var] = val[0]
            opt_list[i][2] = None
    # start parsing
    i = 0; text_file = None
    while i < argc:
        arg = argv[i]
        match = filter(lambda (opt):
                    filter(lambda o:
                               re.compile('^-{1,2}'+ o + '$').match(arg),
                           opt[0]), opt_list)
        if match == []:
            if ( (i == (argc - 1)) and
                 nonopt_regexp.match(argv[i]) ):
                text_file = argv[i]
                break
            else:
                msg("Unknown option '%s'.\n" % arg)
                usage_and_exit(1)
        (var, t) = (match[0][1], match[0][2])
        if t is None:
            opts[var] = True
        else:
            if ( (i + 1) < argc and
                 nonopt_regexp.match(argv[i+1]) ):
                opts[var] = unicode(argv[i+1], sys.getfilesystemencoding())
                i += 1
            else:
                msg("Argument required for option '%s'.\n" % arg)
                usage_and_exit(1)
        i += 1

    ##
    if 'help' in opts: usage_and_exit(0)
    if 'monospace_fonts' in opts:
        list_monospace_fonts(); sys.exit(0)
    if text_file is None:
        msg('None text file.\n')
        usage_and_exit(1)
    if 'geometry' in opts:
        g = opts['geometry']
        if ( not ( len(g) > 0 and
                   re.compile('^(\d+x\d+)?(\+?\d+\+\d+)?$').match(g))):
            msg("'-g': Illegal geometry format.\n")
            usage_and_exit(1)
    ##
    text_file = os.path.realpath(text_file)
    check_file(text_file)
    opts['text_file'] = text_file
    SESSION_ATTRIBUTES['surpress_warning'] = opts['no_warning_message']

    return opts

if __name__ == "__main__":
    ##print dir(util)
    try:
        opts = parse_option(sys.argv)
        cfg = Config(opts)
        page = TPage(cfg)
        TView(page, cfg)
    except AppException, (msg, e):
        err_msg(msg, e); sys.exit(1)

    # background process
    if opts['background_process']:
        ## http://effbot.org/librarybook/os.htm
        pid = os.fork()
        if pid > 0:
            os._exit(0)
        os.setpgrp(); os.umask(0)
        sys.stdin.close()
        sys.stdout = NullDevice()
        sys.stderr = NullDevice()

    gtk.main()
