#------------------------------------------------------------------------------
# PROGRAM: exposure-bias-model-reader.py
#------------------------------------------------------------------------------
# Version 0.4
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
from datetime import datetime
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

modelfile1 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.4_Part1_GloSAT_22.06.22.csv'
modelfile2 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.4_Part2_GloSAT_22.06.22.csv'
modelfile3 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.4_Part3_GloSAT_22.06.22.csv'
modelfile4 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.4_Part4_GloSAT_22.06.22.csv'
modelfile5 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.4_Part5_GloSAT_22.06.22.csv'
modelfile6 = 'DATA/GloSATP04_Extratropics_ExposureBias_v0.4_Part6_GloSAT_22.06.22.csv'

exposure_bias_model_file = 'df_exposure_bias.pkl'

#------------------------------------------------------------------------------
# LOAD: Emily's raw data
#------------------------------------------------------------------------------

df1 = pd.read_csv( modelfile1 ) 
df2 = pd.read_csv( modelfile2 ) 
df3 = pd.read_csv( modelfile3 ) 
df4 = pd.read_csv( modelfile4 ) 
df5 = pd.read_csv( modelfile5 ) 
df6 = pd.read_csv( modelfile6 ) 

# Index(['index', 'stationcode', 'exposure_category', 'bias_estimate', 'bias_estimate_2.5', 'bias_estimate_97.5', 'source_flag', 'exposurecorrected_flag'], dtype='object')

#------------------------------------------------------------------------------
# MUNGE
#------------------------------------------------------------------------------

# CONCATENATE: timestamps (yyyy-mm-dd --> datetime64)

datetimes1 = df1[ df1.columns[0] ]
datetimes2 = df2[ df2.columns[0] ]
datetimes3 = df3[ df3.columns[0] ]
datetimes4 = df4[ df4.columns[0] ]
datetimes5 = df5[ df5.columns[0] ]
datetimes6 = df6[ df6.columns[0] ]

datetimes1_standardized = list( pd.to_datetime(datetimes1, format='%Y-%m-%d') )
datetimes2_standardized = list( pd.to_datetime(datetimes2, format='%Y-%m-%d') )
datetimes3_standardized = list( pd.to_datetime(datetimes3, format='%Y-%m-%d') )
datetimes4_standardized = list( pd.to_datetime(datetimes4, format='%Y-%m-%d') )
datetimes5_standardized = list( pd.to_datetime(datetimes5, format='%Y-%m-%d') )
datetimes6_standardized = list( pd.to_datetime(datetimes6, format='%Y-%m-%d') )

datetimes = datetimes1_standardized + datetimes2_standardized + datetimes3_standardized + datetimes4_standardized + datetimes5_standardized + datetimes6_standardized

# CONCATENATE: stationcodes list [ NB: int64 --> 6-digit str ]

stationcodes1 = df1[ df1.columns[1] ]
stationcodes2 = df2[ df2.columns[1] ]
stationcodes3 = df3[ df3.columns[1] ]
stationcodes4 = df4[ df4.columns[1] ]
stationcodes5 = df5[ df5.columns[1] ]
stationcodes6 = df6[ df6.columns[1] ]

stationcodes1_6digit = [ str(stationcodes1[i]).zfill(6) for i in range(len(stationcodes1)) ]
stationcodes2_6digit = [ str(stationcodes2[i]).zfill(6) for i in range(len(stationcodes2)) ]
stationcodes3_6digit = [ str(stationcodes3[i]).zfill(6) for i in range(len(stationcodes3)) ]
stationcodes4_6digit = [ str(stationcodes4[i]).zfill(6) for i in range(len(stationcodes4)) ]
stationcodes5_6digit = [ str(stationcodes5[i]).zfill(6) for i in range(len(stationcodes5)) ]
stationcodes6_6digit = [ str(stationcodes6[i]).zfill(6) for i in range(len(stationcodes6)) ]

stationcodes = stationcodes1_6digit + stationcodes2_6digit + stationcodes3_6digit + stationcodes4_6digit + stationcodes5_6digit + stationcodes6_6digit 

# CONCATENATE: exposure_category list --> used to create dict for integer changepoint flag

exposure_category1 = list( df1[ df1.columns[2] ] )
exposure_category2 = list( df2[ df2.columns[2] ] )
exposure_category3 = list( df3[ df3.columns[2] ] )
exposure_category4 = list( df4[ df4.columns[2] ] )
exposure_category5 = list( df5[ df5.columns[2] ] )
exposure_category6 = list( df6[ df6.columns[2] ] )

