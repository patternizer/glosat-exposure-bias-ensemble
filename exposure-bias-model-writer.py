#------------------------------------------------------------------------------
# PROGRAM: exposure-bias-model-writer.py
#------------------------------------------------------------------------------
# Version 0.1
# 4 May, 2022
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
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

t_start = 1781
t_end = 2021

stat4file = 'CRUTEM/stat4.txt'
exposure_bias_model_file = 'OUT/df_exposure_bias.pkl'
exposure_bias_file = 'OUT/exposure_bias_model.txt'

#------------------------------------------------------------------------------
# METHODS
#------------------------------------------------------------------------------

def make_timeseries( da ):
      
    t_full = pd.date_range(start=str( t_start ), end=str( t_end ), freq='M')
    df_full = pd.DataFrame( {'datetime':t_full} )
    db = df_full.merge( da, how='left', on='datetime' )

    return db

#------------------------------------------------------------------------------
# LOAD: exposure bias model .pkl file
#------------------------------------------------------------------------------

df = pd.read_pickle( exposure_bias_model_file, compression='bz2' )
stationcodes = df.stationcode.unique()

#------------------------------------------------------------------------------
# LOAD: CRUTEM5 stat4 file and extract headers and stationcodes
#------------------------------------------------------------------------------

headerlist = []
stationcodelist = []
    
with open (stat4file, 'r', encoding="ISO-8859-1") as f:                      
    for line in f:   
        if len(line)>1: # ignore empty lines         
            if (len(line.strip().split())!=13) | (len(line.split()[0])>4): # header lines
                header = line
                code = line[0:6]                                                                
                headerlist.append( header )
                stationcodelist.append( code )
            else:           
                continue                                     
        else:                
            continue
f.close

#------------------------------------------------------------------------------
# WRITE: exposure bias model estimates per station in CRUTEM format
#------------------------------------------------------------------------------
'''
exposure bias is in scaled integer format --> bias x1000
fill values = -999
'''   

with open( exposure_bias_file, 'w' ) as f:
    
    for k in range( len( stationcodelist ) ):
        
        station_header = headerlist[k]
        station_years = np.arange( t_start, t_end )    

        idx = [i for i in range(len(stationcodes)) if stationcodes[i] == stationcodelist[k] ]
        if len(idx) > 0:
            da = df[ df.stationcode == stationcodes[idx[0]] ].reset_index(drop=True)
            da.datetime = pd.date_range(start=str(da.datetime.loc[0].year), periods=len(da), freq='M')
            db = make_timeseries( da )        
            ts = db.bias.values
        else:
            ts = np.array( [np.nan]*(len(station_years)*12) ).ravel()
    
        # EXTRACT: years and month data for CRUTEM format
    
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

        if k % 1000 == 0:
            print(k)
   
f.close
        
#------------------------------------------------------------------------------
print('** END')




    
