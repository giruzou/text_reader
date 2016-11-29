# -*- coding: utf-8 -*-

## text_buffer.py
##
## $Id$
##

class TBuffer(object):

    def __init__(self, buf):
        self._buf = buf; self._pos = 0

    def __repr__(self):
        return self._buf[self.cpos():]

    def __len__(self):
        return len(self._buf)

    def __getitem__(self, i):
        try:
            return self._buf[i]
        except IndexError:
            return None

    def __getslice__(self, i, j):
        try:
            return self._buf[i:j]
        except IndexError:
            return None

    def __iter__(self):
        for char in self._buf[self.cpos():]:
            yield char; self.inc(1)

    def cpos(self):
        return self._pos

    def eot(self):
        return ( self.cpos() == len(self) - 1 )

    def reset(self, pos=0):
        max = len(self) - 1
        if pos < 0:
            self._pos = 0
        elif pos > max:
            self._pos = max
        else:
            self._pos = pos

    def inc(self, inc):
        self.reset(self.cpos() + inc)

    def dec(self, dec):
        self.reset(self.cpos() - dec)

    def set_mark(self, pos=None):
        self._mark = (pos if pos else self.cpos())

    def get_mark(self):
        return self._mark

    def find(self, sub, len):
        ret = self._buf.find(sub, self.cpos(), self.cpos()+len)
        if ret >= 0:
            self.reset(ret)
        else:
            self.inc(len)
        return ret
