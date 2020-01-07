# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 22:59:17 2019

@author: yoelr
"""

__all__ = ('read_only', )

def deny(self, *args, **kwargs):
    raise TypeError(f"'{type(self).__name__}' object is read-only")

def read_only(cls=None, methods=()):
    if not cls and methods:
        return lambda cls: read_only(cls, methods)
    else:
        for i in methods: setattr(cls, i, deny)
        cls.__delattr__ = deny
        cls.__setattr__ = deny
        return cls
    

class irreplaceable:
    __slots__ = ('_name',)
    def __new__(self, name):
        self._name = '_' + name
    
    def __get__(self, instance, owner):
        return self
    
def assert_same_object(self, other):
    assert other is fget()
    
def irreplaceable(fget, fdel=None, doc=None):
    