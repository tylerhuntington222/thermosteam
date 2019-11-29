# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 02:38:40 2019

@author: yoelr
"""
from .handle_builder import HandleBuilder
from .thermo_model_handle import TDependentModelHandle, TPDependentModelHandle
from .functor import functor_lookalike
from .utils import shallow_copy

__all__ = ('PhaseProperty', #'PhasePropertyBuilder', 
           'ChemicalPhaseTProperty', 'ChemicalPhaseTPProperty',
           'ChemicalPhaseTPropertyBuilder', 'ChemicalPhaseTPPropertyBuilder',
           'MixturePhaseTPProperty', 'MixturePhaseTProperty')

# %% Utilities

def set_phase_property(phase_property, phase, builder, data):
    if not builder: return
    if isinstance(builder, HandleBuilder):
        prop = builder(data)
    else:
        prop = builder(data)
    setattr(phase_property, phase, prop)
    

# %% Abstract class    

@functor_lookalike
class PhaseProperty:
    __slots__ = ('s', 'l', 'g')
    
    def __init__(self, s=None, l=None, g=None):
        self.s = s
        self.l = l
        self.g = g

    def __bool__(self):
        return any((self.s, self.l, self.g)) 
    
    def copy(self):
        return self.__class__(shallow_copy(self.s),
                              shallow_copy(self.l),
                              shallow_copy(self.g))
    
    @property
    def var(self):
        for phase in ('s', 'l', 'g'):
            try:
                var = getattr(self, phase).var
                if var: return var.split('.')[0]
            except: pass


# %% Pure component

class ChemicalPhaseTProperty(PhaseProperty):
    __slots__ = ()
    
    def __init__(self, s=None, l=None, g=None):
        self.s = TDependentModelHandle() if s is None else s
        self.l = TDependentModelHandle() if l is None else l
        self.g = TDependentModelHandle() if g is None else g
    
    def __call__(self, phase, T):
        return getattr(self, phase)(T)
    
    
class ChemicalPhaseTPProperty(PhaseProperty):
    __slots__ = ()
    
    def __init__(self, s=None, l=None, g=None):
        self.s = TPDependentModelHandle() if s is None else s
        self.l = TPDependentModelHandle() if l is None else l
        self.g = TPDependentModelHandle() if g is None else g
    
    def __call__(self, phase, T, P):
        return getattr(self, phase)(T, P)
    

# %% Mixture
    
class MixturePhaseTProperty(PhaseProperty):
    __slots__ = ()
    
    def __call__(self, phase, z, T):
        return getattr(self, phase)(z, T)

        
class MixturePhaseTPProperty(PhaseProperty):
    __slots__ = ()
    
    def __call__(self, phase, z, T, P):
        return getattr(self, phase)(z, T, P)
    

# %% Builders

class PhasePropertyBuilder:
    __slots__ = ('s', 'l', 'g')
    
    def __init__(self, s, l, g):
        self.s = s
        self.l = l
        self.g = g
        
    def __call__(self, sdata, ldata, gdata, phase_property=None):
        if phase_property is None: phase_property = self.PhaseProperty() 
        phases = ('s', 'g', 'l')
        builders = (self.s, self.g, self.l)
        phases_data = (sdata, gdata, ldata)
        for phase, builder, data in zip(phases, builders, phases_data):
            set_phase_property(phase_property, phase, builder, data)
        return phase_property

class ChemicalPhaseTPropertyBuilder(PhasePropertyBuilder):
    __slots__ = ()
    PhaseProperty = ChemicalPhaseTProperty
    
        
class ChemicalPhaseTPPropertyBuilder(PhasePropertyBuilder):
    __slots__ = ()
    PhaseProperty = ChemicalPhaseTPProperty
        
        
        
        