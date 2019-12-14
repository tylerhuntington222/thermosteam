# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 20:18:27 2019

@author: yoelr
"""
from . import equilibrium as eq
from .chemicals import Chemicals
from .mixture import IdealMixture
from .utils import read_only
from .settings import settings

__all__ = ('Thermo',)

@read_only
class Thermo:
    __slots__ = ('chemicals', 'mixture', 'Gamma', 'Phi', 'PCF') 
    _cache = {}
    def __new__(cls, chemicals, mixture=None,
                Gamma=eq.DortmundActivityCoefficients,
                Phi=eq.IdealFugacityCoefficients,
                PCF=eq.IdealPoyintingCorrectionFactor):
        args = (chemicals, mixture, Gamma, Phi, PCF)
        cache = cls._cache
        if args in cache:
            self = cache[args]
        else:
            self = super().__new__(cls)
            mixture = mixture or IdealMixture(chemicals)
            if not isinstance(chemicals, Chemicals):
                chemicals = Chemicals(chemicals)
            chemicals.compile()
            if settings._debug:
                issubtype = issubclass
                assert issubtype(Gamma, eq.ActivityCoefficients), (
                    f"Gamma must be a '{eq.ActivityCoefficients.__name__}' subclass")
                assert issubtype(Phi, eq.FugacityCoefficients), (
                    f"Phi must be a '{eq.FugacityCoefficients.__name__}' subclass")
                assert issubtype(PCF, eq.PoyintingCorrectionFactor), (
                    f"PCF must be a '{eq.PoyintingCorrectionFactor.__name__}' subclass")
            setattr = object.__setattr__
            setattr(self, 'chemicals', chemicals)
            setattr(self, 'mixture', mixture)
            setattr(self, 'Gamma', Gamma)
            setattr(self, 'Phi', Phi)
            setattr(self, 'PCF', PCF)    
            cache[args] = self
        return self
    
    def __reduce__(self):
        return self.__new__, (self.__class__, self.chemicals, self.mixture,
                              self.Gamma, self.Phi, self.PCF)
    
    def __repr__(self):
        IDs = [i for i in self.chemicals.IDs]
        return f"{type(self).__name__}([{', '.join(IDs)}])"