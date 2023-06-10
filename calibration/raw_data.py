#!/usr/bin/python
# coding=utf-8

import operator
import csv
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import numpy as np
import scipy.optimize as spo
import jinja2
import sys
import sweep
import os

__all__ = [
    'pressure_channel_names',
    'pressures',
    'deltas',
    'ratios',
    'ratios_pos',
]

########################################################################

# ** Probe geometry **
#
# The probe has a standard 5-hole spherical nose probe with a static
# probe added. The raw measurements are as follows:
#     (dp0, dpA, dpB)
# where the pressures are defined as:
#     dp0 = (center hole) - (static)
#     dpA = (lower hole) - (upper hole)
#     dpB = (right hole) - (left hole)
#
# For our wind tunnel data, we have measured each hole independently
# relative to tunnel static, and have also used a Pitot tube to obtain
# tunnel q.

########################################################################

raw_data_files = [
    'c01_05.csv',
    'c01_10.csv',
    'c02_10.csv',
    'c03_10.csv',
]
raw_data_dir = 'raw_data'

########################################################################

# Raw pressures come in via module "sweep" as pressure coefficients,
# already normalized with reference to tunnel q.

raw_pressures = [
    'd', # down hole
    'u', # up hole
    'r', # right hole
    'l', # left hole
    'c', # center hole
    's', # static probe reading
]

pressure_channel_names = raw_pressures

def restrict(alpha, beta):
    return abs(beta) <= 30

def read_data(csv_file_name):

    d = {
        'alpha': np.array([]),
        'beta': np.array([]),
    }

    for p in raw_pressures:
        d[p] = np.array([])

    (data, _) = sweep.read_channels(
        os.path.join(raw_data_dir, csv_file_name),
        os.path.join(raw_data_dir, 'esp32_scanner.cal'))

    data = data.restrict_alphabeta(restrict)

    for i in range(0, len(data.alpha)):
        d['alpha'] = np.append(d['alpha'], int(data.alpha[i]))
        d['beta'] = np.append(d['beta'], int(data.beta[i]))
        for chan in range(0, len(raw_pressures)):
            d[raw_pressures[chan]] = np.append(
                d[raw_pressures[chan]],
                float(data[chan + 1][i]))
                
    return d

########################################################################

def tuples(data):
    n = len(data[list(data.keys())[0]])
    for i in range(0, n):
        t = {}
        for k in data:
            t[k] = data[k][i]
        yield t

def filter(data, f):
    r = {}
    for k in data:
        r[k] = np.array([])
    for t in tuples(data):
        if f(t):
            for k in data:
                r[k] = np.append(r[k], t[k])
    return r

def combine(d0, d1):
    if d0 == None: return d1
    k0 = [k for k in d0]
    k1 = [k for k in d1]
    if not k0 == k1: raise 'Cannot merge incompatible colums'    
    return {k: np.append(d0[k], d1[k]) for k in d0}

def distance(x, y):
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))

def sign(x):
    if x < 0: return -1
    return 1

########################################################################

raw_data = None
for f in raw_data_files:
    raw_data = combine(raw_data, read_data(f))

pressures = raw_data
    
deltas = {
    'alpha': raw_data['alpha'],
    'beta': raw_data['beta'],
    'dp0': raw_data['c'] - raw_data['s'],
    'dpa' : raw_data['d'] - raw_data['u'],
    'dpb': raw_data['r'] - raw_data['l'],
    'minus_s': raw_data['s'] * -1,
}

ratios = {
    'alpha': deltas['alpha'],
    'beta': deltas['beta'],
    'dpa_over_dp0': deltas['dpa'] / deltas['dp0'],
    'dpb_over_dp0': deltas['dpb'] / deltas['dp0'],
    'q_over_dp0': 1 / deltas['dp0'],
    'minus_s_over_dp0': deltas['minus_s'] / deltas['dp0'],
}

ratios_pos = {
    'alpha': np.abs(ratios['alpha']),
    'beta': np.abs(ratios['beta']),
    'dpa_over_dp0': np.array([
            ratios['dpa_over_dp0'][i] * sign(ratios['alpha'][i])
            for i in range(0, len(ratios['alpha']))
        ]),
    'dpb_over_dp0': np.array([
            ratios['dpb_over_dp0'][i] * sign(ratios['beta'][i])
            for i in range(0, len(ratios['beta']))
        ]),
    'q_over_dp0': ratios['q_over_dp0'],
    'minus_s_over_dp0': ratios['minus_s_over_dp0'],
}
