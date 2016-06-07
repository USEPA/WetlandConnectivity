#--------------------------------------------------------
# Name: LakeConnect.py
# Purpose: creates shifted lake basin rasters in each of the
#          flow direction raster directions in order to run
#          raster calculator and create a 'flow table' of
#          from-to flow for nested watersheds to use in
#          accumulation script
#
# Author: Ryan Hill with modifications by Marc Weber
# Created 10/24/2014
# ArcGIS Version:  10.2.1
# Python Version:  2.7
#--------------------------------------------------------

# Import arcpy module
import os, sys, arcpy
from arcpy.sa import *
from datetime import datetime
import struct, decimal, itertools
import pysal as ps
import pandas as pd
import numpy as np
from collections import deque, defaultdict

def children(token, tree, chkset=None):
    visited = set()
    to_crawl = deque([token])
    while to_crawl:
        current = to_crawl.popleft()
        if current in visited:
            continue
        visited.add(current)
        node_children = set(tree[current])
        to_crawl.extendleft(node_children - visited)
    #visited.remove(token)
    if chkset != None:
        visited = visited.intersection(chkset)
    return list(visited)

def dbf2DF(dbfile, upper=True):
    db = ps.open(dbfile)
    cols = {col: db.by_col(col) for col in db.header}
    db.close()  #Close dbf 
    pandasDF = pd.DataFrame(cols)
    if upper == True:
        pandasDF.columns = map(str.upper, pandasDF.columns.values) 
    return pandasDF


# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.env.workspace = "C:/users/mweber/temp"

