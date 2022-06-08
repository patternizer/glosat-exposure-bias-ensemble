#------------------------------------------------------------------------------
# PROGRAM: exposure-bias-model-reader.py
#------------------------------------------------------------------------------
# Version 0.2
# 4 May, 2022
# Michael Taylor
# https://patternizer.github.io
# michael DOT a DOT taylor AT uea DOT ac DOT uk
# patternizer AT gmail DOT com
#------------------------------------------------------------------------------

# PLAN A: produce HadXRUT5-analysis exposure bias field and save in CRUTEM5 format [DONE] 
# PLAN B: update HadCRUT5-analysis field with exposure bias model and save in CRUTEM5 format
# PLAN C: compare updated exposure bias field with LEK adjustment ( LEK - obs ) field    

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------
# Dataframe libraries:
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

t_start = 1781
t_end = 2021

modelfile1 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.1_Part1.csv'
modelfile2 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.1_Part2.csv'
modelfile3 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.1_Part3.csv'
modelfile4 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.1_Part4.csv'
modelfile5 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.1_Part5.csv'

exposure_bias_model_file = 'OUT/df_exposure_bias.pkl'

#------------------------------------------------------------------------------
# LOAD: Emily's raw data
#------------------------------------------------------------------------------

df1 = pd.read_csv( modelfile1 ) 
df2 = pd.read_csv( modelfile2 ) 
df3 = pd.read_csv( modelfile3 ) 
df4 = pd.read_csv( modelfile4 ) 
df5 = pd.read_csv( modelfile5 ) 

# Index(['index', 'stationcode', 'exposure_category', 'bias_estimate',
#       'bias_estimate_2.5', 'bias_estimate_97.5', 'source_flag', 'exposurecorrected_flag'],
#      dtype='object')

#------------------------------------------------------------------------------
# MUNGE
#------------------------------------------------------------------------------

# FIX: date list [ mixed format dd/mm/yyyy & yyyy-mm-dd --> datetime64 ]

datetimes1 = df1[ df1.columns[0] ]
datetimes2 = df2[ df2.columns[0] ]
datetimes3 = df3[ df3.columns[0] ]
datetimes4 = df4[ df4.columns[0] ]
datetimes5 = df5[ df5.columns[0] ]

split1a = [ datetimes1[i].split('/') for i in range(len(datetimes1)) ]
split2a = [ datetimes2[i].split('/') for i in range(len(datetimes2)) ]
split3a = [ datetimes3[i].split('/') for i in range(len(datetimes3)) ]
split4a = [ datetimes4[i].split('/') for i in range(len(datetimes4)) ]
split5a = [ datetimes5[i].split('/') for i in range(len(datetimes5)) ]

split1b = [ datetimes1[i].split('-') for i in range(len(datetimes1)) ]
split2b = [ datetimes2[i].split('-') for i in range(len(datetimes2)) ]
split3b = [ datetimes3[i].split('-') for i in range(len(datetimes3)) ]
split4b = [ datetimes4[i].split('-') for i in range(len(datetimes4)) ]
split5b = [ datetimes5[i].split('-') for i in range(len(datetimes5)) ]

nsplit1a = [ len(datetimes1[i].split('/')) for i in range(len(datetimes1)) ]
nsplit2a = [ len(datetimes2[i].split('/')) for i in range(len(datetimes2)) ]
nsplit3a = [ len(datetimes3[i].split('/')) for i in range(len(datetimes3)) ]
nsplit4a = [ len(datetimes4[i].split('/')) for i in range(len(datetimes4)) ]
nsplit5a = [ len(datetimes5[i].split('/')) for i in range(len(datetimes5)) ]

datetimes1_standardized = []    
datetimes2_standardized = []    
datetimes3_standardized = []    
datetimes4_standardized = []    
datetimes5_standardized = []    

for i in range(len(datetimes1)):    
    if np.isin( nsplit1a[i], 3 ):
        datetimes1_standardized.append( pd.to_datetime( split1b[i], format='%d/%m/%Y' ) )
    else:
        datetimes1_standardized.append( pd.to_datetime( split1a[i], format='%Y-%m-%d') )

for i in range(len(datetimes2)):    
    if np.isin( nsplit2a[i], 3 ):
        datetimes2_standardized.append( pd.to_datetime( split2b[i], format='%d/%m/%Y' ) )
    else:
        datetimes2_standardized.append( pd.to_datetime( split2a[i], format='%Y-%m-%d') )

for i in range(len(datetimes3)):    
    if np.isin( nsplit3a[i], 3 ):
        datetimes3_standardized.append( pd.to_datetime( split3b[i], format='%d/%m/%Y' ) )
    else:
        datetimes3_standardized.append( pd.to_datetime( split3a[i], format='%Y-%m-%d') )

for i in range(len(datetimes4)):    
    if np.isin( nsplit4a[i], 3 ):
        datetimes4_standardized.append( pd.to_datetime( split4b[i], format='%d/%m/%Y' ) )
    else:
        datetimes4_standardized.append( pd.to_datetime( split4a[i], format='%Y-%m-%d') )

for i in range(len(datetimes5)):    
    if np.isin( nsplit5a[i], 3 ):
        datetimes5_standardized.append( pd.to_datetime( split5b[i], format='%d/%m/%Y' ) )
    else:
        datetimes5_standardized.append( pd.to_datetime( split5a[i], format='%Y-%m-%d') )

datetimes = datetimes1_standardized + datetimes2_standardized + datetimes3_standardized + datetimes4_standardized + datetimes5_standardized
timestamps = [ datetimes[i][0] for i in range(len(datetimes)) ] 

# FIX: stationcodes list [ int64 --> 6-digit str ]

