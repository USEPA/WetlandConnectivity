import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")

import os
import time

path_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/StreamCat/LandscapeRasters/QAComplete/WaterMask/'
out_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/FlowLengthsDown/'

files = filter(lambda x: x.endswith(('.tif')) and x.count(('FDRNull')), os.listdir(path_dir))

for fdrnull in files:
    start_time = time.time() 
    print 'Processing: ' + fdrnull 
    outRas = out_dir+'fldown_'+fdrnull[18:]
    
    outFlowLength = FlowLength(path_dir+fdrnull, 'DOWNSTREAM','')
    outFlowLength.save(outRas)
    print("Duration: --- %s seconds ---" % (time.time() - start_time))
    
