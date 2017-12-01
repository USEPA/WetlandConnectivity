import sys, arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
sys.path.append(r'J:\GitProjects\Wetland Connectivity\WetlandScripts')
from raster_function import catcsv2raster2
import pandas as pd
import numpy as np
import gc

year = '2011'
print '------------' + year + '------------'
wd = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/MapRasters/Wetlands/'
wd2 = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/AllWetlands/'
wd3 = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/FinalTables/'

inCSV = wd3 + 'WetConnectMetrics_'+year+'.csv'
inTable = pd.read_csv(inCSV)
#inTable['WET_ID'] = inTable['WetId'].str.split('_').str[0]
inTable['WET_ID'] = inTable['WetId'].astype(int)
inTable['DrainArea_WetArea'] = inTable['DrainAreaSqKm'] / inTable['WetAreaSqKm']

#Set classes to numbers for raster conversion
#Type classes
inTable.loc[inTable['Type']=='Riparian','Type'] = 1
inTable.loc[inTable['Type']=='Shallow','Type'] = 2
inTable.loc[inTable['Type']=='Overland','Type'] = 3
inTable.loc[inTable['Type']=='ShallowDeep','Type'] = 4
#Drainage classes
inTable.loc[inTable['FreqSh']=='VALUE_0','FreqSh'] = np.nan
inTable.loc[inTable['FreqSh']=='VALUE_1','FreqSh'] = 0
inTable.loc[inTable['FreqSh']=='VALUE_2','FreqSh'] = 1
inTable.loc[inTable['FreqSh']=='VALUE_3','FreqSh'] = 2

inTemplate = wd2 + 'WetlandsRgnGrp_300m.tif'

ct = pd.read_csv(wd3 + 'wetland_maps_control_table.csv')
w_names = ct.VarName

w_types = ['All']

#--------------------------------------------------------------------------------------------------------------------   
for w_type in w_types:
    print '-----------'+w_type+'--------------'   
    outfolder = wd + w_type + '/'
    run = ct[w_type]
    for j,i in enumerate(w_names):
        if run[j] == 1:
            print i
            Value = i
            outRas = outfolder + Value + '_300m.tif'
            if not arcpy.Exists(outRas):
                catcsv2raster2(inTable, Value, inTemplate, outRas, dtype='Float', idName='WetId')
            gc.collect()                
#--------------------------------------------------------------------------------------------------------------------   






