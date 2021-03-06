#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 12:17:56 2020

@author: matthew
"""
"""
This script is used to detect marine heat waves using the daily thresheld calculated in MHW_threshold_netcdf_clean.py. 
The script identifies spatial extend of MHW from a 2D grid of sst values. The script calculates the individual
events, the length of MHW event and the category of the event. These parameters are stored in a single netcdf file.
 
INPUT:
    - the path to the folders containing the sst data (netcdf files) 
    - the path to the folder containing threshold netcdf file created from MHW_threshold_netcdf_clean.py
    - thhe name of the netcdf file created from MHW_threshold_netcdf_clean.py
    - the path to folder where the output netcdf file should be stored
    - the name of the netcdf file to be stored 
    - the variable name of sst data (! as written in netcdf file e.g. anaylsed sst !)
    - the variable name of longitude and latitiude in the sst data (! as written in netcdf file e.g lat/lon !) 

OUTPUT:
    - A nedcdf file containing the detected MHW, the length of MHW events and the caterory of the MHW events.
    for the given domain and time period. The file contains the marine_heat_waves, marine_heat_wave_length,
    marine_heat_wave_category, longitude, latitude and time (climatological days)
    
REQUIRMENTS:
    - The sst data provide must be the same resolution used for MHW_threshold_netcdf_clean.py. 

