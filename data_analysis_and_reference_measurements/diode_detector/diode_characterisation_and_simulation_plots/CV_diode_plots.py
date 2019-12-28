#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for plotting the recorded C-V measurement curves, 
including derived depletion depth and effective charge carrier concentration 
(Neff) plots.

@author: Oliver Keller
@date: March 2019
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from os import listdir
from matplotlib.collections import PathCollection
from matplotlib.legend_handler import HandlerPathCollection
import decimal as D

mpl.rcParams['font.size']=13 #default font size

# enable for cleaning the regular mico pattern in the Neff plots, suggests data 
# is affeted by rounding errors introduced by the instrument
FILTER_ROUNDING_ARTEFACTS = False 

## constants

e0 = 8.854e-14 #F/cm
eSi = 11.9 #for Si
q = 1.602e-19 # charge in Coulomb = F/V
A = 0.0702 # diode area in cm^2

### helper functions
 
def oneOverX(x, a, b,c,d,e):
  #return a * np.exp(-b * x) + c
  return (a/(b * (x**c + d))) + e

def depth(C):
    return eSi*e0*A/C

def Neff(oneOverCsq,dV):
    oneOverCsq=oneOverCsq #*1e15
    # following https://cds.cern.ch/record/1169276/files/04636908.pdf
    # unit analysis suggests Neff output is in [1/cm]
    dCdV = np.gradient(oneOverCsq,dV) #/1e15
    return 2/(q * eSi * e0 * (A**2) * dCdV)
    
### read measurement series and prepare data

df = pd.DataFrame()
folder = "../data/high_resolution_CV/"
filepaths = [f for f in listdir(folder) if f.endswith('.csv')]
filepaths.sort()
count = 0
for file in filepaths:
    with open(folder+file) as f:
        head = [next(f) for x in range(15)]
        deviceName = head[9].split()[2]
        #print(deviceName)
    
    anode = 'Vanode'
    # using Decimal here to preserve original precision of numbers (reaveals rounding errors in data)
    df_new = pd.read_csv(folder+file, skiprows=1407, sep=',' ,      converters={anode: D.Decimal, 'Cp': D.Decimal}, engine='c', skipinitialspace= True, float_precision='round_trip') #149
    #df_new = pd.read_csv(folder+file, skiprows=1407, sep=',' ,  dtype={1:np.float128,2:np.float128,5:np.float128}, engine='c', skipinitialspace= True, float_precision='round_trip') #149

    # dropping large precision numbers for testing (rounding problems of instrument?)
    # c.f. patterns in Neff plots
    # most of the regular micro pattern in Neff is filtered out by this!
    if FILTER_ROUNDING_ARTEFACTS:
        df_tmp = df_new
        for index, row in df_tmp.iterrows():
            s = str(row['Cp'])
            len = s.rindex(s[-1]) + 1
            if len > 11:
                df_new = df_new.drop(index)
                print(index)
    
    if count ==0:
         df['VBias'] = df_new[anode].astype(dtype='float128')
         df = df.assign(VBias = np.abs(df.VBias))
    count+=1
    df[deviceName] = df_new['Cp'].astype(dtype='float128')
    # calculate errors
    df_new['err']=0
    df_new['err'] = df_new['err'].astype(dtype='float128')
    df_new.loc[df_new.D <= 0.1, 'err'] = 0.11/100
    df_new.loc[df_new.D > 0.1, 'err'] = (0.11 * np.sqrt(1+ (df_new.D**2)))/100
    df[deviceName + '_err'] = df_new['err']
    # calculate 1/C^2
    df[deviceName + '_cc'] = 1.0/(df[deviceName].values * df[deviceName].values)

