# -*- coding: utf-8 -*-

## util.py
##
## $Id$
##
import os
import sys
import cPickle
import gtk

try:
    ## Universal Encoding Detector
    import chardet
except:
    pass

from constants import DEFAULT_READIN_SIZE, SESSION_ATTRIBUTES

## Exception class
##
class AppException(BaseException): pass
class ConfigValueException(BaseException): pass

## Error message
##
def err_msg(m, err=None):
    msg(("Error: %s, exit." % m), err)

## Warning message
##
def warn_msg(m, err=None):
    if not SESSION_ATTRIBUTES['surpress_warning']:
        msg(("Warning: %s" % m), err)

## Print message
##
def msg(message, add=None):
    message += (('\n%s' % add) if add else '')
    print >>sys.stderr, \
        ("%s" % message).encode(sys.getfilesystemencoding())

## Sanity check
##
def check_file(f):
    if not file_readable(f):
        raise AppException, \
            ('%s is not found or not regular file or not readable' % f, None)
    if os.path.getsize(f) == 0:
        raise AppException, ('None text in %s' % f, None)

## File is readable?
##
def file_readable(f):
    if os.path.isfile(f) and os.access(f, os.R_OK):
        return True
    else:
        return False

## Read file
##
def read_file(f, size=-1):
    fp = None
    try:
        ## U: 改行文字をLF(0x0a)に変換
        fp = open(f, "rU")
        return fp.read(size)
    except IOError, e:
        raise AppException, ('Can not open or read %s' % f, e)
    finally:
        if fp: fp.close()

## Read file and covert encoding
##
def load_file(f):
    buf = read_file(f)
    return convert_encoding(buf, f)

## Guess encoding
##
def guess_encoding(data, size=DEFAULT_READIN_SIZE):
    if 'chardet' in sys.modules:
        charset = chardet.detect(data[0:size])
        if charset.has_key('encoding'):
            charset = charset['encoding']
        else:
            charset = None
    else:
        charset = guess_encoding_poor(data[0:size])

    return charset

def guess_encoding_poor(str):
    encodings=['euc-jp', 'utf-8', 'shift-jis', 'iso2022-jp', 'ascii']
    for enc in encodings:
        try:
            str.decode(enc)
            return enc
        except UnicodeDecodeError, e:
            pass
    return None

## Convert text encoding
##
def convert_encoding(data, f=None):
    charset = guess_encoding(data)
    if not charset:
        raise AppException, \
            (('%s - ' % f if f else '') + 'Fail to convert text encoding', None)
    return unicode(data, charset, 'replace')

## unicode(string[, encoding, errors])
##  errors:
##    'strict': UnicodeDecodeError exceptionをraise
##   'replace': 'REPLACEMENT CHARACTER'であるU+FFFDで置換
##    'ignore': その文字を結果のUnicode文字列に含めない

def load_data(f):
    input = None
    try:
        input = open(f, "rb")
        return cPickle.load(input)
    except Exception, e:
        return None
    finally:
        if input: input.close()

def save_data(f, data):
    output = None
    try:
        output = open(f, "wb")
        cPickle.dump(data, output)
        return True
    except Exception, e:
        warn_msg('%s' % e)
        return False
    finally:
        if output: output.close()

def list_monospace_fonts():
    ctx = gtk.Window().get_pango_context()
    monospace = filter(lambda f: f.is_monospace(),
                       ctx.list_families())
    if len(monospace) == 0:
        print 'Monospace font is not available on this system.'
        return
    m = list(monospace)
    m.sort(cmp=lambda x,y: cmp(x.get_name(), y.get_name()))
    print 'Available monospace fonts are follows:'
    for f in tuple(m):
        print '  %s' % f.get_name().encode(sys.getfilesystemencoding())
