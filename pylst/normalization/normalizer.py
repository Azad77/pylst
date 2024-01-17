# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 14:08:35 2024

@author: Azad Rasul
"""

# pylst/normalization/normalizer.py
import numpy as np

def nrs(lst):
    # Compute NR:
    NR = lst / np.sqrt(np.sum(np.square(lst)))
    
    # Multiply NR by the ratio of means
    NRS = NR * (np.mean(lst) / np.mean(NR))
    
    return NRS
    
        
        
    