# Set overwrite = T
arcpy.env.overwriteOutput = True
# Loop through each region to process
inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}
for regions in inputs.keys():
    for hydro in inputs[regions]:
        print 'on region ' + regions + ' and hydro number ' + hydro
        nhddir = "H://NHDPlusV21/NHDPlus%s/NHDPlus%s"%(regions, hydro)
        for dirs in os.listdir(nhddir):
            if dirs.count("FdrFac") and not dirs.count('.txt') and not dirs.count('.7z'):
                print dirs
                if not arcpy.Exists("L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/FlowTables/WetlandFrmTo" + dirs[-3:] + ".dbf"):
                    fdr = Raster(nhddir + "/NHDPlusFdrFac"  + dirs[-3:] + "/fdr")
                    Paths = Raster('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/Data/StreamLink' + dirs[-3:] + '.tif')
                    
                    Paths = Con(IsNull(Paths), 0, Paths)
                    arcpy.env.snapRaster = fdr
                    arcpy.env.cellSize = "30"
                    arcpy.env.mask = fdr
                    arcpy.env.extent = fdr
                    
                    startTime = datetime.now()
                    # Process: Shift
                    print 'shifting'
                    
                    shift1 = arcpy.Shift_management(Paths, "shift1", "-30", "0", fdr)
                    shift2 = arcpy.Shift_management(Paths, "shift2", "-30", "30", Paths)
                    shift4 = arcpy.Shift_management(Paths, "shift4", "0", "30", Paths)
                    shift8 = arcpy.Shift_management(Paths, "shift8", "30", "30", Paths)
                    shift16 = arcpy.Shift_management(Paths, "shift16", "30", "0", Paths)
                    shift32 = arcpy.Shift_management(Paths, "shift32", "30", "-30", Paths)
                    shift64 = arcpy.Shift_management(Paths, "shift64", "0", "-30", Paths)
                    shift128 = arcpy.Shift_management(Paths, "shift128", "-30", "-30", Paths)
                    
                    
                    
                    # Process: Raster Calculator
                    print 'running raster calculator on shifts'
                    flowto1 = ((shift1 != Paths) * (fdr == 1)) * shift1
                    flowto1.save("C:/Users/mweber/Temp/FlowTo1.tif")
                    flowto1 = Raster("C:/Users/mweber/Temp/FlowTo1.tif")
                    flowto1 = Con(IsNull(flowto1),0,flowto1)
                    
                    flowto2 = ((shift2 != Paths) * (fdr == 2)) * shift2
                    flowto2.save("C:/Users/mweber/Temp/FlowTo2.tif")
                    flowto2 = Raster("C:/Users/mweber/Temp/FlowTo2.tif")
                    flowto2 = Con(IsNull(flowto2),0,flowto2)
                    
                    flowto4 = ((shift4 != Paths) * (fdr == 4)) * shift4
                    flowto4.save("C:/Users/mweber/Temp/FlowTo4.tif")
                    flowto4 = Raster("C:/Users/mweber/Temp/FlowTo4.tif")
                    flowto4 = Con(IsNull(flowto4),0,flowto4)
                    
                    flowto8 = ((shift8 != Paths) * (fdr == 8)) * shift8
                    flowto8.save("C:/Users/mweber/Temp/FlowTo8.tif")
                    flowto8 = Raster("C:/Users/mweber/Temp/FlowTo8.tif")
                    flowto8 = Con(IsNull(flowto8),0,flowto8)
                    
                    flowto16 = ((shift16 != Paths) * (fdr == 16)) * shift16
                    flowto16.save("C:/Users/mweber/Temp/FlowTo16.tif")
                    flowto16 = Raster("C:/Users/mweber/Temp/FlowTo16.tif")
                    flowto16 = Con(IsNull(flowto16),0,flowto16)
                    
                    flowto32 = ((shift32 != Paths) * (fdr == 32)) * shift32
                    flowto32.save("C:/Users/mweber/Temp/FlowTo32.tif")
                    flowto32 = Raster("C:/Users/mweber/Temp/FlowTo32.tif")
                    flowto32 = Con(IsNull(flowto32),0,flowto32)
                    
                    flowto64 = ((shift64 != Paths) * (fdr == 64)) * shift64
                    flowto64.save("C:/Users/mweber/Temp/FlowTo64.tif")
                    flowto64 = Raster("C:/Users/mweber/Temp/FlowTo64.tif")
                    flowto64 = Con(IsNull(flowto64),0,flowto64)
                    
                    flowto128 = ((shift128 != Paths) * (fdr == 128)) * shift128
                    flowto128.save("C:/Users/mweber/Temp/FlowTo128.tif")
                    flowto128 = Raster("C:/Users/mweber/Temp/FlowTo128.tif")
                    flowto128 = Con(IsNull(flowto128),0,flowto128)
                    
                    
                    
                    FlowToSum = flowto1 + flowto2 + flowto4 + flowto8 + flowto16 + flowto32 + flowto64 + flowto128
                    FlowToSum.save("C:/Users/mweber/Temp/FlowToSum.tif")
                    FlowToSum = Raster("C:/Users/mweber/Temp/FlowToSum.tif")
                    FlowToFinal = Con(FlowToSum != 0, FlowToSum)
                    FlowToFinal.save("C:/Users/mweber/Temp/FlowToFinal.tif")
                    
                    outCombine = Combine([FlowToFinal, Paths])
                    outCombine.save("L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/FlowTables/WetlandFrmTo" + dirs[-3:] + ".tif")
                    #rasterList = arcpy.ListRasters("*", "")
                    #for raster in rasterList:
                    #    arcpy.Delete_management(raster)
                    outDbf = "L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/FlowTables/WetlandFrmTo" + dirs[-3:] + ".dbf"
                    if not arcpy.Exists(outDbf):
                        arcpy.CopyRows_management(outCombine, outDbf, "")
                    

                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo1.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo2.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo4.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo8.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo16.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo32.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo64.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowTo128.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowToSum.tif")
                    arcpy.Delete_management("C:/Users/mweber/Temp/FlowToFinal.tif")
                                
                     # Generate the Full Flows Downstream from a wetland
                    
                    flow = dbf2DF(outDbf)[['IFTHE_RAS9', 'FLOWTOFINA']]
                    flow.head()
                    flow  = flow[flow.IFTHE_RAS9 != 0]
                    
                    fromID = np.array(flow.IFTHE_RAS9)
                    toID = np.array(flow.FLOWTOFINA)
                    DownIDs = defaultdict(list)
                    for i in range(0, len(flow), 1):
                        FROMID = fromID[i]
                        TOID = toID[i]
                        DownIDs[FROMID].append(TOID)
                                  
                    FullIDs = dict()
                    for key in DownIDs.keys():
                        FullIDs[key] = children(key, DownIDs)
    
                    
                    print "total elapsed time " + str(datetime.now()-startTime)