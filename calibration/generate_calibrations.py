#!/usr/bin/python
# coding=utf-8

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo
import jinja2
import os

import raw_data

########################################################################

plots_dir = 'calibration_plots'

if not os.path.isdir(plots_dir):
    os.mkdir(plots_dir)

########################################################################

def plot_alphabeta(data, name, variable, zlim, wait=False):
    fig = plt.figure(figsize=(11, 8.5))
    ax = plt.axes(projection='3d')
    ax.set_xlabel('alpha (degrees)')
    ax.set_ylabel('beta (degrees)')
    ax.set_zlabel(variable)
    if zlim: ax.set_zlim(zlim[0], zlim[1])
    ax.scatter3D(
        data['alpha'],
        data['beta'],
        data[variable])
    if wait: plt.show()
    plt.savefig(
        os.path.join(
            plots_dir,
            'alpha_beta_to_' + name + '_' + variable + '.png'),
        dpi=300)
    plt.close()

for p in raw_data.pressure_channel_names:
    plot_alphabeta(raw_data.pressures, 'pressures', p, [-1, 1])

plot_alphabeta(raw_data.deltas, 'deltas', 'dp0', [-1, 1])
plot_alphabeta(raw_data.deltas, 'deltas', 'dpa', [-1, 1])
plot_alphabeta(raw_data.deltas, 'deltas', 'dpb', [-1, 1])
plot_alphabeta(raw_data.deltas, 'deltas', 'minus_s', [-1, 1])

plot_alphabeta(raw_data.ratios, 'ratios', 'q_over_dp0', [0, 5])
plot_alphabeta(raw_data.ratios, 'ratios', 'dpa_over_dp0', [-2, 2])
plot_alphabeta(raw_data.ratios, 'ratios', 'dpb_over_dp0', [-2, 2])
plot_alphabeta(raw_data.ratios, 'ratios', 'minus_s_over_dp0', [0, 1])

plot_alphabeta(raw_data.ratios_pos, 'ratios_pos', 'q_over_dp0', [0, 5])
plot_alphabeta(raw_data.ratios_pos, 'ratios_pos', 'dpa_over_dp0', [0, 2])
plot_alphabeta(raw_data.ratios_pos, 'ratios_pos', 'dpb_over_dp0', [0, 2])
plot_alphabeta(raw_data.ratios_pos, 'ratios_pos', 'minus_s_over_dp0', [0, 1])
               
########################################################################

def plot_scatter(data, variable, xylim, wait=False):
    fig = plt.figure(figsize=(11, 8.5))
    ax = plt.axes(projection='3d')
    ax.set_xlabel('dpa_over_dp0')
    ax.set_ylabel('dpb_over_dp0')
    ax.set_zlabel(variable)
    ax.set_xlim(xylim[0], xylim[1])
    ax.set_ylim(xylim[0], xylim[1])    
    ax.scatter3D(
        data['dpa_over_dp0'],
        data['dpb_over_dp0'],
        data[variable])
    if wait: plt.show()
    plt.savefig(
        os.path.join(
            plots_dir,
            'pressure_ratios_to_' + variable + '.png'),
        dpi=300)
    plt.close()
    
plot_scatter(raw_data.ratios_pos, 'alpha', [0, 5])
plot_scatter(raw_data.ratios_pos, 'beta', [0, 5])
plot_scatter(raw_data.ratios_pos, 'q_over_dp0', [0, 5])
plot_scatter(raw_data.ratios_pos, 'minus_s_over_dp0', [0, 5])

########################################################################

def poly_thru_yaxis_sym_xaxis(xvalues, *p):
    x = xvalues[0]
    y = xvalues[1]
    return (p[0] * np.power(x, 1) +
            p[1] * np.power(x, 2) +
            p[2] * np.power(x, 3) +
            p[3] * np.power(x, 1) * np.power(y, 2) +
            p[4] * np.power(x, 1) * np.power(y, 4) +
            p[5] * np.power(x, 1) * np.power(y, 6))
poly_thru_yaxis_sym_xaxis.n = 6