The inputs to the script should be changed where necessary is the section below called USER INPUTS
"""

# %% # USER INPUTS

#Adding the path to the model data 
path_to_data  =  '/media/matthew/Elements/SST_data/Low_res_SST/NCEI_OISST_AVHRR_ND/'

#Adding path to save the threshold netcdf file 
thres_path = '/home/matthew/Documents/Python_scripts/Marine_heat_waves/Github_test/'
thres_fname = "MHW_threshold" +".nc"

#Adding path to save the satelite netcdf file 
save_path = '/home/matthew/Documents/Python_scripts/Marine_heat_waves/Github_test/'
save_fname = "MHW_final_2000_2018" +".nc"

# Domain of analysis
west = 9     
east = 48    
north = -11  
south = -40  

#The start and end date of the time period
#start_time = 
#end_time = 

#The variables to be analysed as written in netcdf files 
satelite_variable= "analysed_sst"

#The longitude and latitude dimesions of the observations of named in netcdf file
lat = 'lat'
lon = 'lon'

#The Kelvin offset
kelvin_offset = 273.15

# %% Import all the packages 

import numpy as np
from natsort import natsorted
#import pylab as plt
import xarray as xr
from glob import glob
#import matplotlib.dates as mdates
#from mpl_toolkits.basemap import Basemap 
from datetime import datetime
import itertools
#import pyproj    
#import shapely.ops as ops
#from shapely.geometry.polygon import Polygon
#from functools import partial


# %% Defining function to define threshold

def postive_int(tmp_array):
    array=np.zeros(np.shape(tmp_array))
    count = 0
    for num in tmp_array:
        if num < 0:
            num = 0
        elif np.isnan(num):
            num = np.nan 
        else:
            num = 1
        array[count]=num
        count = count+1 

    return array

def cat_mhw(x,catergory_thres):
    if all(np.isnan(x)):
        mh_cat = x[:]
        return mh_cat

    else:
        mh_cat=np.zeros(np.shape(x))
        for i in np.arange(len(x)):
            if catergory_thres[i]*2 > x[i] > 0: 
                mh_cat_tmp = 1

            elif catergory_thres[i]*3 > x[i] >= catergory_thres[i]*2:
                mh_cat_tmp = 2

            elif catergory_thres[i]*4 > x[i] >= catergory_thres[i]*3:
                mh_cat_tmp = 3

            elif x[i] >= catergory_thres[i]*4:
                mh_cat_tmp = 4
            else:
                mh_cat_tmp = 0 

            mh_cat[i]=mh_cat_tmp

        return mh_cat


def min_time_array(x):
    if all(np.isnan(x)):
        mh_event = x[:]
        mh_event_len = np.zeros(np.size(x[:]))
        return mh_event, mh_event_len
        #mh_event_len[:] = np.nan
    else:
        z = [(x[0], len(list(x[1]))) for x in itertools.groupby(x)]
        mh_array = np.zeros(np.shape(z))
        for i in np.arange(len(z)):
            if np.nanmax(z[i][0])==1 and np.nanmax(z[i][1])>=5:
                mh=10
                mh_length=z[i][1]
            elif np.nanmax(z[i][0])==0 and np.nanmax(z[i][1])<=2:
                mh=1
                mh_length=z[i][1]
            elif np.isnan(z[0][0]):
                mh = np.nan 
                mh_length=np.nan
            else:
                mh=0
                mh_length=z[i][1]           
            mh_array[i,0]=mh
            mh_array[i,1]=mh_length

        #reshape list to array length for mhw length 
        mh_reshape_len=np.repeat(999, np.nanmax(mh_array[:,1]*len(mh_array)),).reshape(len(mh_array),int(np.nanmax(mh_array[:,1])))
        for x in np.arange(len(mh_array)):
            mh_reshape_len_tmp = np.repeat(mh_array[x,1],int(mh_array[x,1]))
            mh_reshape_len[x,0:len(mh_reshape_len_tmp)] = mh_reshape_len_tmp

        n_rows=np.shape(mh_reshape_len)[0];n_cols = np.shape(mh_reshape_len)[1];
        mh_len_tmp = np.reshape(mh_reshape_len,(1,n_rows*n_cols))
        mh_event_len = mh_len_tmp[mh_len_tmp != 999]

        #reshape list to array length for mhw events 
        mh_reshape=np.repeat(999, np.nanmax(mh_array[:,1]*len(mh_array)),).reshape(len(mh_array),int(np.nanmax(mh_array[:,1])))
        for x in np.arange(len(mh_array)):
            mh_reshape_tmp = np.repeat(mh_array[x,0],int(mh_array[x,1]))
            mh_reshape[x,0:len(mh_reshape_tmp)] = mh_reshape_tmp

        n_rows=np.shape(mh_reshape)[0];n_cols = np.shape(mh_reshape)[1];
        mh_tmp = np.reshape(mh_reshape,(1,n_rows*n_cols))
        mh_event = mh_tmp[mh_tmp != 999]
    
        index = np.where(mh_event==1)          
        for y in index[0]:
            if y>=len(mh_event)-2:
                 continue
            if mh_event[y-1]==10:
                first=mh_event[y+1];second=mh_event[y+2]
                ref=first+second
                if ref>10:
                    mh_event[y] = 10

        return mh_event, mh_event_len
    


# %% Loading SST data 

#Loading threshold netcdf file 
ds_mhw = xr.open_dataset(thres_path + thres_fname)

# Loads the daily climatology from NC file 
clim = ds_mhw.clim.values
# Loads the daily threshold (90th percentile) from NC file 
thres = ds_mhw.thres.values

#Longitude and latitude
lon = ds_mhw.longitude.values
lat = ds_mhw.latitude.values

# Selecting files in folder
sstFiles = natsorted(glob(path_to_data + "*.nc"))

# Load SST files from previous 5 days 
list_of_arrays = []
for file in sstFiles[10346:13632]:
    ds = xr.open_dataset(file)
    ds = ds.sel(lat=slice(south, north), lon=slice(west, east))
    list_of_arrays.append(ds['analysed_sst'])

final_ds = xr.concat(list_of_arrays[0:len(list_of_arrays)],dim='time')

# loading lon and lat 
lon = ds.lon.values
lat = ds.lat.values

#Loading the time of combined dataset
time=final_ds.time

#Kelvin conversion 
sst = final_ds-kelvin_offset 


# %% detecting mhw defined by threshold calculated 
 
current_sst=sst[:,:,:]
loop_range = np.arange(np.shape(current_sst)[0])
threshold_sst = np.zeros(np.shape(current_sst))
year_day_array = np.zeros(np.shape(current_sst)[0])
thres_array = np.zeros(np.shape(current_sst))
clim_array = np.zeros(np.shape(current_sst))
mhw_cat = np.zeros(np.shape(current_sst))
year_day = np.zeros(np.shape(sstFiles)[0])
year_day_str = []

loop_range = np.arange(np.shape(current_sst)[0])

for i in loop_range:
    sst_tmp = current_sst[i,:,:]
    day_str = str(sst_tmp.time.values);
    year_day_tmp=datetime.strptime(day_str[0:10],"%Y-%m-%d").strftime("%j")
    year_day_str.append(day_str[0:10])
    #account for zero start vs day of year offset
    year_day = int(year_day_tmp)-1
    year_day_array[i] = year_day
    threshold_sst[i,:,:] = sst_tmp-thres[int(year_day),:,:]
    thres_array[i,:,:] = thres[int(year_day),:,:]
    clim_array[i,:,:] = clim[int(year_day),:,:]
    mhw_cat[i,:,:] = thres[int(year_day),:,:]-clim[int(year_day),:,:]
    
row_length = np.shape(threshold_sst[0,:,:])[0];rows=np.arange(start=1, stop=row_length, step=1);
column_length = np.shape(threshold_sst[0,:,:])[1];columns=np.arange(start=1, stop=column_length, step=1);

mh=np.zeros(np.shape(current_sst))
mh_length_events=np.zeros(np.shape(current_sst))
mh_cat=np.zeros(np.shape(current_sst))


for x in rows:
    for y in columns:
        tmp_array=threshold_sst[:,x,y]
        threshold_array=postive_int(tmp_array)
        mh_test=min_time_array(threshold_array)
        mh[:,x,y]=mh_test[0]
        mh_length_events[:,x,y]=mh_test[1]

mh_length_events[mh<10]=0

#Defining the category of mhw events 
mhw_cat[mh<10]=np.nan

row_length = np.shape(threshold_sst[0,:,:])[0];rows=np.arange(start=1, stop=row_length, step=1);
column_length = np.shape(threshold_sst[0,:,:])[1];columns=np.arange(start=1, stop=column_length, step=1);

mh_cat=np.zeros(np.shape(current_sst))

for x in rows:
    for y in columns:
        tmp_array=threshold_sst[:,x,y]
        tmp_array_cat=mhw_cat[:,x,y]
        mh_cat[:,x,y]=cat_mhw(tmp_array,tmp_array_cat)
        
# %% Writing data to netcdf

threshold_values = thres_array[:,:,:]
climatology_values = clim_array[:,:,:]
marine_heat_waves = mh[:,:,:]
marine_heat_wave_length = mh_length_events[:,:,:]
marine_heat_wave_category = mh_cat[:,:,:]


ds = xr.Dataset(
    {
            "marine_heat_waves": (["time", "latitude","longitude"], marine_heat_waves),
            "marine_heat_wave_length": (["time", "latitude","longitude"], marine_heat_wave_length),
            "marine_heat_wave_category": (["time", "latitude","longitude"], marine_heat_wave_category),
            #"threshold_values": (["time", "latitude","longitude"], threshold_values),
            #"climatology_values": (["time", "latitude","longitude"], climatology_values),

            
                            
            },
         coords={
             
             "time": time,
             "latitude": (["latitude"], lat),
             "longitude": (["longitude"], lon),
             
             },
         )
    
#ds.climatology_values.attrs["comment"] = "The daily climatology calculated on a 31 day moving average"
#ds.climatology_values.attrs["units"] =   "^oC"
    
#ds.threshold_values.attrs["comment"] = "The daily climatology calculated on a 31 day moving average"
#ds.threshold_values.attrs["units"] =   "^oC"
    
encoding={'marine_heat_waves':{"dtype": 'int16'},'marine_heat_wave_length':{"dtype": 'int16'},'marine_heat_wave_category':{"dtype": 'int16'}}

#Saving dataset to saving path and filename     
ds.to_netcdf(save_path+save_fname,encoding=encoding)

