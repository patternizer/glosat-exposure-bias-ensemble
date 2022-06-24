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

tstart, tend = 1781, 2022

#------------------------------------------------------------------------------
# LOAD: temperature .pkl file
#------------------------------------------------------------------------------

df_temp = pd.read_pickle( df_temp_file, compression='bz2' )

#------------------------------------------------------------------------------
# LOAD: EBC temperature .pkl file
#------------------------------------------------------------------------------

df_temp_ebc = pd.read_pickle( df_temp_ebc_file, compression='bz2' )

#------------------------------------------------------------------------------
# LOAD: exposure bias correction dataframe
#------------------------------------------------------------------------------

df_ebc = pd.read_pickle( df_ebc_file, compression='bz2' )

#------------------------------------------------------------------------------
# TRIM: to GloSAT year range [1781,2022]
#------------------------------------------------------------------------------

df_temp = df_temp[ ( df_temp.year >= tstart ) & ( df_temp.year <= tend ) ]
df_temp_ebc = df_temp_ebc[ ( df_temp_ebc.year >= tstart ) & ( df_temp_ebc.year <= tend ) ]
df_ebc = df_ebc[ ( df_ebc.year >= tstart ) & ( df_ebc.year <= tend ) ]

#------------------------------------------------------------------------------
# PLOT: global mean EBC
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
ax[0].set_title( 'NH mean EBC', fontsize=fontsize)
ax[0].set_ylim(-0.15,0.1)
for i in range(12):    
    ax[1].plot( df_ebc[ (df_ebc.stationlat<0) ].groupby('year').mean().iloc[:,i], label='Month '+str(i+1))
ax[1].plot( df_ebc[ (df_ebc.stationlat<0) ].groupby('year').mean().iloc[:,0:12].mean(axis=1), ls='-', lw=3, color='black', label='Annual')
ax[1].tick_params(labelsize=fontsize)    
ax[1].legend(loc='lower right', ncol=4, fontsize=12)
ax[1].set_xlabel(xstr, fontsize=fontsize)
ax[1].set_ylabel(ystr, fontsize=fontsize)
ax[1].set_title( 'SH mean EBC', fontsize=fontsize)
ax[1].set_ylim(-0.15,0.1)

plt.savefig(figstr, dpi=300, bbox_inches='tight')
plt.close(fig)
            
#------------------------------------------------------------------------------
print('** END')



    
