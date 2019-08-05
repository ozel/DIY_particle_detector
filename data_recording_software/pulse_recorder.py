#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for recording pulses of the DIY Particle Detector connected to an audio input.
A live view of triggering pulses is provided via an oscilloscope plot if the pulse 
amplitude is larger than the threshold level.

This program tries to process the audio input as fast as possible, therefore no
further analysis is done here. The trigger amplitude is compared with the
MIN_ALPHA_PEAK value and the corresponding particle type ('ptype') is saved with 
each waveform. Further pulses appearing in the same waveform will not be counted.
This is the job of the analysis script analyse_and_plot_pulses.py (it will also catch smaller puslses below
the threshold value.)

Required python modules besides numpy & pandas:
    pyaudio
    pyqtgraph
    pyo (optionally if sonification is desired, see setings below) 

Keyboard shortcuts in pulse/oscilloscope plot window:
    '-' for decreasing threshold (moves yellow threshold line up)
    '+' for increasing threshold (moves yellow threshold line down)
    
Allway close the plot window first (Ctrl-W, CMD-Q etc. or by its closing icon).
The program will stop recording and save all waveforms in a new .pkl file.
Only if script displays "done." but still runs, use Ctrl-C.
    

@author: Oliver Keller
@date: March 2019
"""

THL = -300    # default threshold value, can be modified
              # decreasing (smaller absolute value) will increase recorded data size considerably
              # increasing (larger absolute value) will help in noisy EM environments

SAVE_DATA = True            # save recorded pulses in .pkl file for later analysis
DATA_FOLDER = "./data"      # folder for saving recorded data files (create folder if missing)
ENABLE_SONIFICATION = False # (requires pyo module, https://github.com/belangeo/pyo)
MIN_ALPHA_PEAK = -1243      # threshold to distinguish between alpha and electron pulses
                            # as obtained from reference measurements


import sys
import time
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np
import pyqtgraph as pg
import pyaudio
import pandas as pd
import datetime
import random
if ENABLE_SONIFICATION: import pyo


RATE = 48000       # audio sampling rate, should stay like this.
                   # other rates might require new energy calibration
                   # and will in any case require modification of analysis scripts
FRAME_SIZE = 4096  # size of waveform frame size. could be modified, but not tested

if ENABLE_SONIFICATION:
    s = pyo.Server(duplex=0).boot()
    s.deactivateMidi()
    s.setOutputDevice(1)
    pyo.pa_list_devices()
    s.start()
    tab_m = pyo.HarmTable([1,0,0,0,0,.3,0,0,0,0,0,.2,0,0,0,0,0,.1,0,0,0,0,.05]).normalize()
    tab_p = pyo.HarmTable([1,0,.33,0,.2,0,.143,0,.111])

class Ring:

    def __init__(self, fport=250, fmod=100, amp=.3):
        self.mod = pyo.Osc(tab_m, freq=fmod, mul=amp)
        self.port = pyo.Osc(tab_p, freq=fport, mul=self.mod)

    def out(self):
        self.port.out()
        return self

    def sig(self):
        return self.port

class Scope(QtGui.QMainWindow):
    def __init__(self, parent=None):
        global app
        QtGui.QMainWindow.__init__(self, parent)
        #super(Scope, self).__init__(parent)
        #QtGui.QApplication.setGraphicsSystem("raster")
        #try:
        #    self.app = QtGui.QApplication(sys.argv)
        #except RuntimeError:
        #    self.app = QtGui.QApplication.instance()
       
        self.save_data = SAVE_DATA
        self.sound = ENABLE_SONIFICATION # trigger sounds for each pulse or not
        
        self.app = app
        self.app.aboutToQuit.connect(self.close)
        self.pcounter=0
        self.creation_time=datetime.datetime.now()
        
        self.df = pd.DataFrame(columns = ['ts','ptype'])
        self.ptypes = pd.Series(["alpha", "beta", "betagamma", "x-ray", "muon" ,"unknown"], dtype="category")

        self.thl =  THL
        self.traces=[]
        
        if ENABLE_SONIFICATION:
            # setup some wild Karplus-Strong oscillator
            self.lf = pyo.Sine(.03, mul=.2, add=1)
            self.rg = Ring(fport = [random.choice([62.5,125,187.5,250]) * random.uniform(.99,1.01) for i in range(8)],
                                    fmod = self.lf * [random.choice([25,50,75,100]) * random.uniform(.99,1.01) for i in range(8)],
                                    amp = 0.1)
            self.env = pyo.Adsr(attack=0.01, decay=0.1, sustain=0.5, release=1.5, dur=5, mul=0.1)
            self.res = pyo.Waveguide(self.rg.sig(), freq=[30.1,60.05,119.7,181,242.5,303.33], dur=30, mul=1*self.env).out()
        
        def audio_callback(in_data, frame_count, time_info, status):
            now = time.time()
            samples = np.frombuffer(in_data, dtype=np.int16)
            peak = samples.min()
            if  peak < self.thl:
                t =  pd.datetime.fromtimestamp(now)
                print("* ", t, end="")
                pulse = pd.DataFrame()
                pulse = pulse.assign(ts=[t])
                if peak < MIN_ALPHA_PEAK:
                    pulse = pulse.assign(ptype=[self.ptypes[0]]) #alpha
                    print("   alpha  ", end="")
                else:
                    pulse = pulse.assign(ptype=[self.ptypes[1]]) #beta/electron
                    print("   elect   ", end="")
                if self.sound:
                    self.lf.setMul(abs(int(samples.sum()))/200000)
                    self.env.dur = abs(int(samples.sum()))/40000
                    self.env.play()
                print(self.pcounter, "  ", end="")
                print(peak)
                pulse = pulse.assign(pulse=[samples])
                self.df = self.df.append(pulse, ignore_index=True,sort=False)
                self.pcounter+=1
                # calculate pulse rate in counts per second
                dt = (now-self.lastupdate)
                if dt <= 0:
                    dt = 0.000000000001
                cps2 = 1.0 / dt
                self.lastupdate = now
                self.cps = self.cps * 0.9 + cps2 * 0.1 # simple weighted average
                tx = 'Mean pulse rate:  {cps:.3f} CPS'.format(cps=self.cps )
                self.label.setText(tx)
                self.ydata=np.frombuffer(in_data, dtype=np.int16)
                self.frame_counter+=frame_count
                self.h2.setData(self.ydata)
            self.thlp.setData(FRAME_SIZE*[self.thl])
            return (in_data, pyaudio.paContinue)
 
    
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.otherplot = self.canvas.addPlot()        
        self.h2 = self.otherplot.plot(pen='y')
        self.thlp = self.otherplot.plot(pen='y')

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=FRAME_SIZE,stream_callback=audio_callback)


        #### Set Data  #####################

        self.x = np.linspace(0,50., num=100)
        self.X,self.Y = np.meshgrid(self.x,self.x)

        self.frame_counter = 0
        self.cps = 0.
        self.lastupdate = time.time()
        
        
        self.sh = QtGui.QShortcut(QtGui.QKeySequence("+"), self, self.thl_down); 
        self.sh.setContext(QtCore.Qt.ApplicationShortcut)
        self.sh2 = QtGui.QShortcut(QtGui.QKeySequence("-"), self, self.thl_up); 
        self.sh2.setContext(QtCore.Qt.ApplicationShortcut)     
        #self.sh3 = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self.close)
        #self.sh.setContext(QtCore.Qt.ApplicationShortcut)

        #### Start  #####################
        self.stream.start_stream()
    
    def thl_up(self):
        self.thl+=1
        print(self.thl)

    def thl_down(self):
        print(self.thl)
        self.thl-=1
        
    def close_stream(self):
        self.stream.close()
        self.stream.stop_stream()
        print("Stream closed")
        
    def close(self):
        timediff = datetime.datetime.now() - self.creation_time
        self.close_stream()
        if self.save_data and self.pcounter > 0:
            print("Saving data to file...")
            #print(self.df.to_string)
            td_str = '-'.join(str(timediff).split(':')[:2])
            _ = self.df.to_pickle(DATA_FOLDER + self.creation_time.strftime("/pulses_%Y-%m-%d_%H-%M-%S") + "___" + str(self.pcounter) + "___" + td_str + ".pkl")
            print("Saving completed.")
            print()
            print('Number of recorded waveforms:', self.pcounter, "of",self.frame_counter, "total audio frames")
            print('at least', len(self.df[self.df['ptype'] == 'alpha']) ,"alphas and") 
            print('at least', len(self.df[self.df['ptype'] == 'beta']) ,"electrons/betas were detected") 
        self.p.terminate()
        app = QtGui.QApplication([])
        app.closeAllWindows()
        app.quit()
        app.exit()
        print('done.')

        
if __name__ == '__main__':
    #app = pg.mkQApp()
    # app = QtWidgets.QApplication(sys.argv)
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance() 
    mainWin = Scope()
    mainWin.show()
    #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    app.exec_()
    if ENABLE_SONIFICATION: s.stop()


