#------------------------------------------------------------------------------
# PROGRAM: plot-exposure-bias-correction.py
#------------------------------------------------------------------------------
# Version 0.1
# 24 June, 2022
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
# Maths libraries
import random
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

fontsize = 16

df_temp_file = 'DATA/df_temp_qc.pkl'
df_ebm_file = 'DATA/df_exposure_bias.pkl'
df_temp_ebc_file = 'OUT/df_temp_ebc.pkl'
df_ebc_file = 'OUT/df_ebc.pkl'
sftof_file = 'DATA/sftof.nc' # land/sea mask for zonal weighting

plot_random_stations = False

tstart, tend = 1781, 2022
ndraws = 10 # number of randomly selected EBC stations
    
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

#==============================================================================
# PLOTS
#==============================================================================

#------------------------------------------------------------------------------
# PLOT: hemispherical mean temperatures and EBC-corrected temperature
#------------------------------------------------------------------------------

figstr = 'hemispherical-mean-temp.png'
xstr = 'Year'
ystr = 'Temperature, °C'

fig, ax = plt.subplots(2,1,sharex=True,figsize=(15,10))          
ax[0].plot( df_temp[ (df_temp.stationlat>=0) ].groupby('year').mean().iloc[:,0:12].mean(axis=1), ls='-', lw=1, color='blue', label='CRUTEM')
ax[0].plot( df_temp_ebc[ (df_temp_ebc.stationlat>=0) ].groupby('year').mean().iloc[:,0:12].mean(axis=1), ls='-', lw=1, color='red', label='CRUTEM (EBC)')
ax[0].tick_params(labelsize=fontsize)    
ax[0].legend(loc='lower right', ncol=4, fontsize=12)
ax[0].set_xlabel(xstr, fontsize=fontsize)
ax[0].set_ylabel(ystr, fontsize=fontsize)
ax[0].set_title( 'NH mean temperature: unweighted', fontsize=fontsize)
ax[1].plot( df_temp[ (df_temp.stationlat<0) ].groupby('year').mean().iloc[:,0:12].mean(axis=1), ls='-', lw=1, color='blue', label='CRUTEM')
ax[1].plot( df_temp_ebc[ (df_temp_ebc.stationlat<0) ].groupby('year').mean().iloc[:,0:12].mean(axis=1), ls='-', lw=1, color='red', label='CRUTEM (EBC)')
ax[1].tick_params(labelsize=fontsize)    
ax[1].legend(loc='lower right', ncol=4, fontsize=12)
ax[1].set_xlabel(xstr, fontsize=fontsize)
ax[1].set_ylabel(ystr, fontsize=fontsize)
ax[1].set_title( 'SH mean temperature: unweighted', fontsize=fontsize)
plt.savefig(figstr, dpi=300, bbox_inches='tight')
plt.close(fig)

#------------------------------------------------------------------------------
# PLOT: hemispherical mean EBC
#------------------------------------------------------------------------------

figstr = 'hemispherical-mean-ebc.png'
xstr = 'Year'
ystr = 'Bias, °C'

fig, ax = plt.subplots(2,1,sharex=True,figsize=(15,10))          
for i in range(12):    
    ax[0].plot( df_ebc[ (df_ebc.stationlat>=0) ].groupby('year').mean().iloc[:,i], label='Month '+str(i+1))
ax[0].plot( df_ebc[ (df_ebc.stationlat>=0) ].groupby('year').mean().iloc[:,0:12].mean(axis=1), ls='-', lw=3, color='black', label='Annual')
ax[0].tick_params(labelsize=fontsize)    
ax[0].legend(loc='lower right', ncol=4, fontsize=12)
ax[0].set_xlabel(xstr, fontsize=fontsize)
ax[0].set_ylabel(ystr, fontsize=fontsize)
ax[0].set_title( 'NH mean EBC: unweighted', fontsize=fontsize)
ax[0].set_ylim(-0.1,0.1)
for i in range(12):    
    ax[1].plot( df_ebc[ (df_ebc.stationlat<0) ].groupby('year').mean().iloc[:,i], label='Month '+str(i+1))
ax[1].plot( df_ebc[ (df_ebc.stationlat<0) ].groupby('year').mean().iloc[:,0:12].mean(axis=1), ls='-', lw=3, color='black', label='Annual')
ax[1].tick_params(labelsize=fontsize)    
ax[1].legend(loc='lower right', ncol=4, fontsize=12)
ax[1].set_xlabel(xstr, fontsize=fontsize)
ax[1].set_ylabel(ystr, fontsize=fontsize)
ax[1].set_title( 'SH mean EBC: unweighted', fontsize=fontsize)
ax[1].set_ylim(-0.1,0.1)
plt.savefig(figstr, dpi=300, bbox_inches='tight')
plt.close(fig)
            
