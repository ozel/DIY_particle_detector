#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for plotting time series measurements recorded by ipadpix_receiver.py as 
histograms. Measurements are loaded from pandas dataframes stored in python's 
.pkl format.

@author: Oliver Keller
@date: July 2019
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

def calib_tot(tot, correct=False):
    # Maps pixel tot values to energy in keV, 
    # algorithm extracted from MAFalda https://github.com/idarraga/mafalda.
    # Correction for large pixel energies added.

    # calibration values a,b & c as used in iPadPix
    # further details: CERN-THESIS-2015-169
    
    a = 1.54505
    b = 50.6605 - (1.54505*1.19535) - tot
    c = -141.279 - (1.19535*50.6605)  + (tot*1.19535)

    sol1 = (-b) + (math.sqrt(b*b - (4*a*c)))
    sol1 /= 2*a
    sol2 = (-b) - (math.sqrt(b*b - (4*a*c)))
    sol2 /= 2*a
    
    energy_kev = 0
    
    if (sol1 > 0 and sol2 > 0): #If both solution are positive
        maxsol = sol1
        if(sol2 > maxsol): 
            maxsol = sol2
        energy_kev = maxsol
    elif(sol2 <= 0 and sol1 > 0):
        energy_kev = sol1 #Otherwise use the positive solution
    else:
        energy_kev = sol2
    if correct and energy_kev > 850:
        # correction function from M. Kroupa 2017
        # https://doi.org/10.1063/1.4978281
        energy_kev = (0.36 * energy_kev) + 780
    return energy_kev


def overlapped_bar(df, show=False, width=0.98, alpha=1,
                   title='', xlabel='', ylabel='', **plot_kwargs):
    """Like a stacked bar chart except bars on top of each other with transparency"""
    # https://stackoverflow.com/a/38257929
    xlabel = xlabel or df.index.name
    N = len(df)
    M = 2 #len(df.columns)
    indices = np.arange(N)
    colors = [u'#1f77b4','firebrick', 'darksage', 'goldenrod', 'gray', 'brown'] * int(M / 6. + 1)
    for i, label, color in zip(range(M), df.columns, colors):
        print(i,label,color)
        kwargs = plot_kwargs
        kwargs.update({'color': color, 'label': label})
        plt.bar(indices, df[label], width=width, alpha=alpha if i else 1, **kwargs)
        plt.xticks(indices - .5 * width, ['{}'.format(idx) for idx in df.index.values])
        #plt.xticks(indices, ['{}'.format(idx) for idx in df.index.values])

    plt.title(title)
    plt.xlabel(xlabel, fontsize='x-large')
    plt.ylabel('Counts', horizontalalignment='right', y=1.0, fontsize='x-large')
    if show:
        plt.show()
    return plt.gcf()

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
#####################
# creation of plots #
#####################
#
# KCl dataset
#
df = pd.read_pickle("./data/KCL_block_bare_2019-02-11_20-54-41___1083___1-03.pkl")

dg = resample(df, 'm', 3)
#plt.rcParams.update({'font.size': 16})
fig = plt.figure(figsize=(21,7))

r = pd.DataFrame()

# assemble result for bar plot, data with highest counts first
#r['beta & gamma'] = dg.beta + dg.betagamma 
r['beta & gamma'] = dg.beta + dg.betagamma + dg.muon + dg.unknown + dg['x-ray'] # everything but alpha
r['alpha'] = dg.alpha
#r['other'] = dg.muon + dg.unknown + dg['x-ray']

overlapped_bar(r,xlabel = 'Time [min]', ylabel='Counts')
leg = plt.legend([r'all clusters except $\alpha$' "\n" r'($\beta$,$\gamma$,$\mu$,$X$-$ray,unknown$)', r'$\alpha$-particle clusters'], fontsize = 'x-large', bbox_to_anchor=(1.01,1), borderaxespad=0)
leg.set_title(title="Pixel cluster categories:",prop={'size':'x-large'})

fig.tight_layout(pad=0)

# <codecell>    

# Radon Balloon dataset
df = pd.read_pickle("./data/3hoursRadonBalloon_2019-02-10_14-43-21___2321___2-56.pkl")

dg = resample(df, 'm', 8)
fig = plt.figure(figsize=(14,7))

# assemble result for bar plot, data with highest counts first
r = pd.DataFrame()
r['beta & gamma'] = dg.beta + dg.betagamma 
#r['beta & gamma'] = dg.beta + dg.betagamma + dg.muon + dg.unknown + dg['x-ray'] # everything but alphas
r['alpha'] = dg.alpha
#r['other'] = dg.muon + dg.unknown + dg['x-ray']

overlapped_bar(r,xlabel = 'Time [min]', ylabel='Counts')
leg=plt.legend([r'$\beta$- & $\gamma$-particles',r'$\alpha$-particles'],fontsize = 'xx-large')
leg.set_title(title="Pixel cluster categories:",prop={'size':'xx-large'})
fig.tight_layout(pad=0)

# <codecell>

# plot alpha energy histogram without correction

fig = plt.figure()

df[df.ptype == 'alpha'].energy.hist(bins=30,grid=False)
alphas = df[df.ptype == 'alpha']

# <codecell>
#
# alpha energy histogram after applying energy corerction

corr_e= []
for cluster,row in alphas.iterrows():
    energies = []
    for i in row.tot:
        e=calib_tot(i, correct=True)
        energies.append(e)
    tot_kev = sum(energies)
    corr_e.append(tot_kev)
    if 0 and tot_kev > 8000:
        # show certain clusters if needed
        # e.g. check for pile-up/overlap
        x = alphas.loc[cluster].x
        y = alphas.loc[cluster].y
        tot = alphas.loc[cluster].tot
        fig2 = plt.figure()
        cluster = fig2.add_subplot(111)
        cluster.set_title(round(tot_kev))
        scat = cluster.scatter(x, y, c=energies, marker='s', s=1800, linewidths=0)
        plt.colorbar(scat)

corr_e = np.asarray(corr_e)
print(corr_e)

fig3 = plt.figure(figsize=(7,6))
corr_energy = fig3.add_subplot(111)
(entries, edges,patches) = corr_energy.hist((corr_e/1000), bins=12, histtype='step')
bin_centers = 0.5 * (edges[:-1] + edges[1:])
corr_energy.errorbar(bin_centers, entries, yerr=np.sqrt(entries), fmt='none', capsize=3,color="black", ecolor='black', elinewidth=0.8, label="measured KCl spectrum")
corr_energy.set_xlabel("Energy [MeV]", fontsize='large')
plt.ylabel('Counts', horizontalalignment='right', y=1.0, fontsize='large')
fig3.tight_layout(pad=0)
    