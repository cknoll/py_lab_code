# -*- coding: utf-8 -*-

# Author
# "Carsten.+".replace('+', 'Knoll@') + "tu-dresden.de"

"""
Example Python-Script for reading binary Information from an
Arduino microcontroller via serial interface.

Basic idea: the code should be flexible w.r.t. data type and number of the
transferred variables
"""

import numpy as np
np.set_printoptions(linewidth=300, precision=4)

import serial
import time

import struct




port = '/dev/ttyUSB0'
bauds = 115200
ser = serial.Serial(port, bauds, timeout=2)

L = []
ser.flushInput()

# how many bytes we want to read?

N= 10*36*20

while len(L) < N:
    if len(L) % int(N/10.0)== 0:
        print int(len(L) *100.0/N), "%"
    i = ser.inWaiting()
    if  i < 1:
        time.sleep(0.005)
        continue
    ret = ser.read(i)

    L+=ret

ser.close()






# One protocol meassage from the micro controller consists of several bytes
# The first two bytes are the characters "AA"
# The following bytes might be part of FLOATs, INTs ULONGs etc.

# The following codes converts the recieved bytes from the protocol message
# to proper variables (according to protocol_signature)


class Container():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)



# see http://docs.python.org/library/struct.html
# arduino uses little endian

FLOAT = Container(len = 4, fmt = 'f')
STRING2 = Container(len = 2, fmt = '2s')
INT = Container(len = 2, fmt = 'h') # arduino int -> short
ULONG = Container(len = 4, fmt = 'L')


protocol_signature = [STRING2] + [FLOAT]*6 + [INT, ULONG, ULONG]



# 'AA' is the opening code for a new data protocol
# find all indeces of 'A'
idcs =  [i for i,s in enumerate(L) if s == 'A' ]

# find the the first occurrence of 'AA'
for i in range(len(idcs)-1):
    if idcs[i+1]-idcs[i] == 1:
        break

idx = idcs[i]



protocol_length = sum([part.len for part in protocol_signature])

# pms = Protocoll MeaSsage

def divide_into_pms(L):
    """
    takes a list of bytes and splits them up to protocol messages (pms), i.e.
    smaller lists of bytes each one starting with "AA" and having
    length == protocol_length
    """

    assert L[:2] == ['A']*2

    N = int(len(L)/protocol_length)

    results = []
    for i in range(N):
        L2 = L[i*protocol_length:(i+1)*protocol_length]

        results.append(L2)

    return results



def interpret_pms(bytelist):
    """
    takes one protocol_message and converts the bytes according the
    protocol_signature
    """

    assert len(bytelist) == protocol_length

    fmt = '<' + ''.join([p.fmt for p in protocol_signature])

    return struct.unpack(fmt, ''.join(bytelist))



L2 = divide_into_pms(L[idx:]) # -> List of lists of bytes


L3 = [interpret_pms(LL) for LL in L2] # -> List of lists of values

res = np.array([np.array(l[1:]) for l in L3]) # 2d array (without "AA"-strings)


# save the result


t = time.localtime()
date_string = "%02i%02i_%02i%02i" % (t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min)
fname = date_string + ".dat"


np.savetxt(fname, res)
print fname, "written"

