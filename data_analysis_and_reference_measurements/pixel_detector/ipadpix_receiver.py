#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Receives UDP packets from iPadPix over WiFi.
Applies cluster classification and stores results as pandas data frame in python's .pkl format
Recording is stopped and data saved after hitting Ctrl-C.
Prints histogram overview plots when finished.

Requirements besides numpy, pandas and matplotlib modules:
avro-python3 module version 1.8.2.

@author: Oliver Keller
@date: February 2019
"""

import avro.schema
import avro.io
import socket, io
import struct
import datetime
import pandas as pd
import numpy as np
import time
import sys
import matplotlib.pyplot as plt

HOSTNAME = 'ozelmacpro.local' # specifiy correct hostname or IP to listen on the right network interface
UDP_PORT = 8123

# <codecell>

def resample(df, unit, period = 1):
    if unit == 'm':
        pdOffsetAlias = 'min' #equals 'T'!
    else: 
        pdOffsetAlias = unit
        
    dg = df.groupby([pd.Grouper(freq=str(period)+pdOffsetAlias, key='ts'),'ptype']).size().unstack()
    dgtd = dg.index  - dg.index[0]
    dgtd = dgtd.astype('timedelta64[' + unit + ']').astype(int)
    dg = dg.set_index(dgtd)
    dg.index.name = '[' + pdOffsetAlias + ']'
    dg = dg.fillna(0)
    return dg
                   
# <codecell>

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if sys.platform == "linux":
    # used more precise socket receive timestamps under unix
    SO_TIMESTAMPNS = 35 #Linux?
    sock.setsockopt(socket.SOL_SOCKET, SO_TIMESTAMPNS, 1)
sock.bind((HOSTNAME, UDP_PORT))

schema = avro.schema.Parse(open("ipadpix_schema.json").read())
ptypes = pd.Series(["alpha", "beta", "betagamma", "x-ray", "muon" ,"unknown"], dtype="category")
df = pd.DataFrame(columns = ['ptype','x','y','tot','energy', 'ts'])
df = df.astype(dtype= {"ptype" : "category"})

# Reading avro bytes from UDP packets
counter=0
creation_time=0
while True:
    try:
        # with open('/tmp/pipe.avro', 'rb') as fifo:
        # data = sock.recv(4096)
        data, ancdata, flags, address = sock.recvmsg(4096, 1024)
        #print(ancdata, '-', flags, '-', address)
        if sys.platform == "linux":
            # get precise socket timestamps
            if len(ancdata) > 0:
                # print(len(ancdata),len(ancdata[0]),ancdata[0][0],ancdata[0][1],ancdata[0][2])
                # print('ancdata[0][2]:',type(ancdata[0][2])," - ",ancdata[0][2], " - ",len(ancdata[0][2]));
                for i in ancdata:
                    # print('ancdata: (cmsg_level, cmsg_type, cmsg_data)=(',i[0],",",i[1],", (",len(i[2]),") ",i[2],")");
                    if i[0] != socket.SOL_SOCKET or i[1] != SO_TIMESTAMPNS:
                        continue
                    tmp = (struct.unpack("iiii", i[2]))
                    timestamp = tmp[0] + tmp[2] * 1e-10
        else:
            timestamp = time.time()
        if counter ==0:
            creation_time = datetime.datetime.now()
    
        #dt = datetime.datetime.fromtimestamp(timestamp)
        #dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        #print("SCM_TIMESTAMPNS,", tmp, ", timestamp=", timestamp, dt, pd.datetime.fromtimestamp(timestamp))
        # data = fifo.read()
        if len(data) == 0:
            print("Writer closed")
            break
        tmp = io.BytesIO(data)
        decoder = avro.io.BinaryDecoder(tmp)
        reader = avro.io.DatumReader(schema)
        records = reader.read(decoder)
        
        # # #
        # CLUSTER ANALYSIS
        # # #
        
        for cluster in records['clusterArray']:
            df_new = pd.DataFrame()
            xi = np.array(cluster['xi'], dtype=np.int64)
            yi = np.array(cluster['yi'], dtype=np.int64)
            ei = np.array(cluster['ei'], dtype=np.int64)
            energy = cluster['energy']
            
            df_new = df_new.assign(x=[xi])
            df_new = df_new.assign(y=[yi])
            df_new = df_new.assign(tot=[ei])
            df_new = df_new.assign(energy=energy)
            df_new = df_new.assign(ts=pd.datetime.fromtimestamp(timestamp))
    
            
            max_x = xi.max()
            max_y = yi.max()
            min_x = xi.min()
            min_y = yi.min()
    
            width = max_x - min_x + 1
            height = max_y - min_y + 1
            
            area = height*width
            cluster_size = len(xi)
            occupancy = float(cluster_size/float(area))
            
            cluster_type = ptypes[5] 
            
            if ( (width <= 2 or height <=2) and cluster_size <=4):
                #beta/gamma or xray
                if (energy < 10):
                    cluster_type = ptypes[3] #x-ray
                else:
                    cluster_type = ptypes[2] #betagamma
            elif (occupancy > 0.5):
                if (energy > 1000):
                    cluster_type = ptypes[0] #alpha
                elif (width == 1 or height ==1):
                    cluster_type = ptypes[4] #muon
                #        elif 1:
                #            pass #print(testLinearity(x,y))
                #            #cluster_type = 4 #ptype['muon']
                else:
                    cluster_type = ptypes[5] #unknown
            elif (energy > 200):
                cluster_type = ptypes[1] #beta
            else:
                cluster_type = ptypes[2] #betagamma
        
            df_new = df_new.assign(ptype = cluster_type)
            #clusters[cluster_index].x = x.astype('<u4')
            #clusters[cluster_index].y = y.astype('<u4')
            df = df.append(df_new, ignore_index=True,sort=False)
            print(cluster_type)
            counter+=1
        
    except KeyboardInterrupt:
        print()
        if creation_time:
            timediff = datetime.datetime.now() - creation_time
            if timediff < datetime.timedelta(seconds=60):
                dg = resample(df, 's', 1)
            else:
                dg = resample(df, 'm', 1)
            plt.figure();
            dg.hist() # quick overview plot
            print(df.to_string())
            td_str = ':'.join(str(timediff).split(':')[:2])
            df.to_pickle("./data/" + creation_time.strftime("%Y-%m-%d_%H:%M:%S") + "___" + str(counter) + "___" + td_str + ".pkl")
        else:
            print("no data received!")
        sys.exit()
