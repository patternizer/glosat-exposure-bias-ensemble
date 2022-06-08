#------------------------------------------------------------------------------
# PROGRAM: exposure-bias-hadcrut5.py
#------------------------------------------------------------------------------
# Version 0.2
# 3 May, 2022
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

# Stats libraries:
import random

# Maths libraries
import scipy

# Silence library version notifications
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

t_start = 1781
t_end = 2021

ndraws = 1000000
nensemble = 10    

stat4file = 'CRUTEM/stat4.txt'

#------------------------------------------------------------------------------
# METHODS
#------------------------------------------------------------------------------

def make_timeseries( uncertainty, taper_start, taper_end ):
      
    t_taper = pd.date_range( start = str( taper_start ), end = str( taper_end ), freq='M')
    ts_taper = [ uncertainty / (len( t_taper ) - 1 ) * ( (len( t_taper ) - 1 ) - i ) for i in range( len( t_taper ) ) ]           
    da =  pd.DataFrame( {'datetime':t_taper, 'bias':ts_taper} )

    t_full = pd.date_range(start=str( t_start ), end=str( t_end ), freq='M')
    df_full = pd.DataFrame( {'datetime':t_full} )
    df = df_full.merge( da, how='left', on='datetime' )
    df.bias[ df.datetime <= str( taper_start ) ] = uncertainty
    df.bias[ df.datetime >= str( taper_end ) ] = 0.0

    return df.bias.values

def generate_ensemble_members( nensemble, uncertainty )

    # equiprobable binning
    
    random_numbers = np.random.normal(loc=0, scale=uncertainty, size=ndraws)
    bin_edges = np.linspace( -uncertainty, uncertainty, nensemble+1 )

    bias_ensemble = []
    for k in range(nensemble):    

        random_numbers_bin = [ i for i in random_numbers if i > bin_edges[k] and i < bin_edges[k+1] ]
        random_draw = np.random.randint(len(random_numbers_bin), size=1)[0]
        random_bias = random_numbers_bin[ random_draw ]

        bias_ensemble.append( random_bias )        

    return bias_ensemble

#------------------------------------------------------------------------------
# LOAD: stat4 file and extract headers, stationcodes and latitudes
#------------------------------------------------------------------------------

headerlist = []
stationcodelist = []
latlist = []
    
with open (stat4file, 'r', encoding="ISO-8859-1") as f:                      
    for line in f:   
        if len(line)>1: # ignore empty lines         
            if (len(line.strip().split())!=13) | (len(line.split()[0])>4): # header lines
                header = line
                code = line[0:6]                                                                
                lat = int(line[6:10]) / 10.0
                headerlist.append( header )
                stationcodelist.append( code )
                latlist.append( lat )                
            else:           
                continue                                     
        else:                
            continue
f.close

#------------------------------------------------------------------------------
# HadCRUT5 Exposure Bias Model
#------------------------------------------------------------------------------

# As in work by Brohan et al. [2006], the exposure bias
# model followed is that of Folland et al. [2001], which is
# derived from the results of Parker [1994]. For grid boxes in
# the latitude range of 20S–20N a 1s uncertainty of 0.2C is
# assumed prior to 1930. This then decreases linearly toward a
# value of zero in 1950. For stations that lie outside of 20S–
# 20N the exposure bias uncertainty takes a value of 0.1C
# prior to 1900, decreasing linearly to zero by 1930.
        
for e in range(nensemble):

    exposure_bias_file = 'exposure_bias_hadcrut5' + '_' + 'ensemble_member' + '_' + str(e+1).zfill(2) + '.txt'
    with open(exposure_bias_file,'w') as f:
        
        for k in range( len( stationcodelist ) ):
            
            station_header = headerlist[k]
    
            lat = latlist[k]
        
            if ( lat < -20 ) | ( lat > 20 ):
        
                taper_start = 1930
                taper_end = 1950
                uncertainty = 0.2
                bias_ensemble = generate_ensemble_members( nensemble, uncertainty )
                bias = bias_ensemble[e] # max bias bin
    
            else:
      
                taper_start = 1900
                taper_end = 1930
                uncertainty = 0.1
                bias_ensemble = generate_ensemble_members( nensemble, uncertainty )
                bias = bias_ensemble[e] # max bias bin
        
            ts = make_timeseries( bias, taper_start, taper_end )
        
            # EXTRACT: years and month data for CRUTEM format
        
            station_years = np.arange( t_start, t_end )    
            station_data = np.reshape( ts, [ len( station_years ), 12 ] )
              
            # WRITE: station header + yearly rows of monthly values in CRUTEM format x1000
    
            f.write(station_header)
            for i in range(len(station_years)):  
                rowstr = str(station_years[i])
                for j in range(12):
                    if np.isnan(station_data[i,:][j]):
                        monthstr = str(-999)
                    else:
                        monthstr = str( int( station_data[i,:][j]*1000 ) )
                    rowstr += f"{monthstr:>5}"          
                f.write(rowstr+'\n')                
    f.close
        
#------------------------------------------------------------------------------
print('** END')

    
