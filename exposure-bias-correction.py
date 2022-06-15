#------------------------------------------------------------------------------
# PROGRAM: exposure-bias-correction.py
#------------------------------------------------------------------------------
# Version 0.2
# 14 June, 2022
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

import matplotlib.pyplot as plt

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

df_temp_file = 'DATA/df_temp_qc.pkl'
df_ebm_file = 'OUT/df_exposure_bias.pkl'
df_temp_ebc_file = 'OUT/df_temp_ebc.pkl'
df_ebc_file = 'OUT/df_ebc.pkl'

#------------------------------------------------------------------------------
# LOAD: temperature .pkl file
#------------------------------------------------------------------------------

df_temp = pd.read_pickle( df_temp_file, compression='bz2' )

# TEIM: to GloSAT year range [1781,2022]

df_temp = df_temp[ (df_temp.year >= 1781) & (df_temp.year <= 2022) ]
stationcodes_temp = df_temp.stationcode.unique()

#------------------------------------------------------------------------------
# LOAD: exposure bias model .pkl file
#------------------------------------------------------------------------------

df_ebm = pd.read_pickle( df_ebm_file, compression='bz2' )
stationcodes_ebm = df_ebm.stationcode.unique()

df_ebm['bias'] = df_ebm['bias'].replace(np.nan, 0.0)

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
        
        idx = df_temp_ebc[ df_temp_ebc.stationcode == stationcodes_temp[k] ].index

        # ADD: EBC to temperature data

        for i in range(1,13): 
            
            df_temp_ebc.iloc[idx, i] += da[da.datetime.dt.month == i].bias.values
            df_ebc.iloc[idx, i] += da[da.datetime.dt.month == i].bias.values
 
    else:
        
        continue
        
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
print('** END')


plt.plot(df_temp.year, df_temp['1'],'o')
plt.plot(df_temp_ebc.year, df_temp_ebc['1'],'.')


    
