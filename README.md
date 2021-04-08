# Marine-heat-waves
This repository contains the scripts and functions needed to produce the real-time marine heat wave tracking displayed on the OCIMS test platform.

AUTHOR AND POINT OF CONTACT
Matthew Carr matt@saeon.ac.za

SCRIPTS
MHW_threshold_nedcdf_clean.py, MHW_tracker_clean.py

DEPENDANCIES
- math
- numpy
- natsort
- xarray
- pylab
- glob
- datetime
- itertools

DESCRIPTION
The two scripts MHW_threshold_nedcdf_clean.py and MHW_tracker_clean.py are designed to be run in succession in 
order to identify the spatial extent marine heat waves (MHW). MHW are identified following the parameters 
described by Hobday et al. 2016 (https://doi.org/10.1016/j.pocean.2015.12.014). This tool is designed to 
identify the spatial extended of MHWs for the OCIMS website. The tool also provides the length of MHW events and 
the caterory of the MHW events. Research users are encoraged to use the MHW detection code provided by 
https://github.com/ecjoliver/marineHeatWaves.

ADDITIONAL INFORMATION 
Each script has a header describing the inputs required, user requirements and outputs produced. The document 
Marine_heat_wave_report.docx provides a show summary of the performance of the scripts relative to MHW detection 
code provided by https://github.com/ecjoliver/marineHeatWaves.