def poly_thru_xaxis_sym_yaxis(xvalues, *p):
    return poly_thru_yaxis_sym_xaxis([xvalues[1], xvalues[0]], *p)
poly_thru_xaxis_sym_yaxis.n = poly_thru_yaxis_sym_xaxis.n

def poly_sym_xaxis_yaxis(xvalues, *p):
    x = xvalues[0]
    y = xvalues[1]
    return (p[0] +
            p[1] * np.power(x, 2) +
            p[2] * np.power(x, 4) +
            p[3] * np.power(x, 6) +
            p[4] * np.power(y, 2) +
            p[5] * np.power(y, 4) +
            p[6] * np.power(y, 6))
poly_sym_xaxis_yaxis.n = 7

def make_fit(fn, x, y, z):

    popt, pcov = spo.curve_fit(
        fn,
        [x, y],
        z,
        [1 for i in range(0, fn.n)])

    def result_function(x, y):
        return fn([x, y], *popt)

    return result_function

########################################################################

model = {
    'alpha': make_fit(
        poly_thru_yaxis_sym_xaxis,
        raw_data.ratios_pos['dpa_over_dp0'],
        raw_data.ratios_pos['dpb_over_dp0'],
        raw_data.ratios_pos['alpha']),
    'beta': make_fit(
        poly_thru_xaxis_sym_yaxis,
        raw_data.ratios_pos['dpa_over_dp0'],
        raw_data.ratios_pos['dpb_over_dp0'],
        raw_data.ratios_pos['beta']),
    'q_over_dp0': make_fit(
        poly_sym_xaxis_yaxis,
        raw_data.ratios_pos['dpa_over_dp0'],
        raw_data.ratios_pos['dpb_over_dp0'],
        raw_data.ratios_pos['q_over_dp0']),
    'minus_s_over_dp0': make_fit(
        poly_sym_xaxis_yaxis,
        raw_data.ratios_pos['dpa_over_dp0'],
        raw_data.ratios_pos['dpb_over_dp0'],
        raw_data.ratios_pos['minus_s_over_dp0']),
}

def plot_curve_fit(data, model, variable, wait=False):
    X, Y = np.meshgrid(
        np.arange(0, 3.0, 0.1),
        np.arange(0, 2.5, 0.1))
    Z = model[variable](X, Y)
    fig = plt.figure(figsize=(11, 8.5))
    ax = plt.axes(projection='3d')
    ax.set_xlabel('dpa_over_dp0')
    ax.set_ylabel('dpb_over_dp0')
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)    
    ax.set_zlabel(variable)
    ax.scatter3D(
        data['dpa_over_dp0'],
        data['dpb_over_dp0'],
        data[variable],
        color='blue')
    ax.plot_surface(X, Y, Z, color='yellow')
    if wait: plt.show()
    plt.savefig(
        os.path.join(
            plots_dir,
            'curve_fit_' + variable + '.png'),
        dpi=300)
    plt.close()
             
plot_curve_fit(raw_data.ratios_pos, model, 'alpha', False)
plot_curve_fit(raw_data.ratios_pos, model, 'beta', False)
plot_curve_fit(raw_data.ratios_pos, model, 'q_over_dp0', False)
plot_curve_fit(raw_data.ratios_pos, model, 'minus_s_over_dp0', False)

########################################################################

# Load the calibration data template

def load_template():
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    return templateEnv.get_template("calibration_data.jinja")

########################################################################

# Plot raw calibration data for quality control

def plot_calibration(var_name, nx, ny, linear_data):
    xx, yy = np.meshgrid(range(0, nx), range(0, ny))
    f = lambda ix, iy: linear_data[iy + ny * ix]
    zz = np.vectorize(f)(xx, yy)

    title = 'probe_calibration_' + var_name
        
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x index')
    ax.set_ylabel('y index')
    ax.set_zlabel(var_name)
    ax.plot_surface(xx, yy, zz, rstride=1, cstride=1)
    fake2Dline = matplotlib.lines.Line2D([0],[0], linestyle="none", c='b', marker = 'o')
    ax.legend([fake2Dline], [title], numpoints = 1)
    plt.savefig(
        os.path.join(
            plots_dir,
            title + '.png'),
        dpi=600)
    plt.close()

