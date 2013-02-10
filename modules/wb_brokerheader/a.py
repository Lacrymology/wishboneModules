#!/usr/bin/env python

from pkg_resources import iter_entry_points


for object in iter_entry_points(group='wishbone.module', name=None):
    kak=object.load()
    
meuh = kak()
