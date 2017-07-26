#!/usr/bin/python3
 
from random import randint
import sys
import struct 
import numpy as np
import time
import glob
import _thread
import random

from matplotlib.pylab import *
import matplotlib.pyplot as plt
import matplotlib.animation as anim

from time import sleep
from collections import deque

import scipy.signal as signal
import scipy.io.wavfile as wavfile
import collections
import matplotlib.dates as mdate
import datetime as dt

from multiprocessing import Process, Queue

# Audio chunk size
CHUNK=1024*2

# Number of CPU cores to use
CORES=8

# Try to remove false bubbles
def remove(ny):
    for i in range(0,len(ny)):
        zeroidx = -1
        if ny[i] == 1:
            count = 1
            for i2 in range(i+1,len(ny)):
                if ny[i2] == 1:
                    count += 1
                else: 
                    if ny[i2] == 0:
                        zeroidx = i2
                        break
            zz = i+1
            if count > 7:
                zz = i

            for i2 in range(zz,zeroidx):
                ny[i2] = 0
            
            i = zeroidx

    return ny

# Generate data for the graph
def data_gen(filename):

    wav = wavfile.read(filename)[1]
    r = 0

    while True:
 
        data = wav[r:r+CHUNK]

        if len(data) != CHUNK:
            break
        
        fft = np.fft.fft(data)
        fft = np.abs(fft[0:int(len(fft)/2)])

        mags = []   
        c = 0                                                                        
        
        for v in fft:                                                                                                      
            if v > 40000:
                mags.append(c)   
            c += 1 
                 
        r += CHUNK

        yield mags

q = Queue()
plist = []

def process(filename,epoch,q):
    
    y = []
    x = []
    i=1

    for v in data_gen(filename):

        if len(v) > 24 and max(v) > 50:
            y.append(1)
        else: 
            y.append(0)

        x.append((epoch-(60*60))+((CHUNK/48e3)*i))
        i+=1
    
    q.put((x,y,epoch))


data = {}

lines = []

# Load file with timestamp data
with open('wav/txt') as fin:
    for line in fin: 
        v = line.split(",")
        ep = int(v[0])
        wfile = v[1][1:-2]
        lines.append(("wav/"+wfile,ep))

c = 1

# Spawn processes to process each wav file
for l in lines:

    p = Process(target=process, args=(l[0],l[1],q,))
    plist.append(p)
    p.start()

    print("starting")
    if len(plist) == CORES or c == len(lines):
        for p in plist:
            job = q.get()
            data[job[2]] = ( job[0] , job[1] )
        for p in plist:
            p.join()
        plist = []
        q = Queue()

    c += 1

y = []
x = []

# Sort data from the multiple processes
od = collections.OrderedDict(sorted(data.items()))
for k, v in od.items():
    for val in range(0,len(v[0])):
        x.append(v[0][val])
        y.append(v[1][val])

y = remove(y)

newy = []
newx = []

count = 0

tval = x[0]

# Extract bubbles per minute data
for i in range(0,len(x)):

    if y[i] == 1:
        count += 1

    if x[i] > tval + (60):
        newy.append(count)
        newx.append(tval)
        tval = x[i]
        count = 0

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)

fig = plt.figure()
ax = fig.add_subplot(111)
secs = mdate.epoch2num(newx)
ax.plot_date(secs,newy,'r-')

date_fmt = '%d-%m-%y %H:%M:%S'
date_formatter = mdate.DateFormatter(date_fmt)
ax.xaxis.set_major_formatter(date_formatter)
fig.autofmt_xdate()

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
yhat = signal.savgol_filter(newy, 31, 3) # window size 31, polynomial order 3

ax2.plot_date(secs,yhat,'b-')
ax2.xaxis.set_major_formatter(date_formatter)
fig2.autofmt_xdate()

plt.show()
