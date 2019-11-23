#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 08:58:41 2018

@author: Yoel Rene Cortes-Pena
"""
from math import exp
import numpy as np
from .unifac_data import DOUFSG, DOUFIP2016, UFIP, UFSG
from numba import njit

__all__ = ('GroupActivityCoefficients',
           'DortmundActivityCoefficients',
           'UNIFACActivityCoefficiencts')

# %% Utilities

def chemgroup_array(chemgroups, index):
    M = len(chemgroups)
    N = len(index)
    array = np.zeros((M, N))
    for i, groups in enumerate(chemgroups):
        for group, count in groups.items():
            array[i, index[group]] = count
    return array

@njit
def group_activity_coefficients(xs, chemgroups, loggammacs,
                                Qs, psis, cQfs, gpsis):
    weighted_counts = chemgroups.transpose() @ xs
    Q_fractions = Qs * weighted_counts 
    Q_fractions /= Q_fractions.sum()
    Q_psis = psis * Q_fractions
    sum1 = Q_psis.sum(1)
    sum2 = -(psis.transpose() / sum1) @ Q_fractions
    loggamma_groups = Qs * (1. - np.log(sum1) + sum2)
    sum1 = cQfs @ gpsis.transpose()
    sum1 = np.where(sum1==0, 1., sum1)
    fracs = - cQfs / sum1
    sum2 = fracs @ gpsis
    chem_loggamma_groups = Qs*(1. - np.log(sum1) + sum2)
    loggammars = ((loggamma_groups - chem_loggamma_groups) * chemgroups).sum(1)
    return np.exp(loggammacs + loggammars)


# %% Activity Coefficients

class GroupActivityCoefficients:
    __slots__ = ('_chemgroups', '_rs', '_qs', '_group_mask',
                 '_Qs', '_chem_Qfractions', '_group_psis',
                 '_interactions', '_chemicals')
    _cached = {}
    def __init__(self, chemicals):
        self.chemicals = chemicals
        
    @property
    def chemicals(self):
        return self._chemicals
    
    @chemicals.setter
    def chemicals(self, chemicals):
        chemicals = tuple(chemicals)
        if chemicals in self._cached:
            (self._rs, self._qs, self._Qs,
             self._chemgroups, self._group_psis,
             self._chem_Qfractions, self._interactions,
             self._group_mask) = self._cached[chemicals]
        else:
            get = getattr
            attr = self.group_name
            chemgroups = [get(s, attr) for s in chemicals]
            all_groups = set()
            for groups in chemgroups: all_groups.update(groups)
            index = {group:i for i,group in enumerate(all_groups)}
            chemgroups = chemgroup_array(chemgroups, index)
            all_subgroups = self.all_subgroups
            subgroups = [all_subgroups[i] for i in all_groups]
            main_group_ids = [i.main_group_id for i in subgroups]
            self._Qs = Qs = np.array([i.Q for i in subgroups])
            Rs = np.array([i.R for i in subgroups])
            self._rs = rs = chemgroups @ Rs
            self._qs = qs = chemgroups @ Qs
            self._chemgroups = chemgroups
            chem_Qs = Qs * chemgroups
            self._chem_Qfractions = cQfs = chem_Qs/chem_Qs.sum(1, keepdims=True)
            all_interactions = self.all_interactions
            self._interactions = [[None if i == j else all_interactions[i][j]
                                   for i in main_group_ids]
                                 for j in main_group_ids]
            N_groups = len(all_groups)
            group_shape = (N_groups, N_groups)
            # Psis array with only symmetrically available groups
            self._group_psis = np.zeros(group_shape, dtype=float)
            # Make mask for retrieving symmetrically available groups
            rowindex = np.arange(N_groups, dtype=int)
            indices = [rowindex[rowmask] for rowmask in cQfs != 0]
            self._group_mask = group_mask = np.zeros(group_shape, dtype=bool)
            for index in indices:
                for i in index:
                    group_mask[i, index] = True
            self._cached[chemicals] = (rs, qs, Qs, chemgroups,
                                       self._group_psis, cQfs,
                                       self._interactions, self._group_mask)
        self._chemicals = chemicals
        
    def __call__(self, xs, T):
        """Return UNIFAC coefficients.
        
        Parameters
        ----------
        xs : array_like
            Molar fractions
        T : float
            Temperature (K)
        
        """
        xs = np.asarray(xs)
        psis = np.array([[self.psi(T, d) if d else 1. for d in i]
                         for i in self._interactions])
        mask = self._group_mask
        self._group_psis[mask] =  psis[mask]
        return group_activity_coefficients(xs, self._chemgroups,
                                           self.loggammacs(self._qs, self._rs, xs),
                                           self._Qs, psis,
                                           self._chem_Qfractions,
                                           self._group_psis)
    
    def __repr__(self):
        chemicals = ", ".join([i.ID for i in self.chemicals])
        return f"<{type(self).__name__}({chemicals})>"
    
    
class UNIFACActivityCoefficiencts(GroupActivityCoefficients):
    all_subgroups = UFSG
    all_interactions = UFIP
    group_name = 'UNIFAC'
    @staticmethod
    @njit
    def loggammacs(qs, rs, xs):
        r_net = (xs*rs).sum()
        q_net = (xs*qs).sum()  
        Vs = rs/r_net
        Fs = qs/q_net
        Vs_over_Fs = Vs/Fs
        return 1. - Vs - np.log(Vs) - 5.*qs*(1. - Vs_over_Fs + np.log(Vs_over_Fs))
    
    @staticmethod
    def psi(T, a):
        return exp(-a/T)


class DortmundActivityCoefficients(GroupActivityCoefficients):
    __slots__ = ()
    all_subgroups = DOUFSG
    all_interactions = DOUFIP2016
    group_name = 'Dortmund'
    @staticmethod
    @njit
    def loggammacs(qs, rs, xs):
        r_net = (xs*rs).sum()
        q_net = (xs*qs).sum()
        rs_p = rs**0.75
        r_pnet = (rs_p*xs).sum()
        Vs = rs/r_net
        Fs = qs/q_net
        Vs_over_Fs = Vs/Fs
        Vs_p = rs_p/r_pnet
        return 1. - Vs_p + np.log(Vs_p) - 5.*qs*(1. - Vs_over_Fs + np.log(Vs_over_Fs))
    
    @staticmethod
    def psi(T, abc):
        a, b, c = abc
        return exp((-a/T - b - c*T)) 
    
    



