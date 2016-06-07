#--------------------------------------------------------
# Name: FlowPath.py
# Purpose: Generate flow paths from individual
#          Wetland groups based on NLCD==90 or 95 cells
#          to nearest stream cells and generate zonal
#          statistics of underlying features along flow paths
# Author: Marc Weber
# Created 4/5/2016
# Python Version:  2.7

# Import arcpy module
import arcpy
import os
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
from arcpy import env
import geopandas as gp
import pandas as pd
from datetime import datetime

# Set variables
watermask_dir = "J:/Watershed Integrity Spatial Prediction/WaterMask"
working_dir = "J:/GitProjects/Wetland Connectivity/SpatialData"
nlcd = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/StreamCat/LandscapeRasters/QAComplete/nlcd2006.tif'
temp = 'C:/users/mweber/temp'
nhddir = "H:/NHDPlusV21"
working_gdb = temp + "/Working.gdb"
# Define the NHDPlus hydro-regions toLoop through and process as a dictionary
inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}
          
for region in inputs.keys():
    for hydro in inputs[region]:
        print 'on region ' + region + ' and hydro number ' + hydro
        for dirs in os.listdir(nhddir + "/NHDPlus%s/NHDPlus%s"%(region, hydro)):
            if dirs.count("FdrFac") and not dirs.count('.txt') and not dirs.count('.7z'):
                if not arcpy.Exists(working_dir + "/StreamLink" + dirs[-3:] + ".tif"):
                    print dirs
                    print dirs[-3:]
                    flowgrid = Raster("J:/Watershed Integrity Spatial Prediction/Spatial Data/line100mbuffer/flowgrid"+ hydro) # gridded NHDPlus flowlines
                    watermask = Raster(watermask_dir + "/WaterMask_" + dirs[-3:] + ".tif") # NLCD water cells that are contiguous to NHDPlus streams
                    fdr = Raster(nhddir +"/NHDPlus" +region + "/NHDPlus" + hydro + "/NHDPlusFdrFac"  + dirs[-3:] + "/fdr")
    
                    arcpy.env.snapRaster = fdr
                    arcpy.env.cellSize = "30"
                    arcpy.env.mask = fdr
                    arcpy.env.extent = fdr
    
                    # combine gridded NHDPlus flowlines with watermask
                    flowgrid = Con(IsNull(flowgrid),0,flowgrid)
                    watermask = Con(IsNull(watermask),0,watermask)
                    FullStreams = flowgrid+watermask
                    FullStreams = Con(FullStreams > 0,1,)
                    if not arcpy.Exists(working_dir + "/FullStreams" + dirs[-3:] + ".tif"):
                        FullStreams.save(working_dir + "/FullStreams" + dirs[-3:] + ".tif")
                    
                    # Derive NLCD based wetlands
                    NLCD = Raster(nlcd)
                    wetlands = Con((NLCD == 90) | (NLCD == 95), 1,)
                    if not arcpy.Exists(temp + "/Wetlands" + dirs[-3:] + ".tif"):
                        wetlands.save(temp + "/Wetlands" + dirs[-3:] + ".tif")
                    
                    # We only want wetland cells that aren't also water cells AND aren't adjacent to streams
                    # We'll just use our full buffer to cut back the wetland  raster
                    wetlands = Raster(temp + "/Wetlands" + dirs[-3:] + ".tif")
                    FullStreams = Raster(working_dir + "/FullStreams" + dirs[-3:] + ".tif")
                    outCon1 = Con(IsNull(FullStreams), 0,)
                    outCon2 = wetlands + outCon1
                    if not arcpy.Exists(temp + "/Wetlands" + dirs[-3:] + "v2.tif"):
                        outCon2.save(temp + "/Wetlands" + dirs[-3:] + "v2.tif")
                    
                    # Now create unique wetland groups of contiguous wetland cells
                    Wetlands = Raster(temp + "/Wetlands" + dirs[-3:] + "v2.tif")
                    WetlandRegions = RegionGroup(Wetlands, "EIGHT", "WITHIN", "NO_LINK", "")
                    if not arcpy.Exists(working_dir + "/Wetlands" + dirs[-3:] + ".tif"):
                        WetlandRegions.save(working_dir + "/Wetlands" + dirs[-3:] + ".tif")                    
                    # Raster to points
                    outPoint = temp + "/RasterPoints" + dirs[-3:] + ".shp"
                    # Execute RasterToPoint
                    WetlandRegions = working_dir + "/Wetlands" + dirs[-3:] + ".tif"
                    if not arcpy.Exists(outPoint):
                        arcpy.RasterToPoint_conversion(WetlandRegions, outPoint, "VALUE")
                    
                    # Execute ExtractValuesToPoints to get flow accumulation for each wetland region grid point
                    fac = nhddir +"/NHDPlus" +region + "/NHDPlus" + hydro + "/NHDPlusFdrFac"  + dirs[-3:] + "/fac"
                    outPointFac = temp + "/PointFac" + dirs[-3:] +  ".shp"
                    if not arcpy.Exists(outPointFac):
                        ExtractValuesToPoints(outPoint, fac, outPointFac,"", "ALL")
                    
                    # Process: Make Feature Layer
                    arcpy.MakeFeatureLayer_management(outPointFac, "FacPoints")
                    
                    # Process: Make Feature Layer
                    BoundaryUnits = nhddir + "/NHDPlusGlobalData/BoundaryUnit.shp"
                    arcpy.MakeFeatureLayer_management(BoundaryUnits, "BoundaryUnit", "\"UnitID\" = '%s'"%(dirs[-3:]))
                    
                    # Process: Select Layer By Location
                    arcpy.SelectLayerByLocation_management("FacPoints", "INTERSECT", "BoundaryUnit", "", "NEW_SELECTION")
                    
                    # Process: Feature Class To Shapefile (multiple)
                    arcpy.FeatureClassToShapefile_conversion("FacPoints", temp)
                    
                    # Use Pandas to get the minimum flow distance point for each wetland region group ID
                    WetPoints = gp.GeoDataFrame.from_file(temp + "/FacPoints.shp")
                    # First we'll drop all the -999 sites - these are wetland grid cells in the stream
                    WetPoints = WetPoints.loc[WetPoints.RASTERVALU!=-9999]
                    # Now we'll group points by wetland region group minimum flow distance
                    WetPoints = WetPoints.loc[WetPoints.groupby("GRID_CODE")["RASTERVALU"].idxmax()]
                    # And then we'll export to a text file after grabbing coordinates as fields we add
                    df = WetPoints.drop('geometry', axis=1)  # df is a DataFrame, not GeoDataFrame after the drop
                    def getXY(pt):
                        return (pt.x, pt.y)
                    centroidseries = WetPoints['geometry'].centroid
                    x,y = [list(t) for t in zip(*map(getXY, centroidseries))]
                    WetPoints['XCOORD'] = x
                    WetPoints['YCOORD'] = y
                    if not arcpy.Exists(working_dir + "/WetlandPoints" + dirs[-3:] +".shp"):
                        WetPoints.to_file(working_dir + "/WetlandPoints" + dirs[-3:]+ ".shp", driver = 'ESRI Shapefile')  
                    df['XCOORD'] = x
                    df['YCOORD'] = y
                    df.head()
                    #df[x] = WetPoints.geometry.apply(lambda p: p.x)
                    #df[y] = WetPoints.geometry.apply(lambda p: p.y)
                    df.to_csv(working_dir +"/WetlandPoints" + dirs[-3:] + ".csv")
                      
                    df = pd.read_csv(working_dir +"/WetlandPoints" + dirs[-3:] + ".csv") 
                            
                    WetPoints = working_dir + "/WetlandPoints" + dirs[-3:] + ".shp"   
                    arcpy.Delete_management(outPoint)
                    arcpy.Delete_management("FacPoints")
                    arcpy.Delete_management(temp + "/FacPoints.shp")
                    # Create Full cost path raster - first, we'll geneerate our own custom 'fdrnull' grid to pass to cost path tool
                    outfdr1 = Con(IsNull(FullStreams),0, 99)
                    outfdr2 = Con(outfdr1<>99, fdr,)
                    if not arcpy.Exists(working_dir + "/FullStreamsFDRNull" + dirs[-3:] + ".tif"):
                        outfdr2.save(working_dir + "/FullStreamsFDRNull" + dirs[-3:] + ".tif")
                    fdrnull = working_dir + "/FullStreamsFDRNull" + dirs[-3:] + ".tif"
                    if not arcpy.Exists(temp + "/CostPath.tif"):
                        arcpy.gp.CostPath_sa(WetPoints, nhddir + "/NHDPlus" + region + "/NHDPlus" + hydro + "/NHDPlusHydrodem" + dirs[-3:] + "/hydrodem", 
                                             fdrnull, temp + "/CostPath.tif", "EACH_CELL", "GRID_CODE")
                    
                    outCostPath = Raster(temp + "/CostPath.tif")
                    outCostPath = Con(outCostPath<>0,outCostPath,)
    
                    # Run stream link on the cost path to 'uniqueify' the sections
                    # Execute StreamLink
                    outStreamLink = StreamLink(outCostPath, fdr)
                    # Save the output 
                    outStreamLink.save(temp + "/StreamLink.tif")
                    
                    # Raster to polyline to get splits along path excatly right
                    arcpy.RasterToPolyline_conversion(in_raster=temp + "/StreamLink.tif", out_polyline_features=working_gdb + "/StreamLink", 
                                                      background_value="NODATA", minimum_dangle_length="0", simplify="SIMPLIFY", raster_field="VALUE")
                    
                    # Split the polylines at wetland points
                    arcpy.SplitLineAtPoint_management(in_features=working_gdb + "/StreamLink", point_features = working_dir + "/WetlandPoints" + dirs[-3:] + ".shp", 
                                                      out_feature_class = working_gdb + "/StreamLinkSplit", search_radius="90 Meters")
                    
                    # Now convert polylines back to a raster
                    arcpy.PolylineToRaster_conversion(in_features = working_gdb + "/StreamLinkSplit", value_field="OBJECTID",
                                                      out_rasterdataset=temp + "/StreamLinkSplit.tif", 
                                                      cell_assignment="MAXIMUM_LENGTH", priority_field="NONE", cellsize="30")
                                       
                    EucAlloc = EucAllocation(temp + "/StreamLinkSplit.tif", "30", "", "30", "Value", "", "")
                    
                    # Create dummy StreamLink with every value a 1
                    PathTemplate = Raster(temp + "/StreamLink.tif")
                    PathTemplate = Con(PathTemplate> 0,1,)