#------------------------------------------------------------------------------
# PLOT: n randomly selected EBC stations
#------------------------------------------------------------------------------

if plot_random_stations == True:
    
    # SAMPLE: n random stationcodes
        
    stationcodes_ebm = df_ebm.stationcode.unique()
    nstations = stationcodes_ebm.shape[0]
    rng = np.random.default_rng(20220625) 
    allowed = list( np.arange( nstations ) )    
    draws = [ random.choice( allowed ) for i in range( ndraws) ]
    stationcodes_sample = [ stationcodes_ebm[draws[i]] for i in range(len(draws)) ]    
    
    for k in range(len(draws)):
            
        stationcode = stationcodes_sample[k]
        stationlat = np.round( df_temp[ df_temp['stationcode'] == stationcode ].stationlat.unique()[0], 1 )        
        stationlon = np.round( df_temp[ df_temp['stationcode'] == stationcode ].stationlon.unique()[0], 1 )        
        stationelevation = int( df_temp[ df_temp['stationcode'] == stationcode ].stationelevation.unique()[0] )       
        stationname = df_temp[ df_temp['stationcode'] == stationcode ].stationname.unique()[0]   
        stationcountry = df_temp[ df_temp['stationcode'] == stationcode ].stationcountry.unique()[0].upper()        
    
        da_temp = df_temp[ df_temp['stationcode'] == stationcode ].sort_values(by='year').reset_index(drop=True).dropna()        
        da_temp_ebc = df_temp_ebc[ df_temp_ebc['stationcode'] == stationcode ].sort_values(by='year').reset_index(drop=True).dropna()        
        df_yearly = pd.DataFrame({'year': np.arange( tstart, tend )}) 
        d1 = df_yearly.merge(da_temp, how='left', on='year')
        d2 = df_yearly.merge(da_temp_ebc, how='left', on='year')
    
        # EXTRACT: monthly timeseries
        
        ts_1 = np.array( d1.groupby('year').mean().iloc[:,0:12]).ravel().astype(float)
        ts_2 = np.array( d2.groupby('year').mean().iloc[:,0:12]).ravel().astype(float)
        
        # SET: monthly and seasonal time vectors
        
        t = pd.date_range(start=str(d1['year'].iloc[0]), periods=len(ts_1), freq='MS')     
    
        figstr = stationcode + '-' + 'compare_temp.png'       
        titlestr = stationcode + ': ' + stationname + ', ' + stationcountry + ' (' + str(stationlat) + ',' + str(stationlon) + ') ' + str(stationelevation) + '[m] a.s.l.'          
        
        fig, ax = plt.subplots(2,1,sharex=True,figsize=(15,10))
        ax[0].plot(t, ts_1, marker='o', ls='-', lw=1, color='blue', alpha=0.2, label='CRUTEM')                                        
        ax[0].plot(t, ts_2, marker='o', ls='-', lw=1, color='red', alpha=0.2, label='CRUTEM (EBC)')                                        
        ax[0].axhline( y=0, ls='-', lw=1, color='black', alpha=0.2)                    
        ax[0].set_xlim(t[0],t[-1])
        ax[0].set_xlabel('Year', fontsize=fontsize)
        ax[0].set_ylabel(r'Temperature, $^{\circ}$C', fontsize=fontsize)
        ax[0].set_title( titlestr, color='black', fontsize=fontsize)           
        ax[0].tick_params(labelsize=fontsize)  
        ax[0].legend(loc='upper left', ncol=1, markerscale=1, facecolor='lightgrey', framealpha=0.5, fontsize=fontsize)   
    
        ax[1].plot(t, ( ts_2 - ts_1 ), marker='.', ls='-', lw=1, color='teal', alpha=1)                                        
        ax[1].axhline( y=0, ls='-', lw=1, color='black', alpha=0.2)                    
        ax[1].set_xlim(t[0],t[-1])
        ax[1].set_xlabel('Year', fontsize=fontsize)
        ax[1].set_ylabel(r'Exposure bias correction, $^{\circ}$C', fontsize=fontsize)
        ax[1].tick_params(labelsize=fontsize)  
    
        plt.savefig(figstr, dpi=300)
        plt.close('all')       

#------------------------------------------------------------------------------
print('** END')



    