stationcodes1 = df1[ df1.columns[1] ]
stationcodes2 = df2[ df2.columns[1] ]
stationcodes3 = df3[ df3.columns[1] ]
stationcodes4 = df4[ df4.columns[1] ]
stationcodes5 = df5[ df5.columns[1] ]

stationcodes1_6digit = [ str(stationcodes1[i]).zfill(6) for i in range(len(stationcodes1)) ]
stationcodes2_6digit = [ str(stationcodes2[i]).zfill(6) for i in range(len(stationcodes2)) ]
stationcodes3_6digit = [ str(stationcodes3[i]).zfill(6) for i in range(len(stationcodes3)) ]
stationcodes4_6digit = [ str(stationcodes4[i]).zfill(6) for i in range(len(stationcodes4)) ]
stationcodes5_6digit = [ str(stationcodes5[i]).zfill(6) for i in range(len(stationcodes5)) ]

stationcodes = stationcodes1_6digit + stationcodes2_6digit + stationcodes3_6digit + stationcodes4_6digit + stationcodes5_6digit 

# STORE: wall types list --> create dict for integer flag

wall_types1 = list( df1[ df1.columns[2] ] )
wall_types2 = list( df2[ df2.columns[2] ] )
wall_types3 = list( df3[ df3.columns[2] ] )
wall_types4 = list( df4[ df4.columns[2] ] )
wall_types5 = list( df5[ df5.columns[2] ] )

wall_types = wall_types1 + wall_types2 + wall_types3 + wall_types4 + wall_types5

# FIX: bias estimate list [ entries where no c.i. exists but bias_estimates_97.5 column contains values --> np.nan ]

bias_estimates1 = df1[ df1.columns[3] ]
bias_estimates2 = df2[ df2.columns[3] ]
bias_estimates3 = df3[ df3.columns[3] ]
bias_estimates4 = df4[ df4.columns[3] ]
bias_estimates5 = df5[ df5.columns[3] ]

bias_estimates = list( bias_estimates1 ) + list( bias_estimates2 ) + list( bias_estimates3 ) + list( bias_estimates4 ) + list( bias_estimates5 )

bias_estimates1_025 = df1[ df1.columns[4] ]
bias_estimates2_025 = df2[ df2.columns[4] ]
bias_estimates3_025 = df3[ df3.columns[4] ]
bias_estimates4_025 = df4[ df4.columns[4] ]
bias_estimates5_025 = df5[ df5.columns[4] ]

bias_estimates1_975 = df1[ df1.columns[5] ]
bias_estimates2_975 = df2[ df2.columns[5] ]
bias_estimates3_975 = df3[ df3.columns[5] ]
bias_estimates4_975 = df4[ df4.columns[5] ]
bias_estimates5_975 = df5[ df5.columns[5] ]

bias_estimates1_975_fixed = []
bias_estimates2_975_fixed = []
bias_estimates3_975_fixed = []
bias_estimates4_975_fixed = []
bias_estimates5_975_fixed = []

for i in range(len(bias_estimates1)):    
    if np.isnan( bias_estimates1[i] ) & np.isnan( bias_estimates1_025[i] ):
        bias_estimates1_975_fixed.append( np.nan )
    else:
        bias_estimates1_975_fixed.append( bias_estimates1_975[i] )

for i in range(len(bias_estimates2)):    
    if np.isnan( bias_estimates2[i] ) & np.isnan( bias_estimates2_025[i] ):
        bias_estimates2_975_fixed.append( np.nan )
    else:
        bias_estimates2_975_fixed.append( bias_estimates2_975[i] )

for i in range(len(bias_estimates3)):    
    if np.isnan( bias_estimates3[i] ) & np.isnan( bias_estimates3_025[i] ):
        bias_estimates3_975_fixed.append( np.nan )
    else:
        bias_estimates3_975_fixed.append( bias_estimates3_975[i] )

for i in range(len(bias_estimates4)):    
    if np.isnan( bias_estimates4[i] ) & np.isnan( bias_estimates4_025[i] ):
        bias_estimates4_975_fixed.append( np.nan )
    else:
        bias_estimates4_975_fixed.append( bias_estimates4_975[i] )

for i in range(len(bias_estimates5)):    
    if np.isnan( bias_estimates5[i] ) & np.isnan( bias_estimates5_025[i] ):
        bias_estimates5_975_fixed.append( np.nan )
    else:
        bias_estimates5_975_fixed.append( bias_estimates5_975[i] )

# COMPUTE: 95% c.i. uncertainty
                
bias_uncertainty1 = list( np.subtract( bias_estimates1_975_fixed, bias_estimates1_025 ) )
bias_uncertainty2 = list( np.subtract( bias_estimates2_975_fixed, bias_estimates2_025 ) )
bias_uncertainty3 = list( np.subtract( bias_estimates3_975_fixed, bias_estimates3_025 ) )
bias_uncertainty4 = list( np.subtract( bias_estimates4_975_fixed, bias_estimates4_025 ) )
bias_uncertainty5 = list( np.subtract( bias_estimates5_975_fixed, bias_estimates5_025 ) )

bias_uncertainties = bias_uncertainty1 + bias_uncertainty2 + bias_uncertainty3 + bias_uncertainty4 + bias_uncertainty5
                
# CONSTRUCT: dataframe

df = pd.DataFrame( {'datetime':timestamps, 'stationcode':stationcodes, 'wall_type':wall_types, 'bias':bias_estimates, 'uncertainty':bias_uncertainties} )
df.to_pickle( exposure_bias_model_file, compression='bz2' )

#------------------------------------------------------------------------------
print('** END')




    
