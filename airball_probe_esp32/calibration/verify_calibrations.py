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
import subprocess

import raw_data

########################################################################

plots_dir = 'verification_plots'

if not os.path.isdir(plots_dir):
    os.mkdir(plots_dir)

########################################################################        

def calibration(dp0, dpa, dpb, raw_baro):
    p = subprocess.Popen(
        ['./probe_calibration_test'] +
            list(map(str, [dp0, dpa, dpb, raw_baro])),
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=None)
    p.wait()
    if p.returncode != 0:
        return {
            'alpha': 0,
            'beta': 0,
            'q': 0,
            'p': 0,
        }
    fields = list(map(float, p.stdout.readline().decode('utf-8').strip().split(',')))
    return {
        'alpha': fields[0],
        'beta': fields[1],
        'q': fields[2],
        'p': fields[3],
    }

########################################################################

cal_derived = {
    'alpha': [],
    'beta': [],
    'q': [],
    'p': [],
}

for i in range(0, len(raw_data.deltas['alpha'])):
    r = calibration(
        raw_data.deltas['dp0'][i],
        raw_data.deltas['dpa'][i],        
        raw_data.deltas['dpb'][i],
        0.0)
    cal_derived['alpha'].append(r['alpha'])
    cal_derived['beta'].append(r['beta'])
    cal_derived['q'].append(r['q'])
    cal_derived['p'].append(r['p'])

########################################################################

def plot_comparison(title,
                    cal_derived_label, cal_derived_values,
                    raw_data_label, raw_data_values):
    fig = plt.figure(figsize=(11, 8.5))
    ax = plt.axes(projection='3d')
    ax.set_xlabel('dpa_over_dp0')
    ax.set_ylabel('dpb_over_dp0')
    ax.scatter3D(
        raw_data.ratios['dpa_over_dp0'],
        raw_data.ratios['dpb_over_dp0'],
        cal_derived_values,
        label='calibration derived ' + cal_derived_label)
    if raw_data_label != None:
        ax.scatter3D(
            raw_data.ratios['dpa_over_dp0'],
            raw_data.ratios['dpb_over_dp0'],
            raw_data_values,
            label='raw data ' + raw_data_label)
    ax.legend()
    plt.savefig(
        os.path.join(
            plots_dir,
            title + '.png'),
        dpi=600)
    plt.close()

plot_comparison(
    'verify_alpha',
    'alpha', cal_derived['alpha'], 
    'alpha', raw_data.ratios['alpha'])
plot_comparison(
    'verify_beta',
    'beta', cal_derived['beta'],
    'beta', raw_data.ratios['beta'])
plot_comparison(
    'verify_q',
    'q', cal_derived['q'],
    None, None)
plot_comparison(
    'verify_p',
    'p', cal_derived['p'],
    'minus_s', raw_data.deltas['minus_s'])