#                    EucAlloc = Raster(temp + '/StreamLink_EucAlloc.tif')
                    
                    Adjusted = EucAlloc * PathTemplate
                    
                    Adjusted.save(working_dir + "/StreamLink" + dirs[-3:] + ".tif")                    
                    
                    try:
                        arcpy.Delete_management(outCon1)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(outCon2)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(wetlands)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(temp + "/StreamLink.tif")
                    except:
                        pass
                    try:
                        arcpy.Delete_management(Wetlands)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(temp + "/CostPath.tif")
                    except:
                        pass
                    try:
                        arcpy.Delete_management("FacPoints")
                    except:
                        pass
                    try:
                        arcpy.Delete_management("FacPoints")
                    except:
                        pass
                    try:
                        arcpy.Delete_management(temp + "/StreamLinkSplit.tif")
                    except:
                        pass
                    try:
                        arcpy.Delete_management(temp + "/FacPoints.shp")
                    except:
                        pass
                    try:
                        arcpy.Delete_management(outCostPath)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(temp + "/CostPath.tif")
                    except:
                        pass
                    try:
                        arcpy.Delete_management(outStreamLink)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(working_gdb + "/StreamLink")
                    except:
                        pass
                    try:
                        arcpy.Delete_management(outPointFac)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(PathTemplate)
                    except:
                        pass
                    try:
                        arcpy.Delete_management(EucAlloc)
                    except:
                        pass


  