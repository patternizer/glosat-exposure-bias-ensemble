#------------------------------------------------------------------------------
# PROGRAM: exposure-bias-correction.py
#------------------------------------------------------------------------------
# Version 0.3
# 23 June, 2022
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

df_temp_ebc_file = 'df_temp_ebc.pkl'
df_ebc_file = 'df_ebc.pkl'

tstart, tend = 1781, 2022

#------------------------------------------------------------------------------
# LOAD: temperature .pkl file
#------------------------------------------------------------------------------

df_temp = pd.read_pickle( df_temp_file, compression='bz2' )

# TRIM: to GloSAT year range [1781,2022]

df_temp = df_temp[ ( df_temp.year >= tstart ) & ( df_temp.year <= tend ) ]
stationcodes_temp = df_temp.stationcode.unique()

#------------------------------------------------------------------------------
# LOAD: exposure bias model .pkl file
#------------------------------------------------------------------------------

df_ebm = pd.read_pickle( df_ebm_file, compression='bz2' )
df_ebm['bias'] = df_ebm['bias'].replace( np.nan, 0.0 )
stationcodes_ebm = df_ebm.stationcode.unique()

#------------------------------------------------------------------------------
# CONDITIONS: exposure bias = 0 if source_flag = 3 | exposurecorrected_flag = 1
#------------------------------------------------------------------------------

# SET: bias to zero on conditions

#df_ebm['bias'].loc[ df_ebm['source_flag'] > 2 ] = 0.0 # no correction if source_flag = 3
df_ebm['bias'].loc[ df_ebm['exposurecorrected_flag'] == 1 ] = 0.0 # no correction if already corrected
       
# SET: uncertainty to zero on conditions

#df_ebm['uncertainty'].loc[ df_ebm['source_flag'] > 2 ] = np.nan # fill value if source_flag = 3
df_ebm['uncertainty'].loc[ df_ebm['exposurecorrected_flag'] == 1 ] = np.nan # fill value if already corrected

#------------------------------------------------------------------------------
# INITIALISE: exposure bias correction dataframe
#------------------------------------------------------------------------------

df_ebc = df_temp.copy()
for i in range(1,13): df_ebc[str(i)] = 0.0

#------------------------------------------------------------------------------
# BIAS CORRECT: temperature dataframe with EBM values
#------------------------------------------------------------------------------

df_temp_ebc = df_temp.copy()

for k in range( len( stationcodes_temp ) ):
     
    if stationcodes_temp[k] in stationcodes_ebm:        
        
        da = df_ebm[ df_ebm.stationcode == stationcodes_temp[k] ].reset_index(drop=True)
        da.datetime = pd.date_range(start=str(da.datetime.loc[0].year), periods=len(da), freq='M')
        
        idx = df_temp_ebc[ df_temp_ebc.stationcode == stationcodes_temp[k] ].index.values

        # ADD: EBC to temperature data

        for i in range(1,13): 
            
            df_temp_ebc[str(i)][idx] = np.array( df_temp_ebc[str(i)][idx] ) + np.array( da[da.datetime.dt.month == i].bias.values )
            df_ebc[str(i)][idx] = np.array( df_ebc[str(i)][idx] ) + np.array( da[da.datetime.dt.month == i].bias.values )
 
#    else: continue
        
    if k % 10 == 0: print(k)

#------------------------------------------------------------------------------
# SAVE: exposure bias corrected temperature dataframe .pkl file
#------------------------------------------------------------------------------

df_temp_ebc.to_pickle( df_temp_ebc_file, compression='bz2' )

#------------------------------------------------------------------------------
# SAVE: exposure bias corrections dataframe .pkl file
#------------------------------------------------------------------------------

df_ebc.to_pickle( df_ebc_file, compression='bz2' )

#------------------------------------------------------------------------------
# PLOT: global mean EBC
#------------------------------------------------------------------------------

figstr = 'global-mean-ebc-monthly.png'
titlestr = 'Global mean EBC: N(corrected stations)=' + str(stationcodes_ebm.shape[0])    
xstr = 'Year'
ystr = 'Bias, °C'

fig, ax = plt.subplots(figsize=(15,10))          
for i in range(12):    
    plt.plot( df_ebc.groupby('year').mean().iloc[:,i], label='Month '+str(i+1))
plt.tick_params(labelsize=fontsize)    
plt.legend(loc='lower right', ncol=4, fontsize=12)
plt.xlabel(xstr, fontsize=fontsize)
plt.ylabel(ystr, fontsize=fontsize)
plt.title(titlestr, fontsize=fontsize)
plt.savefig(figstr, dpi=300, bbox_inches='tight')
plt.close(fig)
            
#------------------------------------------------------------------------------
print('** END')



    
