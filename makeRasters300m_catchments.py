import sys, arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
sys.path.append('D:/WorkFolder/WetConnect_Nov2016/Scripts')
from raster_function import catcsv2raster2
arcpy.env.compression = 'LZW'
import pandas as pd
import gc

year = '2011'
print year
wd = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/MapRasters/Catchments/'
wd2 = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/FinalTables/NHDCatTables/'
wd3 = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/SSWR1.1B/PredictionVisualizations/RasterTemplate/'
wd4 = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD' + year + '/FinalTables/'
inTemplate = wd3 + 'comid300m_clp.tif'

ct = pd.read_csv(wd4 + 'cat_region_maps_control_table.csv')
w_names = list(ct.VarName)

#w_types = ['All','Rip','NonRip']
w_types = ['Rip','NonRip']

#--------------------------------------------------------------------------------------------------------------------
for w_type in w_types:
    print '-----------'+w_type+'--------------'    
    outfolder = wd + w_type + '/'
    inCSV = wd2 + w_type + '/' + 'wetconnect_cat_summaries.csv'
    inTable = pd.read_csv(inCSV)
    ct[w_type+'_fin'] = 0
    run = ct[w_type]
    for j,i in enumerate(w_names):
        if run[j] == 1:    
            print i
            Value = i    
            outRas = outfolder + Value + '_300m.tif'
            if not arcpy.Exists(outRas):
                catcsv2raster2(inTable, Value, inTemplate, outRas, dtype='Float', idName='COMID')
            gc.collect()       
            ct[w_type+'_fin'].loc[j] = 1
            ct.to_csv(wd4 + 'cat_region_maps_control_table.csv', index=False)
#--------------------------------------------------------------------------------------------------------------------   