# <codecell>
    
           
def plotNeff(df, columns,colors):
    fig = plt.figure()
    plot = fig.add_subplot(111)
    i =0
    for column in df[columns]:
        print(column)
        # RAW C data to Neff
        d_raw = depth(df[column].values)*10000 # in um
        neff_raw = Neff(df[column+'_cc'], df.VBias)#df.VBias[1]-df.VBias[0] )#df.VBias.values)

        cc_err_max = 1.0/((df[column]*(1+df[column+'_err'].values)) * (df[column]*(1+df[column+'_err'].values)))
        cc_err_min = 1.0/((df[column]*(1-df[column+'_err'].values)) * (df[column]*(1-df[column+'_err'].values)))
        neff_err_max = Neff(cc_err_max, df.VBias)
        neff_err_min = Neff(cc_err_min, df.VBias)
        
        plot.plot(d_raw,neff_err_max, linewidth=0.1,color=colors[i])
        plot.plot(d_raw,neff_err_min, linewidth=0.1,color=colors[i])
        plot.scatter(x=d_raw, y=neff_raw,s=1.5,marker='d', label=column, color=colors[i])        
        
        i+=1
    txt = r"\n(errors are smaller than marker symbols)"
    plot.set_xlabel('Depletion layer depth ['+u'\u03bc'+'m]') #+ txt )
    plot.set_ylabel('Neff [cm$^{-3}$]')
    plot.set_yscale('log')
    plot.set_xscale('log')
    def update1(handle, orig):
        handle.update_from(orig)
        handle.set_sizes([30])
    plot.legend(handler_map={PathCollection : HandlerPathCollection(update_func=update1)},fontsize=10,scatterpoints=1,loc=4)
    plot.set_xticklabels(list(map(str, [0.1,1,10,100]))) # WARNING: adapt in case of other changes
    fig.tight_layout(pad=0.2)


def plotCV(df,columns,colors):
    ### plot C-V curve
    fig = plt.figure()
    plot = fig.add_subplot(111)
    i = 0
    for column in df[columns]:
        plot.errorbar(df.VBias,df[column],yerr=df[column]*df[column+'_err'].values,fmt='s',markeredgewidth=1,markersize=3,label=column,markerfacecolor='none',color='none', markeredgecolor=colors[i])
        i +=1
    txt = r"\n(errors are smaller than marker symbols)"
    plot.set_ylabel('Capacitance [pF]', fontsize=14)
    plot.set_xlabel('Reverse bias voltage [|V|]', fontsize=14)#+ txt )
    plot.set_yscale('log')
    plot.set_xscale('log')
    def update2(handle, orig):
        handle.update_from(orig)
        handle.set_sizes([100])
    plot.legend(handler_map={PathCollection : HandlerPathCollection(update_func=update2)},fontsize=10,scatterpoints=5)
    plot.grid(which='minor',linewidth=0.5)
    plot.grid(which='major',linewidth=1.0)
    plot.set_xticklabels(list(map(str, [0.001,0.01,0.1,1,10]))) # WARNING: adapt in case of other changes
    plot.set_yticklabels(list(map(str, [0.1,1,10,100,1000]))) # WARNING: adapt in case of other changes
    fig.tight_layout(pad=0.2)


def plotDepth(df,columns,colors):
    fig = plt.figure()
    plot = fig.add_subplot(111)
    i = 0
    for column in df[columns]:
        plot.plot(df.VBias,depth(df[column])*10000,label=column, color=colors[i])
        i +=1
    plot.set_ylabel('Depletion layer depth [' + u'\u03bc' + "m]", fontsize=14)
    plot.set_xlabel('Reverse bias voltage [|V|]', fontsize=14)
    plot.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    plot.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    plot.legend()
    plot.grid(True,which='minor',linewidth=0.5)
    plot.grid(True,which='major',linewidth=1.0)
    plot.set_xlim(-1,25)
    fig.tight_layout(pad=0.2)

df = df.replace(-np.inf, np.nan)
df = df.dropna()
    
# <codecell>
plotNeff(df,['BPX61-1','BPX61-2','BPX61-3','BPW34-1','BPW34-2','BPW34-3','BPW34F-1','BPW34F-2','BPW34F-3','BPW34FA-1'],
            ['firebrick','red','salmon','olive','yellowgreen','lawngreen','blue','royalblue','dodgerblue','lightblue'])
# <codecell>
plotDepth(df,['BPW34-3','BPX61-2','BPW34F-3'],
              ['lawngreen','red','dodgerblue'])
# <codecell>
plotCV(df,['BPX61-1','BPX61-2','BPX61-3','BPW34-1','BPW34-2','BPW34-3','BPW34F-1','BPW34F-2','BPW34F-3','BPW34FA-1'],
            ['firebrick','red','salmon','olive','yellowgreen','lawngreen','blue','royalblue','dodgerblue','lightblue'])
