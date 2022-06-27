#------------------------------------------------------------------------------
# PROGRAM: plot-exposure-bias-correction-area-weighted.py
#------------------------------------------------------------------------------
# Version 0.1
# 26 June, 2022
# Michael Taylor
# https://patternizer.github.io
# michael DOT a DOT taylor AT uea DOT ac DOT uk
# patternizer AT gmail DOT com
#------------------------------------------------------------------------------ 

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------
# Dataframe libraries:
import numpy as np
import pandas as pd
import pickle
import xarray as xr
import netCDF4
# Plotting libraries:
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

fontsize = 16

df_temp_file = 'DATA/df_temp_qc.pkl'
df_ebm_file = 'DATA/df_exposure_bias.pkl'
df_temp_ebc_file = 'OUT/df_temp_ebc.pkl'
df_ebc_file = 'OUT/df_ebc.pkl'
sftof_file = 'DATA/sftof.nc' # CMPI6 climatological land/sea mask for zonal land weighting

tstart, tend = 1781, 2022
nsmooth = 60 # months

latstep = 5
    
#------------------------------------------------------------------------------
# LOAD: dataframes
#------------------------------------------------------------------------------

# LOAD: temperature .pkl file
df_temp = pd.read_pickle( df_temp_file, compression='bz2' )

# LOAD: EBC temperature .pkl file
df_temp_ebc = pd.read_pickle( df_temp_ebc_file, compression='bz2' )

# LOAD: exposure bias correction dataframe
df_ebc = pd.read_pickle( df_ebc_file, compression='bz2' )

# LOAD: exposure bias model
df_ebm = pd.read_pickle( df_ebm_file, compression='bz2' )

#------------------------------------------------------------------------------
# TRIM: to GloSAT year range [1781,2022]
#------------------------------------------------------------------------------

df_temp = df_temp[ ( df_temp.year >= tstart ) & ( df_temp.year <= tend ) ]
df_temp_ebc = df_temp_ebc[ ( df_temp_ebc.year >= tstart ) & ( df_temp_ebc.year <= tend ) ]
df_ebc = df_ebc[ ( df_ebc.year >= tstart ) & ( df_ebc.year <= tend ) ]

#------------------------------------------------------------------------------
# COMPUTE: zonal aweighting
#------------------------------------------------------------------------------

# COMPUTE: Zonal latitude weights

zones = np.arange(-90,90+latstep,latstep) # zone boundaries
zones_per_degree = np.arange(-90,90+1,1) # zone boundaries oer degree
zone_bins = np.arange(-90+latstep/2, 90+latstep/2, latstep)
zone_bins_per_degree = np.arange(-90+1/2, 90+1/2, 1)

zonal_lat_weight_per_degree = []
for i in zone_bins_per_degree:
    zonal_lat_weight_per_degree.append( np.abs( np.cos( (i/180) * np.pi ) ) )
zonal_lat_weight_per_degree = np.array( zonal_lat_weight_per_degree )
zonal_lat_weight = []
for i in zone_bins:
    zonal_lat_weight.append( np.abs( np.cos( (i/180) * np.pi ) ) )
zonal_lat_weight = np.array( zonal_lat_weight )

# COMPUTE: Zonal land fraction weights

nc = netCDF4.Dataset( sftof_file, "r") # 1x1 degree
lats = nc.variables["lat"][:]
lons = nc.variables["lon"][:]
sftof = np.ma.filled(nc.variables["sftof"][:,:],0.0)
nc.close()
zonal_land_weight_per_degree = np.nanmean( sftof, axis=1 ) # per degree
zonal_land_weight_per_degree = zonal_land_weight_per_degree[::-1]/100
zonal_land_weight = []
zones_dict = dict( zip( zones_per_degree, np.arange(len(zonal_land_weight_per_degree)+1) ) )
for i in range(len(zones)-1):  
    weight_land = np.nanmean( zonal_land_weight_per_degree[ zones_dict[zones[i]] : zones_dict[zones[i]+latstep] ] )
    print(i, zones[i], weight_land)
    zonal_land_weight.append( weight_land ) 
zonal_land_weight = np.array( zonal_land_weight )

# COMBINE: weights

zonal_weight = zonal_lat_weight * zonal_land_weight
zonal_weight_per_degree = zonal_lat_weight_per_degree * zonal_land_weight_per_degree

# HEMISPHERICAL: weights

zonal_weight_hemisphere = np.array([ 0.49577966, 0.43426979]) # NH,SH computed from latstep = 90 run

#==============================================================================
# PLOTS
#==============================================================================

#------------------------------------------------------------------------------
# PLOT: zonal area-weights
#------------------------------------------------------------------------------

figstr = 'zonal-weighting' + '-' + str(latstep).zfill(2) + '.png'
titlestr = 'Zonal weights: ' + str(latstep) + r'$^{\circ}$ bins with land fraction weighting'
xstr = 'Weight'
ystr = 'Latitude, °N'

fig, ax = plt.subplots(figsize=(15,10))          
plt.plot( zonal_lat_weight_per_degree, zone_bins_per_degree,'^-', label='Cos(lat): ' + str(1) + r'$^{\circ}$' )
plt.plot( zonal_weight_per_degree, zone_bins_per_degree,'o-', label='Cos(lat)*sftof: ' + str(1) + r'$^{\circ}$' )
plt.plot( zonal_weight, zone_bins,'v-', label='Cos(lat)*sftof: ' + str(latstep) + r'$^{\circ}$' )
plt.tick_params(labelsize=fontsize)    
plt.legend(loc='lower right', ncol=1, fontsize=12)
plt.xlabel(xstr, fontsize=fontsize)
plt.ylabel(ystr, fontsize=fontsize)
plt.title( titlestr, fontsize=fontsize)
plt.savefig(figstr, dpi=300, bbox_inches='tight')
plt.close(fig)

#------------------------------------------------------------------------------
# PLOT: zonal area-weighted EBC
#------------------------------------------------------------------------------

figstr = 'zonal-mean-ebc' + '-' + str(latstep).zfill(2) + '.png'
titlestr = 'Zonal EBC: ' + str(latstep) + r'$^{\circ}$ bins with land fraction weighting'
xstr = 'Year'
ystr = 'Bias, °C'

fig, ax = plt.subplots(figsize=(15,10))          
for i in range(len(zones)-1):  
    zonal_mean = df_ebc[ ( df_ebc.stationlat > zones[i] ) & ( df_ebc.stationlat <= zones[i+1] ) ].groupby('year').mean().iloc[:,0:12].mean(axis=1) * zonal_weight[i]
    zonal_mean_rms = np.sqrt( np.nanmean( zonal_mean**2.0 ) ) 
    if zonal_mean_rms > 0:
        plt.plot( zonal_mean, label = '[' + str(zones[i]) + ',' + str(zones[i+1]) + ']' + r'$^{\circ}$ latitude')
plt.tick_params(labelsize=fontsize)    
plt.legend(loc='lower right', ncol=1, fontsize=12)
plt.xlabel(xstr, fontsize=fontsize)
plt.ylabel(ystr, fontsize=fontsize)
plt.title( titlestr, fontsize=fontsize)
plt.savefig(figstr, dpi=300, bbox_inches='tight')
plt.close(fig)
            
#------------------------------------------------------------------------------
print('** END')



    
