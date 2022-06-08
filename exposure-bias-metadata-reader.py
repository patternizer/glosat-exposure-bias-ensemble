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
use_exposure_category = True    # (default=True) False --> use exposure
use_nma_assumption = True      # (default=False) True --> use all source_codes
use_transition = True          # (default=False) True --> include transitions in categories

#------------------------------------------------------------------------------
# LOAD: Emily's raw data
#------------------------------------------------------------------------------

metadatafile = 'DATA/GloSATPrelim04StationData_Exposure_DataforMTaylor.csv'

df_metadata = pd.read_csv( metadatafile ) 

#Index(['year', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
#       'stationcode', 'stationlat', 'stationlon', 'stationelevation',
#       'stationname', 'stationcountry', 'stationfirstyear', 'stationlastyear',
#       'stationsource', 'stationfirstreliable', 'exposure',
#       'exposure_category', 'source_flag', 'exposurecorrected_flag'],
#      dtype='object')

columns = [ 'year', 'stationcode', 'stationlat', 'stationlon', 'stationelevation', 'exposure', 'exposure_category', 'source_flag', 'exposurecorrected_flag' ]
df = pd.DataFrame(df_metadata, columns=columns)
    
#------------------------------------------------------------------------------
# STATS:
#------------------------------------------------------------------------------

t_start = df.year.min()                                                                 # 1658
t_end = df.year.max()                                                                   # 2021
n_stations = df.stationcode.unique().shape[0]                                           # 11873
n_exposure = df.exposure.unique().shape[0]                                              # 130 ( see below )
n_exposure_category = df.exposure_category.unique().shape[0]                            #  14 ( see below )
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

if use_exposure_category == True:

    dg = df.copy().dropna(subset=['exposure_category','source_flag']).reset_index(drop=True)
    exposure_category_dict = dict( zip( dg.exposure_category.unique(), np.arange(n_exposure_category) ) )

    # APPLY: dict map to dataframe

    dg['exposure_category'] = dg['exposure_category'].map( exposure_category_dict )

    # FIND: break indices
    
    v = dg['exposure_category']
    t = np.where( np.diff(v) )[0] + 1  

else:

    dg = df.copy().dropna(subset=['exposure','source_flag']).reset_index(drop=True)
    exposure_dict = dict( zip( dg.exposure.unique(), np.arange(n_exposure) ) )

    # APPLY: dict map to dataframe

    dg['exposure'] = dg['exposure'].map( exposure_dict )

    # FIND: break indices
    
    v = dg['exposure']
    t = np.where( np.diff(v) )[0] + 1  

# EXTRACT: breaks subset

dh = dg.copy()
mask = list( set( np.arange(len(dh)) ) - set(t) )
dh = dh.drop( mask )

#==============================================================================
# PLOTS
#==============================================================================

# PLOT: breakpoints from exposure changes ( x=stationcode, y=breakpoint year )

fig, ax = plt.subplots(figsize=(12, 7))
for i in range( dh.source_flag.unique().shape[0] ):    
    da = dh[ dh.source_flag == i+1 ]
    plt.plot(da.stationcode, da.year, 'o', markersize=5, alpha=0.5, label='source_code='+str(i+1)+' : median='+str( int( np.median( da.year ) ) ) )
ax.axes.xaxis.set_ticklabels([])
plt.legend(loc='lower right', fontsize=fontsize)
plt.xlabel('stationcode', fontsize=fontsize)
plt.ylabel('breakpoint year', fontsize=fontsize)
if use_exposure_category == True:
    plt.title( 'Breakpoints from changes in exposure_category', fontsize=fontsize )
    plt.savefig( 'breakpoints_exposure_category_source_code_stationcode.png', dpi=300 )
else:
    plt.title( 'Breakpoints from changes in exposure', fontsize=fontsize )
    plt.savefig( 'breakpoints_exposure_source_code_stationcode.png', dpi=300 )

# PLOT: distribution of breakpoint years by source_code

fig, ax = plt.subplots(figsize=(12, 7))
for i in range( dh.source_flag.unique().shape[0] ):
    da = dh[ dh.source_flag == i+1 ]
    ax.violinplot(da.year, positions = [i+1])
ax.set_xlim(0.5, dh.source_flag.unique().shape[0] + 0.5)
positions   = [1, 2, 3]
labels = ['1','2','3']
ax.set_xticks(positions)
ax.set_xticklabels(labels)
plt.xlabel('source_code', fontsize=fontsize)
plt.ylabel('breakpoint year', fontsize=fontsize)
if use_exposure_category == True:
    plt.title( 'Breakpoints from changes in exposure_category', fontsize=fontsize )
    plt.savefig( 'breakpoints_exposure_category_source_code_violinplot.png', dpi=300 )
