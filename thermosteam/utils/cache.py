# -*- coding: utf-8 -*-
# BioSTEAM: The Biorefinery Simulation and Techno-Economic Analysis Modules
# Copyright (C) 2020, Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module is under the UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
"""
"""

__all__ = ('Cache', 'cached_method')

class Cache:
    __slots__ = ('args', 'value')
    def __init_subclass__(cls):
        try:
            cls.load
        except:
            raise NotImplementedError('Cache subclass must implement as `load` method')
    
    def __init__(self, *args):
        self.args = args
        self.value = None
    
    def retrieve(self):
        value = self.value
        if not value:
            self.value = value = self.load(*self.args)
        return value
    
    def __call__(self, *args):
        if args == self.args:
            value = self.retrieve()
        else:
            self.args = args
            self.value = value = self.load(*self.args)
        return value
    
def cached_method(f):
    return type(f.__name__, (Cache,), {'load': staticmethod(f),
                                       '__module__': f.__module__})
    