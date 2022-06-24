#------------------------------------------------------------------------------
# PROGRAM: exposure-bias-metadata-reader.py
#------------------------------------------------------------------------------
# Version 0.1
# 30 May, 2022
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
# Plotting libraries:
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS
#------------------------------------------------------------------------------

fontsize = 16
use_nma_assumption = False     # (default=False) True --> use all source_codes
use_transition = True          # (default=True) False --> include transitions in categories

#------------------------------------------------------------------------------
# LOAD: Emily's raw data
#------------------------------------------------------------------------------

#metadatafile = 'DATA/GloSATPrelim04StationData_Exposure_DataforMTaylor.csv'
#df_metadata = pd.read_csv( metadatafile ) 

#Index(['year', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
#       'stationcode', 'stationlat', 'stationlon', 'stationelevation',
#       'stationname', 'stationcountry', 'stationfirstyear', 'stationlastyear',
#       'stationsource', 'stationfirstreliable', 'exposure',
#       'exposure_category', 'source_flag', 'exposurecorrected_flag'],
#      dtype='object')

metadatafile = 'DATA/df_exposure_bias.pkl'
df_metadata = pd.read_pickle( metadatafile, compression='bz2' )

#Index(['datetime', 'stationcode', 'exposure_category', 'bias', 'uncertainty', 'source_flag', 'exposurecorrected_flag'],
#      dtype='object')

columns = [ 'datetime', 'stationcode', 'exposure_category', 'source_flag', 'exposurecorrected_flag' ]
df = pd.DataFrame(df_metadata, columns=columns)
    
#------------------------------------------------------------------------------
# STATS:
#------------------------------------------------------------------------------

t_start = df.datetime.dt.year.min()                                                     # 1781
t_end = df.datetime.dt.year.max()                                                       # 2021
n_stations = df.stationcode.unique().shape[0]                                           # 4404
n_exposure_category = df.exposure_category.unique().shape[0]                            #  15 ( see below )
n_source_flag = df.source_flag.unique().shape[0]                                        #   4 [ nan, 1., 2., 3. ]
n_exposurecorrected_flag = df.exposurecorrected_flag.unique().shape[0]                  #   2 [ nan, 1. ]
n_exposurecorrected = df[df.exposurecorrected_flag==1].stationcode.unique().shape[0]    #  21

#------------------------------------------------------------------------------
# APPLY: filters
#------------------------------------------------------------------------------

if use_nma_assumption == False: df = df[ (df.source_flag < 3) ]
if use_transition == False: df = df[ df.exposure_category.str.contains('Transition') == False ]

#------------------------------------------------------------------------------
# FIND: breaks
#------------------------------------------------------------------------------

# CREATE: dictionary mapping exposure_category keys to integer values

dg = df.copy().dropna(subset=['exposure_category','source_flag']).reset_index(drop=True)
exposure_category_dict = dict( zip( dg.exposure_category.unique(), np.arange(n_exposure_category) ) )

# APPLY: dict map to dataframe

dg['exposure_category'] = dg['exposure_category'].map( exposure_category_dict )

# FIND: break indices
    
v = dg['exposure_category']
t = np.where( np.diff(v) )[0] + 1  

# EXTRACT: breaks subset

dh = dg.copy()
mask = list( set( np.arange(len(dh)) ) - set(t) )
dh = dh.drop( mask )

#==============================================================================
# PLOTS
#==============================================================================

# PLOT: breakpoints from exposure changes ( x=stationcode, y=breakpoint year )

assumptionstr = ''
transitionstr = ''
if use_nma_assumption == True: assumptionstr = '_nma_assumption'
if use_transition == True: transitionstr = '_transition'
figstrstem = 'breakpoints_exposure_category_source_code_stationcode'
figstr = figstrstem + assumptionstr + transitionstr + '.png'


fig, ax = plt.subplots(figsize=(12, 7))
for i in range( dh.source_flag.unique().shape[0] ):    
    da = dh[ dh.source_flag == i+1 ]
#    plt.plot(da.stationcode, da.datetime.dt.year, 'o', markersize=5, alpha=0.5, label='source_code='+str(i+1)+' : median='+str( int( np.median( da.datetime.dt.year ) ) ) )
    plt.plot(da.datetime.dt.year, 'o', markersize=5, alpha=0.5, label='source_code='+str(i+1)+' : median='+str( int( np.median( da.datetime.dt.year ) ) ) )
