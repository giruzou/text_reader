# -*- coding: utf-8 -*-

## text_view.py
##
## $Id$
##

import os
import re

from text_buffer import TBuffer
from config import Config
from util import *

class TPage():

    def __init__(self, cfg):
        self._cfg = cfg; w_cfg = cfg.window
        self.lpp = w_cfg.lpp; self.cpl = w_cfg.cpl
        self._line_head_wrap = cfg.line_head_wrap
        self._line_tail_wrap = cfg.line_tail_wrap
        ## Construct all pages
        self.set_page(); self.set_page_info()
        self._saved_position = w_cfg.saved_position
        self._cline = self.line_in_position(w_cfg.saved_position)

    def __str__(self):
        return "   current page = %d\n" % self.cpage() + \
               "number of pages = %d\n" % self.num_pages() + \
               " lines per page = %d\n" % self.lpp + \
               " chars per line = %d\n" % self.cpl + \
               "number of lines = %d\n" % self.num_lines()

    def __getitem__(self, i):
        try:
            return self._lines[i]
        except IndexError:
            return None

    def __getslice__(self, i, j):
        try:
            return self._lines[i:j]
        except IndexError:
            return None

    def __iter__(self):
        start = self.cline()
        end = start + self.lpp
        for line in self._lines[start:end]:
            yield line

    # Construct page
    def set_page(self):
        tbuf = self._cfg._file_text.rstrip() + '\n'
        if len(self._cfg.functions) > 0:
            tbuf = self.apply_functions(tbuf)
        self._tbuf = TBuffer(tbuf)
        self.set_lines()

    # Page information
    def set_page_info(self):
        self._num_lines = len(self._lines)
        self._num_pages = int(self._num_lines/self.lpp)
        if (self._num_lines % self.lpp) > 0:
            self._num_pages += 1

    def set_lines(self):
        self._lines = []
        buf = self._tbuf; buf.reset(); buf.set_mark()
        while not buf.eot():
            # change current position(='buf._pos') in buf.find method
            found = buf.find('\n', self.cpl)
            eol = buf.cpos() - 1
            # 禁則処理
            if not buf.eot() and buf[buf.cpos()] != '\n':
                eol = self.line_break(eol)
            # Set the region of nth line:
            #   Empty line if buf.get_mark() == eol
            #   表示の際にはslice(=buf[start:eol])で切り出すため、
            #   eol=eol+1となる(+1のoffsetが必要)
            self._lines.append( (buf.get_mark(), eol+1) )
            # Skip newline
            if found >= 0 or buf[buf.cpos()] == '\n':
                buf.inc(1)
            buf.set_mark()
        buf.reset()

    def line_break(self, eol):
        buf = self._tbuf
        if self._line_head_wrap and self._line_head_wrap.match(buf[eol+1]):
            ## 行頭禁則文字
            if self._line_head_wrap.match(buf[eol+2]):
                # 次の文字も行頭禁則文字の場合は追い出し処理を行う
                eol = self.line_break_shift_head(eol)
            else:
                # ぶら下がり
                eol += 1
        elif self._line_tail_wrap and self._line_tail_wrap.match(buf[eol]):
            ## 行末禁則文字: 追い出し処理のみ
            eol = self.line_break_shift_tail(eol)
        buf.reset(eol+1); return eol

    ##
    def line_break_shift_head(self, eol):
        buf = self._tbuf;
        head = self._line_head_wrap; tail = self._line_tail_wrap
        start = buf.get_mark()
        for i in range(eol, start, -1):
            if tail:
                if head.match(buf[i]):
                    continue
                if tail.match(buf[i]):
                    if tail.match(buf[i-1]):
                        continue
                    else:
                        eol = i - 1; break
                if tail.match(buf[i-1]): continue
                eol = i - 1; break
            elif not head.match(buf[i]):
                eol = i - 1; break
        return eol
    ##
    def line_break_shift_tail(self, eol):
        head = self._line_head_wrap; tail = self._line_tail_wrap
        buf = self._tbuf; start = buf.get_mark()
        for i in range(eol, start, -1):
            if head:
                if head.match(buf[i]):
                    continue
                if tail.match(buf[i]):
                    if tail.match(buf[i-1]):
                        continue
                    else:
                        eol = i - 1; break
                if tail.match(buf[i-1]): continue
                eol = i - 1; break
            elif not tail.match(buf[i]):
                eol = i; break
        return eol

    def apply_functions(self, buf):
        functions = self._cfg.functions
        for i, (reg, reg2) in enumerate(functions):
            try:
                (func, reg2) = reg2.strip('() \t').split(' ', 1)
                func = getattr(self, 'func_' + func, None)
                if func:
                    reg2 = reg2.strip("'")
                    buf = apply(func, (buf, reg, reg2))
            except Exception, err:
                warn_msg('Fail to execute functions(%s), ignored.' % [reg2], err)
                del functions[i]
        return buf

    def func_replace(self, buf, reg1, reg2):
        if re.compile('^lambda ').match(reg2):
            reg2 = reg2.replace('cpl', str(self.cpl))
            reg2 = eval(reg2)
        return reg1.sub(reg2, buf)

    def func_ruby(self, buf, arg1, arg2):
        pass

    # get text buffer
    def get_buffer(self):
        return self._tbuf

    # current line
    def cline(self):
        return self._cline

    # number of lines
    def num_lines(self):
        return self._num_lines

    # goto line
    def goto_line(self, l):
        last = self.num_lines()
        if l < 0:
            self._cline = 0
        elif l > last - 1:
            t = last % self.lpp
            self._cline = last - ( t if t > 0 else self.lpp)
        else:
            self._cline = l

    # current page
    def cpage(self):
        return self.cline() / self.lpp + 1

    # number of pages
    def num_pages(self):
        return self._num_pages

    # go to page
    def goto_page(self, p, fixed=True):
        ## First line of nth page
        self.goto_line((p - 1) * self.lpp)
        if fixed:
            self._saved_position = self[self.cline()][0]

    # next page
    def next_page(self):
        self.goto_page(self.cpage() + 1)

    # previous page
    def prev_page(self):
        self.goto_page(self.cpage() - 1)

    # first page
    def goto_first_page(self):
        self.goto_page(1)

    # last page
    def goto_last_page(self):
        self.goto_page(self.num_pages())

    # Call when window resized
    def reset_page(self, new_lpp, new_cpl):
        if self.cpl == new_cpl and self.lpp == new_lpp:
            return
        self.lpp = new_lpp
        if self.cpl != new_cpl:
            # Reconstruct all pages
            self.cpl = new_cpl
            self.set_page()
        self.set_page_info()
        self.reset_current_page_when_resized()

    # Ballpark position
    def reset_current_page_when_resized(self):
        pos = self._saved_position
        if pos == 0:
            page = 1
        else:
            for line, (start, end) in enumerate(self[:]):
                if ( (start == end and pos == start) or
                     (start <= pos < end) ):
                    break
            page = int(line / self.lpp) + 1
        self.goto_page(page, False)

    def line_in_position(self, pos):
        if pos == 0:
            line = 0
        else:
            for line, (start, end) in enumerate(self[:]):
                if ( (start == end and pos == start) or
                     (start <= pos < end) ):
                    break
            ##
            ##line = filter(lambda (line, (start, end)):
            ##               ((start == end and pos == start) or
            ##                (start <= pos < end)),
            ##         enumerate(self[:]))
            ##line = ( line[0][0] if len(line) > 0 else 0 )
            ##
            # first line of page
            line -= ( line % self.lpp )
        return line

    def save_status(self):
        w_cfg = self._cfg.window
        w_cfg.saved_position = self[self.cline()][0]
        w_cfg.lpp = self.lpp; w_cfg.cpl = self.cpl