else:
    plt.title( 'Breakpoints from changes in exposure', fontsize=fontsize )
    plt.savefig( 'breakpoints_exposure_source_code_violinplot.png', dpi=300 )

#==============================================================================
# SAVE: breakpoints dataframe
#==============================================================================

dh.to_pickle('df_breaks.pkl', compression='bz2')

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
# exposure A-Z: (object)
#------------------------------------------------------------------------------
        
# np.sort( list(df.exposure.unique()) )
#
# array(['nan', 
#       'AMJJASO: Hazen shelter; NDJFM: Wall', 'AWS', 'Balcony', 'Bilham screen', 'CRS', 'CRS Roof', 
#       'Canadian thermometer shelter', 'Canvas tent on roof', 'Double screen', 'Double screen Roof',
#       'E Wall', 'E wall (no screen)', 'ENE window', 'East Wall', 'East wall', 'East window shelter',
#       'Eiffel Shelter adapted for the Tropics', 'French screen',
#      
#       'Glaisher', 
#       'Glaisher stand', 
#       'Glaisher stand in Summerhouse',
#       'Glaisher/Wall', 
#       
#       'Greenwich stand', 'Indian Pattern Thermometer shed', 'Indian Thatched Shelter',
#
#       'Inside and unheated room', 
#       'Inside glass gallery',
#       'Inside large room', 
#       'Inside small house', 
#       'Inside small room',
#       
#       'Large Octogonal screen', 'Large louvred screen', 'Lawson shelter', 'Louvred Octogon (Summerhouse)', 
#       'Louvred shed', 'MMTS', 'Metal cylindrical housing N window', 'Metal screen', 'Modified Greenwich stand', 
#       
#       'Montsouris',
#       
#       'N balcony wickerwork housing', 'N wall (no screen)', 'N window', 'N window (no screen)', 'NE Wall (no screen)', 
#       'NE window', 'NE window shelter', 'NNW window', 'NNW window shelter', 'NW Window shelter', 
#       'NW wall', 'NW window shelter', 'North Porch',
#
#       'North Wall', 
#       'North Wall (cylindrical metal shield)',
#       'North Wall (no screen)', 
#       'North Wall (unscreened)',
#       'North Window', 'North Window shelter', 'North wall',
#       'North wall (zinc cylindrical screen)', 'North window',
#       'North window shelter', 'North window shelter influenced by stove',
#
#       'Open',
#
#       'Pavillion on roof with thermometer inside in zinc housing', 'Porch', 'Porch wall', 'Radiation shield', 
#       'Railroad shelter', 'SE Balcony - poor exposure', 'SE Verandah', 'SS at N Wall', 'SW Window screen', 
#       'Shade of a tree', 'Shelter on tower terrace', 'Smithsonian window shelter, near fireplace and chimney',
#       'South porch, inside on sunny days', 'South wall', 'South window',
#
#       'Stevenson screen', 
#       'Stevenson screen Roof',
#       'Stevenson type screen', 
#       'Stevenson type screen 2nd floor Terrace',
#       'Stevenson type screen Roof',
#       'Stevenson type screen Roof (poor exposure)',
#       'Stevenson type screen Roof close to chimney',
#       'Stevenson type screen Roof close to steam vent',
#       'Stevenson-type screen', 
#       'Stevensone screen', 
#
#       'Summerhouse', 'Thermometer hut on roof', 'Thermometer shed', 'Tin housing on North wall', 'Tin shelter at N window',
#
#       'Transition Montsouris', 
#       'Transition Stevenson-type screen',
#       'Transition Wild hut', 
#
#       'Trestle', 'Under piazza', 'Unknown', 'Unstandardised', 'Verandah', 
#
#       'Wall', 
#       'Wall (no screen)',
#       'Wall mounted tin housing, influenced by radiation', 
#       'Wall screen',
#       'Wall shelter', 
#
#       'Wild hut',
#       'Wild hut not according to instructions',
#       'Wild shield and hut at NNE window', 
#       'Wild shield at North window',
#
#       'Window', 
#       'Window (no screen)', 
#       'Window in porch',
#       'Window mounted wild screen and hut',
#       'Window of unheated building', 
#       'Window shelter',
#
#       'Zinc housing NE window', 'Zinc housing and Wild hut at N window', 'Zinc housing at N window', 
#       'Zinc sheet housing at NNE wall', 'Zinc sheet housing in wood hut mounted on N Wall',
#       'Zinc sheeting in garden', 'Zinc sheild inside canvas covered box',
#       'Zinc shield and Wild hut mounted at window in porch', 'Zinc shield and Wild shelter at window',
#       'Zinc shield inside Wild hut on NE wall', 'zinc sheet housing on 2nd floor balcony'], dtype='<U57')    
#------------------------------------------------------------------------------






    