exposure_categories = exposure_category1 + exposure_category2 + exposure_category3 + exposure_category4 + exposure_category5 + exposure_category6

# CONCATENATE: bias estimates

bias_estimates1 = list( df1[ df1.columns[3] ] )
bias_estimates2 = list( df2[ df2.columns[3] ] )
bias_estimates3 = list( df3[ df3.columns[3] ] )
bias_estimates4 = list( df4[ df4.columns[3] ] )
bias_estimates5 = list( df5[ df5.columns[3] ] )
bias_estimates6 = list( df6[ df6.columns[3] ] )

bias_estimates = bias_estimates1 + bias_estimates2 + bias_estimates3 + bias_estimates4 + bias_estimates5 + bias_estimates6

# COMPUTE + CONCATENATE: 95% c.i. uncertainty

bias_estimates1_025 = df1[ df1.columns[4] ]
bias_estimates2_025 = df2[ df2.columns[4] ]
bias_estimates3_025 = df3[ df3.columns[4] ]
bias_estimates4_025 = df4[ df4.columns[4] ]
bias_estimates5_025 = df5[ df5.columns[4] ]
bias_estimates6_025 = df6[ df6.columns[4] ]

bias_estimates1_975 = df1[ df1.columns[5] ]
bias_estimates2_975 = df2[ df2.columns[5] ]
bias_estimates3_975 = df3[ df3.columns[5] ]
bias_estimates4_975 = df4[ df4.columns[5] ]
bias_estimates5_975 = df5[ df5.columns[5] ]
bias_estimates6_975 = df6[ df6.columns[5] ]
              
bias_uncertainty1 = list( np.subtract( bias_estimates1_975, bias_estimates1_025 ) )
bias_uncertainty2 = list( np.subtract( bias_estimates2_975, bias_estimates2_025 ) )
bias_uncertainty3 = list( np.subtract( bias_estimates3_975, bias_estimates3_025 ) )
bias_uncertainty4 = list( np.subtract( bias_estimates4_975, bias_estimates4_025 ) )
bias_uncertainty5 = list( np.subtract( bias_estimates5_975, bias_estimates5_025 ) )
bias_uncertainty6 = list( np.subtract( bias_estimates6_975, bias_estimates6_025 ) )

bias_uncertainties = bias_uncertainty1 + bias_uncertainty2 + bias_uncertainty3 + bias_uncertainty4 + bias_uncertainty5 + bias_uncertainty6
               
# Index(['index', 'stationcode', 'exposure_category', 'bias_estimate', 'bias_estimate_2.5', 'bias_estimate_97.5', 'source_flag', 'exposurecorrected_flag'], dtype='object')

# CONCATENATE: source_flag

source_flags1 = list( df1[ df1.columns[6] ] )
source_flags2 = list( df2[ df2.columns[6] ] )
source_flags3 = list( df3[ df3.columns[6] ] )
source_flags4 = list( df4[ df4.columns[6] ] )
source_flags5 = list( df5[ df5.columns[6] ] )
source_flags6 = list( df6[ df6.columns[6] ] )

source_flags = source_flags1 + source_flags2 + source_flags3 + source_flags4 + source_flags5 + source_flags6

# CONCATENATE: exposurecorrected_flag

exposurecorrected_flags1 = list( df1[ df1.columns[7] ] )
exposurecorrected_flags2 = list( df2[ df2.columns[7] ] )
exposurecorrected_flags3 = list( df3[ df3.columns[7] ] )
exposurecorrected_flags4 = list( df4[ df4.columns[7] ] )
exposurecorrected_flags5 = list( df5[ df5.columns[7] ] )
exposurecorrected_flags6 = list( df6[ df6.columns[7] ] )

exposurecorrected_flags = exposurecorrected_flags1 + exposurecorrected_flags2 + exposurecorrected_flags3 + exposurecorrected_flags4 + exposurecorrected_flags5 + exposurecorrected_flags6 

# CONSTRUCT: dataframe

df = pd.DataFrame( {'datetime':datetimes, 'stationcode':stationcodes, 'exposure_category':exposure_categories, 'bias':bias_estimates, 
                    'uncertainty':bias_uncertainties, 'source_flag':source_flags, 'exposurecorrected_flag':exposurecorrected_flags } )
                    
# SAVE: dataframe
                    
df.to_pickle( exposure_bias_model_file, compression='bz2' )

#------------------------------------------------------------------------------
print('** END')




    
