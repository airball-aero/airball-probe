from calibration import Calibration
from pathlib import Path
import numpy
import pprint


NUM_CHANNELS = 8


class Channels(dict):

    def __init__(self, label):
        self.label = label
        self.alpha = []
        self.beta = []
        for chan in range(0, NUM_CHANNELS):
            self[chan] = []

    def abs_alpha(self):
        d = Channels(self.label + '.abs_alpha')
        d.alpha = map(abs, self.alpha)
        d.beta = self.beta
        for chan in range(0, NUM_CHANNELS):
            d[chan] = self[chan]
        return d

    def abs_beta(self):
        d = Channels(self.label + '.abs_beta')
        d.alpha = self.alpha
        d.beta = map(abs, self.beta)
        for chan in range(0, NUM_CHANNELS):
            d[chan] = self[chan]
        return d

    def restrict_alphabeta(self, f):
        d = Channels(self.label + '.restrict')
        for i in range(0, len(self.alpha)):
            if f(self.alpha[i], self.beta[i]):
                d.alpha.append(self.alpha[i])
                d.beta.append(self.beta[i])
                for chan in range(0, NUM_CHANNELS):
                    d[chan].append(self[chan][i])
        return d
    
    def asymmetry(self):
        
        m = {}
        
        for i in range(0, len(self.alpha)):
            
            alphabeta = (abs(self.alpha[i]), abs(self.beta[i]))
            
            if not alphabeta in m:
                m[alphabeta] = []
                for chan in range(0, NUM_CHANNELS):
                  m[alphabeta].append([])
            for chan in range(0, NUM_CHANNELS):
                m[alphabeta][chan].append(self[chan][i])

        def asymmetry(arr):
            return max(arr) - min(arr)

        d = Channels(self.label + '.asymmetry')
                
        for alphabeta in m:
            d.alpha.append(alphabeta[0])
            d.beta.append(alphabeta[1])
            for chan in range(0, NUM_CHANNELS):
                d[chan].append(asymmetry(m[alphabeta][chan]))
                
        return d

    
def read_channels(data_path, cal):
        
    if type(cal) == str:
        calibration = Calibration(cal)
        
    data_map = {}
        
    with open(data_path, 'r') as f:
            
        while True:
                
            line = f.readline()
            if not line: break
                
            values = list(map(float, line.split(',')))
                
            alphabeta = (values[0], values[1])
            
            pressures = calibration.apply(values[2:])

            for i in range(1, NUM_CHANNELS):
                pressures[i] = pressures[i] / pressures[0]
                    
            if not alphabeta in data_map:
                data_map[alphabeta] = []
                for i in range(0, NUM_CHANNELS):
                    data_map[alphabeta].append([])
                for i in range(0, NUM_CHANNELS):
                    data_map[alphabeta][i].append(pressures[i])

    label = Path(data_path).stem
    data = Channels(label + '.data')
    sigma = Channels(label + '.sigma')

    for alphabeta in data_map:
        for m in (data, sigma):
            m.alpha.append(alphabeta[0])
            m.beta.append(alphabeta[1])
        for i in range(0, NUM_CHANNELS):
            data_array = data_map[alphabeta][i]
            data[i].append(numpy.mean(data_array))
            sigma[i].append(numpy.std(data_array))

    return (data, sigma)
    