ax.axes.xaxis.set_ticklabels([])
plt.legend(loc='lower right', fontsize=fontsize)
plt.xlabel('stationcode', fontsize=fontsize)
plt.ylabel('breakpoint year', fontsize=fontsize)
plt.title( 'Breakpoints from changes in exposure_category', fontsize=fontsize )
plt.savefig( figstr, dpi=300 )

# PLOT: distribution of breakpoint years by source_code

assumptionstr = ''
transitionstr = ''
if use_nma_assumption == True: assumptionstr = '_nma_assumption'
if use_transition == True: transitionstr = '_transition'
figstrstem = 'breakpoints_exposure_category_source_code_violinplot'
figstr = figstrstem + assumptionstr + transitionstr + '.png'

fig, ax = plt.subplots(figsize=(12, 7))
for i in range( dh.source_flag.unique().shape[0] ):
    da = dh[ dh.source_flag == i+1 ]
    ax.violinplot(da.datetime.dt.year, positions = [i+1])
ax.set_xlim(0.5, dh.source_flag.unique().shape[0] + 0.5)
positions   = [1, 2, 3]
labels = ['1','2','3']
ax.set_xticks(positions)
ax.set_xticklabels(labels)
plt.xlabel('source_code', fontsize=fontsize)
plt.ylabel('breakpoint year', fontsize=fontsize)
plt.title( 'Breakpoints from changes in exposure_category', fontsize=fontsize )
plt.savefig( figstr, dpi=300 )

#==============================================================================
# SAVE: breakpoints dataframe
#==============================================================================

assumptionstr = ''
transitionstr = ''
if use_nma_assumption == True: assumptionstr = '_nma_assumption'
if use_transition == True: transitionstr = '_transition'
pklstem = 'df_breaks'
pklfile = pklstem + assumptionstr + transitionstr + '.pkl'

dh.to_pickle( pklfile, compression='bz2')

#------------------------------------------------------------------------------
print('** END')

#------------------------------------------------------------------------------
# exposurecorrected_flag A-Z: (float64)
#------------------------------------------------------------------------------

# np.sort( list(df.exposurecorrected_flag.unique()) )
#
# array([ nan, 1.])

#------------------------------------------------------------------------------
# source_flags A-Z: (float64)
#------------------------------------------------------------------------------

#  np.sort( list(df.source_flag.unique()) )
#
# array([ nan, 1.,  2.,  3.])
#
# 1 – Known exposure based on station-specific metadata (e.g. where the exposure has been documented in 
#     a paper or station yearbook).
# 2 – Exposure estimated based on station-specific metadata (e.g. from incomplete descriptions of the exposure, 
#     or based on known exposures at other points in the station record).
# 3 – Exposure estimated based on country (or state)-level metadata (e.g. from national guides for observers).
#
# I think the columns are the same as you have seen previously, although I have left in an additional column 
# for ‘exposure’ (as well as ‘exposure_category’). This column sometimes gives a bit more detail about the exposure, 
# and may have breakpoints that are not present in the ‘exposure_category’ column, for example where the exposure changed, 
# but stayed within the same category grouping.
# 
# From a quick analysis it looks like I have exposure information for 5869 stations (I have only been adding exposure 
# information to stations that have a first year <= 1960). The majority of this information is source code 3, 
# but I have source code 1 or 2 information for 908 stations (and this will increase when I finish adding in the data 
# for Germany, Poland and Italy and elsewhere).

#------------------------------------------------------------------------------
# exposure_categories A-Z: (object)
#------------------------------------------------------------------------------
    
# np.sort( list(df.exposure_category.unique()) ) 
#
# array(['nan',
#       'Closed', 
#       'Closed Roof', 
#       'Intermediate', 
#       'Miscellaneous', 
#       'Open',
#       'Open/Wall', 
#       'Stevenson screen', 'Stevenson screen Roof',
#       'Transition Montsouris', 'Transition Stevenson-type screen', 'Transition Wild hut', 
#       'Unknown', 
#       'Wall'], dtype='<U32')
#------------------------------------------------------------------------------






    
