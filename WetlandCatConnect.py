
# Import arcpy module
import arcpy
import os
from arcpy.sa import *
from datetime import datetime
import struct, decimal, itertools
import pysal as ps
import pandas as pd
import numpy as np
from collections import deque, defaultdict
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")


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
        pandasDF.columns = pandasDF.columns.str.upper()              
    return pandasDF

nhddir = "D:/GISData/NHDPlusV21"
working_dir = 'D:/WorkFolder/WetConnect_Aug2016'
arcpy.env.workspace = working_dir


inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}
          
for region in inputs.keys():
    for hydro in inputs[region]:
        print 'on region ' + region + ' and hydro number ' + hydro
        for dirs in os.listdir(nhddir + "/NHDPlus%s/NHDPlus%s"%(region, hydro)):
            if dirs.count("FdrFac") and not dirs.count('.txt') and not dirs.count('.7z'):
                print dirs
                print dirs[-3:]
                # Make fdr access loopable 
                nhd_fdr = Raster(nhddir +"/NHDPlus" +region + "/NHDPlus" + hydro + "/NHDPlusFdrFac"  + dirs[-3:] + "/fdr")
                
                arcpy.env.snapRaster = nhd_fdr
                arcpy.env.cellSize = "30"
                arcpy.env.mask = nhd_fdr
                arcpy.env.extent = nhd_fdr
                
                if not arcpy.Exists(working_dir+'/WetlandCat'+'/WetlandWs' + dirs[-3:] + '.tif'):
                    # Generate wetland watersheds
                    outWtshd = Watershed(nhd_fdr, working_dir+'/Wetlands' + dirs[-3:] + '.tif', "VALUE")

                    # Save watershed
                    outWtshd.save(working_dir+'/WetlandWs' + dirs[-3:] + '.tif')

#                Wtshds = Raster(working_dir+'/WetlandWs' + dirs[-3:] + '.tif')

                startTime = datetime.now()
                
                shift1 = arcpy.Shift_management(Wtshds, lclWet+"shift1.tif", "-30", "0", Wtshds)
                shift2 = arcpy.Shift_management(Wtshds, lclWet+"shift2.tif", "-30", "30", Wtshds)
                shift4 = arcpy.Shift_management(Wtshds, lclWet+"shift4.tif", "0", "30", Wtshds)
                shift8 = arcpy.Shift_management(Wtshds, lclWet+"shift8.tif", "30", "30", Wtshds)
                shift16 = arcpy.Shift_management(Wtshds, lclWet+"shift16.tif", "30", "0", Wtshds)
                shift32 = arcpy.Shift_management(Wtshds, lclWet+"shift32.tif", "30", "-30", Wtshds)
                shift64 = arcpy.Shift_management(Wtshds, lclWet+"shift64.tif", "0", "-30", Wtshds)
                shift128 = arcpy.Shift_management(Wtshds, lclWet+"shift128.tif", "-30", "-30", Wtshds)
                
                print "total elapsed time to shift: " + str(datetime.now()-startTime)
                
                # Process: Raster Calculator
                print 'running raster calculator on shifts'
                flowto1 = ((shift1 != Wtshds) * (nhd_fdr == 1)) * shift1
                flowto1.save(lclWet+"FlowTo1.tif")
                flowto1 = Raster(lclWet+"FlowTo1.tif")
                flowto1 = Con(IsNull(flowto1),0,flowto1)
                
                flowto2 = ((shift2 != Wtshds) * (nhd_fdr == 2)) * shift2
                flowto2.save(lclWet+"FlowTo2.tif")
                flowto2 = Raster(lclWet+"FlowTo2.tif")
                flowto2 = Con(IsNull(flowto2),0,flowto2)
                
                flowto4 = ((shift4 != Wtshds) * (nhd_fdr == 4)) * shift4
                flowto4.save(lclWet+"FlowTo4.tif")
                flowto4 = Raster(lclWet+"FlowTo4.tif")
                flowto4 = Con(IsNull(flowto4),0,flowto4)
                
                flowto8 = ((shift8 != Wtshds) * (nhd_fdr == 8)) * shift8
                flowto8.save(lclWet+"FlowTo8.tif")
                flowto8 = Raster(lclWet+"FlowTo8.tif")
                flowto8 = Con(IsNull(flowto8),0,flowto8)
                
                flowto16 = ((shift16 != Wtshds) * (nhd_fdr == 16)) * shift16
                flowto16.save(lclWet+"FlowTo16.tif")
                flowto16 = Raster(lclWet+"FlowTo16.tif")
                flowto16 = Con(IsNull(flowto16),0,flowto16)
                
                flowto32 = ((shift32 != Wtshds) * (nhd_fdr == 32)) * shift32
                flowto32.save(lclWet+"FlowTo32.tif")
                flowto32 = Raster(lclWet+"FlowTo32.tif")
                flowto32 = Con(IsNull(flowto32),0,flowto32)
                
                flowto64 = ((shift64 != Wtshds) * (nhd_fdr == 64)) * shift64
                flowto64.save(lclWet+"FlowTo64.tif")
                flowto64 = Raster(lclWet+"FlowTo64.tif")
                flowto64 = Con(IsNull(flowto64),0,flowto64)
                
                flowto128 = ((shift128 != Wtshds) * (nhd_fdr == 128)) * shift128
                flowto128.save(lclWet+"FlowTo128.tif")
                flowto128 = Raster(lclWet+"FlowTo128.tif")
                flowto128 = Con(IsNull(flowto128),0,flowto128)
                
                FlowToSum = flowto1 + flowto2 + flowto4 + flowto8 + flowto16 + flowto32 + flowto64 + flowto128
                FlowToSum.save(lclWet+"FlowToSum.tif")
                FlowToFinal = Con(FlowToSum != 0, FlowToSum)
                FlowToFinal.save(lclWet+"FlowToFinal.tif")
                
                outCombine = Combine([FlowToFinal, Wtshds])
                outCombine.save(lclWet+"WetlandWsFrmTo17C.tif")
                
                outDbf = lclWet+"WetlandWsFrmTo17C.dbf"
                if not arcpy.Exists(outDbf):
                    arcpy.CopyRows_management(outCombine, outDbf, "")
                print "total elapsed time to query and build from-to table: " + str(datetime.now()-startTime)
                
                
                # Generate the Full Flows Downstream from a wetland
                flow = dbf2DF(outDbf)[['WETLANDWS', 'FLOWTOFINA']]
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





