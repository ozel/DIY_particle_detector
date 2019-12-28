#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for plotting the results from the AASI alpha particle simulation software V2.0.
AASI is available for free here:
https://www.stuk.fi/web/en/services/aasi-program-for-simulating-energy-spectra-in-alpha-spectrometry/thank-you-for-your-registration-download-the-aasi-program
Corresponding simulation parameters that were used are stored in ./sim/AASI-settings.

@author: Oliver Keller
@date: July 2019
"""
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import decimal as D

mpl.rcParams['font.size']=13 #default font size


# estimated centroid positions as found in AASI simulation (zero/threshold value from x-ray calibration)
ref = np.asarray([33,1300, 3893, 4290, 4636]) # 11mm of air (1.123 kg/m^3 density) between detector and source

# AASI simulation results are already binned (unfortunatelly... but can be defined in AASI)
# original binning is used here

ticks_minor = np.arange(0.5,5,1) #minor 0.5 Mev

fig2 = plt.figure()
h2 = fig2.add_subplot(111)

h2.set_ylim(0,1430) # scaling roughly to the Gd148 peak size in measured histogram

sum_mev = pd.read_csv("../sim/sum_of_Pu-Am-Cm.txt", skiprows=0, sep='\t' ,      converters={'Energy': D.Decimal, 'Counts': D.Decimal}, engine='c', skipinitialspace= True, float_precision='round_trip')
gd_mev = pd.read_csv("../sim/Gd_148_3084000.txt", skiprows=0, sep='\t' ,      converters={'Energy': D.Decimal, 'Counts': D.Decimal}, engine='c', skipinitialspace= True, float_precision='round_trip')
pu_mev = pd.read_csv("../sim/Pu_239_3108000.txt", skiprows=0, sep='\t' ,      converters={'Energy': D.Decimal, 'Counts': D.Decimal}, engine='c', skipinitialspace= True, float_precision='round_trip')
am_mev = pd.read_csv("../sim/Am_241_3422000.txt", skiprows=0, sep='\t' ,      converters={'Energy': D.Decimal, 'Counts': D.Decimal}, engine='c', skipinitialspace= True, float_precision='round_trip')
cm_mev = pd.read_csv("../sim/Cm_244_2258000.txt", skiprows=0, sep='\t' ,      converters={'Energy': D.Decimal, 'Counts': D.Decimal}, engine='c', skipinitialspace= True, float_precision='round_trip')


sum_mev['Energy'] = sum_mev['Energy'].astype(dtype='float128')
pu_mev['Energy'] = pu_mev['Energy'].astype(dtype='float128')
am_mev['Energy'] = am_mev['Energy'].astype(dtype='float128')
cm_mev['Energy'] = cm_mev['Energy'].astype(dtype='float128')
cm_mev['Energy'] = cm_mev['Energy'].astype(dtype='float128')
sum_mev['Energy'] = sum_mev['Energy'].round(3)
pu_mev['Energy'] = pu_mev['Energy'].round(3)
am_mev['Energy'] = am_mev['Energy'].round(3)
cm_mev['Energy'] = cm_mev['Energy'].round(3)
cm_mev['Energy'] = cm_mev['Energy'].round(3)


sum_mev['Counts'] = sum_mev['Counts'].astype(dtype='int')
pu_mev['Counts'] = pu_mev['Counts'].astype(dtype='int')
am_mev['Counts'] = am_mev['Counts'].astype(dtype='int')
cm_mev['Counts'] = cm_mev['Counts'].astype(dtype='int')
gd_mev['Counts'] = gd_mev['Counts'].astype(dtype='int')

h2.set_xlim(min(sum_mev['Energy'] ),max(sum_mev['Energy'] ))

sum_mev['Counts'] = sum_mev['Counts'].add(gd_mev['Counts'], fill_value=0)
mev_edges = np.insert(sum_mev['Energy'].values, 0,0)
(entries,edges,patches) = h2.hist(mev_edges[:-1], alpha=1, histtype='step',color="black", bins=mev_edges, weights=sum_mev['Counts'].values,log=0, linewidth="0.8", label="sum of ${}^{148}$Gd, ${}^{239}$Pu, ${}^{241}$Am & ${}^{244}$Cm decays") #,hatch='\\')

# add missing energy bins to single peak data sets
pd.merge(pu_mev, sum_mev, how='outer', on="Energy",sort='False')['Counts_x']
pu_counts=pd.merge(pu_mev, sum_mev, how='outer', on="Energy",sort='False')['Counts_x'].fillna(0).values
am_counts=pd.merge(am_mev, sum_mev, how='outer', on="Energy",sort='False')['Counts_x'].fillna(0).values
cm_counts=pd.merge(cm_mev, sum_mev, how='outer', on="Energy",sort='False')['Counts_x'].fillna(0).values

# draw Pu, Am and Cm
h2.hist(mev_edges[:-1], alpha=1, histtype='step',color="red", bins=mev_edges, weights=pu_counts,log=0, linewidth="0.8", label="simulation of ${}^{239}$Pu decays" ) #,hatch='\\')
h2.hist(mev_edges[:-1], alpha=1, histtype='step',color="green", bins=mev_edges, weights=am_counts,log=0, linewidth="0.8", label="simulation of ${}^{241}$Am decays") #,hatch='\\')
h2.hist(mev_edges[:-1], alpha=1, histtype='step',color="blue", bins=mev_edges, weights=cm_counts,log=0, linewidth="0.8", label="simulation of ${}^{244}$Cm decays") #,hatch='\\')
h2.axvline(ref[1]/1000, linewidth=1, linestyle=":", color="grey", ymin=-0.07,clip_on=False) # in_layout=True)
h2.axvline(ref[2]/1000,linewidth=1, linestyle=":", color="grey", ymin=-0.07,clip_on=False)
h2.axvline(ref[3]/1000,linewidth=1, linestyle=":", color="grey", ymin=-0.03,clip_on=False)
h2.axvline(ref[4]/1000,linewidth=1, linestyle=":", color="grey", ymin=-0.07,clip_on=False)

h2.set_xticks(ticks_minor, minor=True)

x_bounds = h2.get_xlim()
h2.annotate(s='${}^{148}$Gd', xy =(((ref[1]/1000-x_bounds[0])/(x_bounds[1]-x_bounds[0])),-0.12), xycoords='axes fraction', verticalalignment='right', horizontalalignment='center', fontsize = 12)
h2.annotate(s='${}^{239}$Pu', xy =(((ref[2]/1000-x_bounds[0])/(x_bounds[1]-x_bounds[0])-0.005),-0.12), xycoords='axes fraction', verticalalignment='right', horizontalalignment='center', fontsize = 12)
h2.annotate(s='${}^{241}$Am', xy =(((ref[3]/1000-x_bounds[0])/(x_bounds[1]-x_bounds[0]))+0.007,-0.06), xycoords='axes fraction', verticalalignment='right', horizontalalignment='center', fontsize = 12)
h2.annotate(s='${}^{244}$Cm', xy =(((ref[4]/1000-x_bounds[0])/(x_bounds[1]-x_bounds[0]))+0.005,-0.12), xycoords='axes fraction', verticalalignment='right', horizontalalignment='center', fontsize = 12)
h2.legend()

# get bin width from simulation dataset
bin_width_kev = (mev_edges[1]-mev_edges[0])*1000

h2.set_xlabel('Energy [MeV]', fontsize = 14)
h2.set_ylabel('Counts/' + str(int(bin_width_kev)) + ' keV' , fontsize = 14)
h2.yaxis.set_label_coords(-0.12, 0.80)

plt.tight_layout(pad=0.5)

print("mumber of bins: ", mev_edges[:-1].size, ", bin size in kev: ",bin_width_kev)
