#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for plotting absorption probabilities of photons in thin layers of silicon
for different thickness values.

@author: Oliver Keller
@date: February 2019
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

x, mu, mu_en = np.loadtxt('../data/Absorption Coefficients for Silicon.csv', delimiter=';', unpack=True, skiprows=1)

# mu/density and mu_en/density in cm^2/g

# mu_en: from https://www.sciencedirect.com/science/article/pii/S0969806X14004526
# The mass-energy absorption coefficients, (μen/ρ), on the other hand, is a 
# measure of the average fractional amount of charged particles as a result of 
# these interactions. It is a more detailed version of the energy-deposition 
# quantity which takes into account the fraction of the kinetic energy that is 
# subsequently lost in radiative energy-loss processes (Bremsstrahlung) as the 
# charged particles slow to rest in the absorbing medium. The net charged 
# particles kinetic energy, in turn, a more or less valid approximation to the 
# amount of photon energy made available for the production of chemical, 
# biological and other effects associated with exposure to ionizing radiation. 
# Therefore, (μen/ρ) has an essential role in estimating the absorbed dose in 
# medical and health physics.

Si_density =  2.321 #g/cm^3

x = x[ np.where( x <= 20 ) ]
mu_en = mu_en[:len(x)]
mu = mu[:len(x)]


fig, ax = plt.subplots()
ax.axis([0.001, 20, 0.001, 1.1])
ax.loglog(x,1-np.exp(-1*mu*Si_density*0.3), label=r'300 $\mu m$ (general att.)')
ax.loglog(x,1-np.exp(-1*mu_en*Si_density*0.3), label=r'300 $\mu m$ (energy att.)')
ax.loglog(x,1-np.exp(-1*mu_en*Si_density*0.1), label=r'100 $\mu m$ (energy  att.)')
ax.loglog(x,1-np.exp(-1*mu_en*Si_density*0.05), label=r'50 $\mu m$ (energy  att.)')

ax.xaxis.set_ticks_position('both')
ax.yaxis.set_ticks_position('both')
ax.tick_params( axis='both', labelsize=12)

for axis in [ax.xaxis, ax.yaxis]:
    formatter = FuncFormatter(lambda y, _: '{:.16g}'.format(y))
    axis.set_major_formatter(formatter)

plt.xlabel('Photon energy [MeV]', fontsize=13)
plt.ylabel('Detection probability in silicon', fontsize=13)
plt.legend(fontsize=12)
fig.tight_layout(pad=0.3)
plt.show()