########################################################################

# Generate a calibration data file for a given probe design

def generate_file(raw2data):

    data_alpha = []
    data_beta = []
    data_q_over_dp0 = []
    data_minus_s_over_dp0 = []    

    dp_step = 0.1
    
    dp_alpha_min = 0
    dp_alpha_max = 3.0
    dp_alpha_zero_offset = 0.0
    n_alpha = int(round((dp_alpha_max - dp_alpha_min) / dp_step) + 1)
    
    dp_beta_min = 0
    dp_beta_max = 2.5
    dp_beta_zero_offset = 0.0
    n_beta = int(round((dp_beta_max - dp_beta_min) / dp_step) + 1)    

    for i in range(0, n_alpha):
        dpa = dp_alpha_min + dp_step * i
        for j in range(0, n_beta):
            dpb = dp_beta_min + dp_step * j
            d = raw2data(dpa, dpb)
            data_alpha.append(d[0]);
            data_beta.append(d[1]);
            data_q_over_dp0.append(d[2])
            data_minus_s_over_dp0.append(d[3])

    plot_calibration('alpha', n_alpha, n_beta, data_alpha)
    plot_calibration('beta', n_alpha, n_beta, data_beta)
    plot_calibration('q_over_dp0', n_alpha, n_beta, data_q_over_dp0)    
    plot_calibration('minus_s_over_dp0', n_alpha, n_beta, data_minus_s_over_dp0)
            
    outfile = open('probe_calibration.h', 'w')
            
    outfile.write(load_template().render(
        fileprefix = 'probe',
        structs = {
            'alpha': {
                'comment': 'Alpha as a function of (dpa/dp0, dpb/dp0)',
                'x': {
                    'size': n_alpha,
                    'step': dp_step,
                    'zero_offset': dp_alpha_zero_offset,
                },
                'y': {
                    'size': n_beta,
                    'step': dp_step,
                    'zero_offset': dp_beta_zero_offset,
                },
                'data': data_alpha,
            },
            'beta': {
                'comment': 'Beta as a function of (dpa/dp0, dpb/dp0)',
                'x': {
                    'size': n_alpha,
                    'step': dp_step,
                    'zero_offset': dp_alpha_zero_offset,
                },
                'y': {
                    'size': n_beta,
                    'step': dp_step,
                    'zero_offset': dp_beta_zero_offset,
                },
                'data': data_beta,
            },
            'q_over_dp0': {
                'comment': 'q/dp0 as a function of (dpa/dp0, dpb/dp0)',
                'x': {
                    'size': n_alpha,
                    'step': dp_step,
                    'zero_offset': dp_alpha_zero_offset,
                },
                'y': {
                    'size': n_beta,
                    'step': dp_step,
                    'zero_offset': dp_beta_zero_offset,
                },
                'data': data_q_over_dp0,
            },
            'minus_s_over_dp0': {
                'comment': '-s/dp0 as a function of (dpa/dp0, dpb/dp0)',
                'x': {
                    'size': n_alpha,
                    'step': dp_step,
                    'zero_offset': dp_alpha_zero_offset,
                },
                'y': {
                    'size': n_beta,
                    'step': dp_step,
                    'zero_offset': dp_beta_zero_offset,
                },
                'data': data_minus_s_over_dp0,
            },
        }))
    
    outfile.close();

########################################################################

# Generate calibration files for our two known probe designs

def probe_raw2data(dpa_over_dp0, dpb_over_dp0):
    return [
        model['alpha'](dpa_over_dp0, dpb_over_dp0),
        model['beta'](dpa_over_dp0, dpb_over_dp0),
        model['q_over_dp0'](dpa_over_dp0, dpb_over_dp0),
        model['minus_s_over_dp0'](dpa_over_dp0, dpb_over_dp0),        
    ]

generate_file(probe_raw2data)
