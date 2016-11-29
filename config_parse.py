# -*- coding: utf-8 -*-

## Parse configuration file for Text Reader
##
## $Id$
##

import sys
import re

from util import load_file

# 
SECTION = '(^|\n)\[(?P<SECTION>[^\n]+?)\][ \t]*\n'
ITEM = '(^|\n)(?P<VAR>[^:=\n]+?)[ \t]*[:=][ \t\n]*(?P<VAL>(.+?))\n([^ \t\n]|$)'
EMPTY_LINE = '(?P<HEAD>(^|\n))(([ \t]*)|(#+[^\n]*?))(\n|$)'

class ConfigParse():

    class Section():
        def __init__(self, section, items=[]):
            self._name = section
            self._items = items

        def __len__(self):
            return len(self._items)

        def __iter__(self):
            for item in self._items[:]:
                yield item

        def get_name(self):
            return self._name

        def get_item(self, var):
            items = self.get_items(var)
            return ( items[0] if items != [] else None )

        def get_items(self, var):
            items = filter(lambda it:it.get_var() == var, self._items)
            return ( items if items != [] else None )

        def add_item(self, item):
            self._items.append(item)
        
    class Item():
        def __init__(self, var, val):
            self._var = var
            self._val = val

        def get_var(self):
            return self._var

        def get_value(self):
            return self._val

    ##
    def __init__(self, buf):
        self._buf = buf.rstrip()
        self._sections = []
        self.parse()
        if self._sections == []: return None

    def __iter__(self):
        for section in self._sections[:]:
            yield section

    def parse(self):
        buf = self._buf
        empty = re.compile(EMPTY_LINE, re.MULTILINE|re.DOTALL)
        buf = empty.sub('\g<HEAD>', buf)
        reg_section = re.compile(SECTION, re.MULTILINE|re.DOTALL)
        section = []; start = 0; end = 0; max = len(buf) - 1
        while True:
            m = reg_section.search(buf[start:])
            if not m: break
            if m.group('SECTION'):
                end = start + m.start(); start += m.end()
                if len(section) > 0:
                    section[len(section)-1][2] = end
                section.append([m.group('SECTION'), start, max])
        if section == []: return None
        for (sec, s, e) in section:
            items = self.parse_section(buf[s:e+1].strip()+'\n')
            if items == []: continue
            self._sections.append(self.Section(sec, items))

    def parse_section(self, ctx):
        reg_item = re.compile(ITEM, re.MULTILINE|re.DOTALL)
        items = []; start = 0
        while True:
            m = reg_item.search(ctx[start:])
            if not m: break
            if m.group('VAR') and m.group('VAL'):
                val = m.group('VAL').strip()
                val = re.compile('\n[ \t]+').sub('\n', val)
                items.append(self.Item(m.group('VAR'), val))
                start += m.end('VAL')
        return items

    def has_section(self, section):
        return ( True if self.get_sections(section) else False )

    def get_section(self, section):
        s = self.get_sections(section)
        return ( s[0] if s is not None else None )

    def get_sections(self, section):
        s = filter(lambda s:s.get_name() == section, self._sections)
        return ( s if s != [] else None )

if __name__ == "__main__":
    pass
    # cfg = ConfigParse('../config.ini')
    # if cfg is None:
    #     print 'None'
    # else:
    #     ##key = 'Functions'
    #     key = 'Font Matrix'
    #     if cfg.has_section(key):
    #         s = cfg.get_section(key)
    #         print s.get_name(), len(s)
    #         for item in s:
    #             print ( 'var = %s, value = %s'
    #                     % (item.get_var(), item.get_value().encode('utf-8')) )
