#!/usr/bin/env python3

import pyaudio
import numpy as np

import os
import sys
import time
from itertools import cycle

this_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_folder)
from flux_led import WifiLedBulb, BulbScanner, LedTimer

np.set_printoptions(suppress=True) # don't use scientific notation

CHUNK = 1024*4 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)
maxValue = 2**16

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK) #uses default input device

# Find the bulb on the LAN
scanner = BulbScanner()
scanner.scan(timeout=4)

r=0
g=0
b=0
# Specific ID/MAC of the bulb to set 
bulb_info = scanner.getBulbInfoByID('ACCF235FFFFF')
if bulb_info:	
	bulb = WifiLedBulb(bulb_info['ipaddr'])
	bulb.setRgb(255,0,0, persist=False)
	# create a numpy array holding a single read of audio data
	while True: #to it a few times just to see
		data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
		
		dataL = data[0::2]
		dataR = data[1::2]
		peakL = np.abs(np.max(dataL)-np.min(dataL))/maxValue
		peakR = np.abs(np.max(dataR)-np.min(dataR))/maxValue
		#print("L:%00.02f \tR:%00.02f"%(peakL*100, peakR*100))
	
		data = data * np.hanning(len(data)) # smooth the FFT by windowing data
		fft = abs(np.fft.fft(data).real)
		fft = fft[:int(len(fft)/2)] # keep only first half
		freq = np.fft.fftfreq(CHUNK,1.0/RATE)
		freq = freq[:int(len(freq)/2)] # keep only first half
		freqPeak = freq[np.where(fft==np.max(fft))[0][0]]+1
		#print("peak frequency: %d Hz"%round(freqPeak))
		
		bulb.refreshState()
		h = round((peakL+peakR)/2*250/4)
		#h = round((freqPeak)/3000*250)
		
		if freqPeak<300 and freqPeak>5:
			r = r+20
		if freqPeak<3500 and freqPeak>300:
			g = g+2
		if freqPeak>2000:
			b = b+5			
		if r>255/2:
			r=255/2
		if g>255/2:
			g=255/2
		if b>255/2:
			b=255/2
		if h>255/2:
			h=255/2
		bulb.setRgb(r+h,g+h,b+h, persist=False)
		r = r-1
		g = g-1
		b = b-1
		if r<0:
			r=0
		if g<0:
			g=0
		if b<0:
			b=0
		# uncomment this if you want to see what the freq vs FFT looks like

# close the stream gracefully
stream.stop_stream()
stream.close()
p.terminate()