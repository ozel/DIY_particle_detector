<img align="right" src="https://github.com/ozel/DIY_particle_detector/raw/master/images/Alpha-spectrometer_with_ceramics_in_chocolate_box.jpeg" width="400">

*Corresponding scientific article:* [![DOI](https://img.shields.io/badge/doi-10.3390/s19194264-blue.svg?style=flat&labelColor=grey)](https://doi.org/10.3390/s19194264)

*Repository archive on Zenodo:* [![DOI](https://img.shields.io/badge/doi-10.5281/zenodo.3361755-blue.svg?style=flat&labelColor=grey)](https://doi.org/10.5281/zenodo.3361755)


# DIY Particle Detector

**Short summary video on twitter**<br>
:point_right: https://twitter.com/CERN/status/1260600298206302210

A mobile low-cost spectrometer for measuring ionising radiation like alpha particles and electrons (energy range: 33 keV to 8 MeV).   
It's an experimental educational tool and citizen science device made for exploring natural and synthetic sources of radioactivity such as stones, airborne radon, potassium-rich salt or food and every-day objects (Uranium glass, ceramics, old Radium watches etc.).

*The main project documentation has been moved to the **[Wiki](https://github.com/ozel/DIY_particle_detector/wiki)**.*     
A summary of the main aspects can be found below.    
The hardware design is licenced using the [CERN Open Hardware License](https://github.com/ozel/DIY_particle_detector/blob/master/hardware/V1.2/CERN_OPEN_HARDWARE_LICENSE_OHL_v_1_2.txt) and the open source software is provided under the terms of the [BSD licence](https://github.com/ozel/DIY_particle_detector/blob/master/LICENSE).

Overview:
* [How does it work?](#how-does-it-work)
* [Hardware](#hardware)
    * [Two variants](#detector-variants): Electron-Detector (easier, lower costs) and Alpha-Spectrometer (more advanced)
    * [General requirements](#general-requirements)
    * [Detector signals](#detector-signals)
* [Software](#software) for recording and analysing measurements
* [Reference measurements and plots](#reference-measurements-and-plots)
* [Workshops](#workshops) with high-school students, teachers and makers

*More info in the **[Wiki](https://github.com/ozel/DIY_particle_detector/wiki)**.*     

## How does it work?
Tiny amounts of electrical charge are generated in repurposed photodiodes by impinging particles. The charges form currents which are amplified and converted into voltage pulses that are compatible with audio/microphone signal inputs.
The size of the pulse is proportional to the energy deposited by the ionising radiation. A reference calibration with sources of known energy spectra is provided.

<br><br><img align="right" src="https://github.com/ozel/DIY_particle_detector/raw/master/images/pulse_rain.png" width="300">

A superposition of several recorded pulse waveforms from electrons of beta decays (KCl salt sample, more info below) is shown on the right. This is the raw analog ouput signal of the detector.

Black lines in the upper area represent electronic noise, detected signal pulses from the natural radioactivity of potassium (isotope K-40) are highlighted in red.

<br>

<br>

<br>

<img align="right" src="https://github.com/ozel/DIY_particle_detector/raw/master/images/Alpha_spectrum_Majolika_ceramic.png" width="300">

The energy spectrum on the right - derived from the size of signal pulses - was taken from an old ceramics pendant of the Majolika manufacture (Karlsruhe/Germany) - without vacuum pump, in normal ambient air! 

The characteristic alpha energies of the uranium isotopes are about 1 MeV lower than the actual values due to internal absorption caused by the transparent surface coating on top of the orange uranium-based glaze. More detais on the energy calibration below and in the [paper](https://doi.org/10.3390/s19194264).

<br>

<br>

## Hardware

<img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.1/documentation/DIY_Particle_Detector_in_candy-tin-box.jpg" height="350"><img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.1/documentation/DIY_Particle_Detector_in_cast-aluminium-case.jpg" height="350">
<img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.2/documentation/Alpha_spectrometer_in_candy_box_open.jpg" height="313"><img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.2/documentation/Alpha_spectrometer_in_candy_box_closed.jpg" height="313">

More photos of finished builds from users around the world can be found in the [picture gallery](https://github.com/ozel/DIY_particle_detector/wiki/Gallery).     
The open hardware design in this repository is relased under the terms of the CERN Open Hardware Licence V1.2.
Usage guidelines and legal requirements for users of his license can be found [here](https://ohwr.org/project/cernohl/wikis/Documents/CERN-OHL-version-1.2).
### Detector Variants
The same circuit board is used with two partially different sets of components in two assembly variants.
For electronic beginners, starting with the electron-detector version is *highly recommended* over the alpha-spectrometer.

* ***Alpha-spectrometer*** measuring energies of alpha particles and electrons using one BPX61 diode.<br/>
  <img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.2/documentation/3D_top_alpha.png" height="200"><img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.2/documentation/3D_bottom_alpha.png" height="200"><br/>
  After the glass window of the diode is carefully broken-up and removed, it can sense alpha particles (see close-up pictures in the [wiki](https://github.com/ozel/DIY_particle_detector/wiki/Diodes#preparation-of-the-bpx61-diode-for-alpha-spectroscopy). 
  The circuit works most precise with only one BPX61 diode (lowest electronic noise) and was specificaly tuned for this scenario.
  * [get alpha-spectrometer parts & circuit board via kitspace](https://kitspace.org/boards/github.com/ozel/diy_particle_detector/diy%20alpha%20spectrometer/)
  * [short parts overview & assembly guide for the alpha-spectrometer](https://github.com/ozel/DIY_particle_detector/blob/master/hardware/V1.2/documentation/DIY%20detector%20-%20parts%20overview%20v1-2%20alphaspectrometer%20version.pdf)
  * [detailed assembly instructions and list of required tools](https://github.com/ozel/DIY_particle_detector/wiki/Assembly-Instructions)
  * [scientific article incl. reference energy calibration with alpha sources](https://doi.org/10.3390/s19194264)



* ***Electron/beta radiation detector*** measuring mostly electrons (plus few gamma photons) with four very low-cost BPW34F or BPW34FA diodes (<1 EUR each).<br/>
  <img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.2/documentation/3D_top_electron.png" height="200"><img src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.2/documentation/3D_bottom_electron.png" height="200"><br/>
  This variant is not able to detect alpha particles but is  easier to operate (less sensitive to visible light and electromagnetic interference, see section on general requirements below). It is also more sensitive towards sources of low intensity (low rate of radioactive decays) since it has four times the sensor volume compared to using only one diode as sensor. This version is ideal for beginners, in total only 8 components are different compared to the alpha-spectrometer variant above. This variant is similar to the previous circuit version 1.1.
  * [get electron-detector parts & circuit board via kitspace](https://kitspace.org/boards/github.com/ozel/diy_particle_detector/diy%20electron%20detector/)
  * [short parts overview & assembly guide for the electron-detector](https://github.com/ozel/DIY_particle_detector/blob/master/hardware/V1.2/documentation/DIY%20detector%20-%20parts%20overview%20v1-2%20electron%20version.pdf) 
  * [detailed assembly instructions and list of required tools](https://github.com/ozel/DIY_particle_detector/wiki/Assembly-Instructions)


Both kinds of diodes, the BPW34 series in various plastic cases and the BPX61 with metal casing, have the same sensitive area (~7 mm^2). The physics of these sensors when used with ionizing radiation is explained in detail in the [article corresponding to this repository](https://doi.org/10.3390/s19194264). The section about figure 1 discusses why their efficiency for detecting gamma photons is quite low in general.  

<img align="left" src="https://github.com/ozel/DIY_particle_detector/raw/master/hardware/V1.2/documentation/BXP61_mircoscope.png" height="300">

Mircoscope image of the Osram BPX61 diode on the left, the green scale indicates 2 mm. The sensitive area of the silicon chip is 2.65 x 2.65 mm^2. A bond wire from the anode pin on the right connects the top of the silicon chip (this side is also marked with a notch in the metal case, lower right corner). For detecting alpha particles, the glass window of this diode must be removed.    
Further instructions in the [wiki](https://github.com/ozel/DIY_particle_detector/wiki/Diodes).

<br>

<br><br>

<br><br>

### General Requirements

* An absolutely light-tight and electromagnetically shielding metal case is mandatory. Either a commercial one made of die casted aluminium (thick metal provides better immunity towards vibrations and prevents "microphonic effects") or an upcycled tin box for candies. Detailed recommendations in the [wiki](https://github.com/ozel/DIY_particle_detector/wiki/Enclosures).
* 9 V [battery](https://github.com/ozel/DIY_particle_detector/wiki/Batteries). NIMH-type accumulators with a nominal value of 9.6 V work best (mains-connected power supplies would introduce too much noise, always use batteries if building the detector for the first time!)
* Signal output is in the range of +/- 0.1 V and compatible with an audio/microphone input such as a [headset connector](https://github.com/ozel/DIY_particle_detector/wiki/Cables#connection-with-a-headset-socket) of a mobile phone or laptop (or an oscilloscope if available)
* The alpha-spectrometer should be operated using a low-cost USB soundcard for best results, see the [wiki](https://github.com/ozel/DIY_particle_detector/wiki/Soundcards).
* The connection cable should be shielded and not too long, recommendations in the [wiki](https://github.com/ozel/DIY_particle_detector/wiki/Cables). 


### Detector Signals
Typical signals from the electron-detector (left/top) and alpha-spectrometer (right/bottom) on an oscilloscope:
<img width=400 src=https://raw.githubusercontent.com/ozel/DIY_particle_detector/master/images/oscilloscope_pulse_electron-detector.png> <img width=400 src=https://raw.githubusercontent.com/ozel/DIY_particle_detector/master/images/oscilloscope_pulse_alpha-spectro.png>     
More details in the [wiki](https://github.com/ozel/DIY_particle_detector/wiki/Oscilloscope-Measurements).

## Software
The open source software in this repository is provided under the terms of the BSD Licence.

It consists of two parts (links to the wiki):
* [Recording, real-time display and counting of particle pulses](https://github.com/ozel/DIY_particle_detector/wiki/Software#signal-display--pulse-counting)     
  Different softwares for desktop computers as well as mobile devices are decsribed in the wiki.     
  Most universal is a [web browser application](https://ozel.github.io/DIY_particle_detector/data_recording_software/webGui/) based on the Web Audio API available in modern browsers (recent Chrome and Firefox versions work best):     
  <img src="https://github.com/ozel/DIY_particle_detector/raw/master/images/webGui_screenshot.png" alt="A single pulse recorded by the web browser GUI." width="600">      
  This acts essentially as a software oscilloscope with trigger functionality (red line = trigger level) reading small detector pulses directly from the microphone input or headset socket of a computer or mobile device.

* [Data analysis of alpha-spectrometer measurements](https://github.com/ozel/DIY_particle_detector/wiki/Software#energy-spectra-from-alpha-particles), providing calibrated energy spectra and time series histograms

## Reference measurements and plots

Several reference measurements have been taken and stored in [data_analysis_and_reference_measurements/diode_detector/data](https://github.com/ozel/DIY_particle_detector/tree/master/data_analysis_and_reference_measurements/diode_detector/data). All have been recorded using the very low-cost [CM108 USB soundcard](https://github.com/ozel/DIY_particle_detector/wiki/Soundcards), sampling the input signal @ 48 kHz and 16-bit resolution.     
*If this whole respository is cloned using git, the [git LFS](https://help.github.com/en/articles/duplicating-a-repository#mirroring-a-repository-that-contains-git-large-file-storage-objects) extension must be used to get as well the large data files (~ 1 GB).*
Alternatively, the data files can be downloaded from this [Zenodo data archive](https://doi.org/10.5281/zenodo.3361764).

Overview on reference measurements:

* A mixed alpha source featuring Gd-148, Pu-239, Am-241 & Cm-244 with a combined alpha energy spectrum of 3 to 6 MeV
* 10 g of KCl (potassium chlorid) salt (an alternative to NaCl table salt) as an example for detection of electrons from beta-decays (from naturally occuring K-40)
* a small columbite stone (containing trace amounts of uranium ore), a combined source of electrons and alphas (and gamma photons which do not interact enough within the thin diode detector to be relevant)
* a watch hand from an old watch that was painted with luminescent radium paint. Featuring Ra-226 and all it's radioactive progeny isotopes

## Workshops

These DIY particle detectors have been built by high school students (age 16 - 18), teachers, makers, and citizen science enthusiasts (age ~20 - 60) during several workshops.
After a little introduction into the soldering of electronic components, the whole device can be built in less than two hours - including the modification of a candy tin box as its case.

* [S'Cool LAB Summer Camp 2017](https://indico.cern.ch/event/570855/timetable/) at CERN, [poster presentation](https://indico.cern.ch/event/570855/contributions/2616929/attachments/1504724/2344411/RG3_DIY_Detector.pdf)
* [Student Summer School of Barcelona Technoweek 2017](http://icc.ub.edu/congress/TechnoWeek2018/outreach_EN.php), [CERN news](https://home.cern/news/news/knowledge-sharing/summer-school-secondary-students-spain)
* [S'Cool LAB Summer Camp 2018](https://indico.cern.ch/event/726779/timetable/) at CERN, [poster presentation, page 3](https://indico.cern.ch/event/726779/contributions/2991390/attachments/1697186/2732121/pdfjoiner.pdf)
* [Gathering of Open Science Hardware 2018 in Shenzhen China](http://openhardware.science/gatherings/gosh-2018-2/), [workshop documentation](https://forum.openhardware.science/t/day-3-build-your-own-particle-detector-discover-natural-radioactivity/1468)

*Notes and announcements of future workshops can be found in the **[Wiki](https://github.com/ozel/DIY_particle_detector/wiki)**.*     

---

The [Pixel Detector](https://github.com/ozel/DIY_particle_detector/wiki/Pixel-Detectors) and [Diode Characterisation](https://github.com/ozel/DIY_particle_detector/wiki/Diode-Characterisation) sections have been moved to the [wiki](https://github.com/ozel/DIY_particle_detector/wiki) of this project. Both are related to the [scientific article](https://www.mdpi.com/1424-8220/19/19/4264/htm) and represent supplementary material.

