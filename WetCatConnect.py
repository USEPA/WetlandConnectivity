
# Import arcpy module
import arcpy
import os
from arcpy.sa import *
from arcpy import env
arcpy.CheckOutExtension("spatial")
from datetime import datetime
import struct, decimal, itertools

arcpy.env.overwriteOutput = True

nhddir = 'L:/Priv/CORFiles/Geospatial_Library/Data/RESOURCE/PHYSICAL/HYDROLOGY/NHDPlusV21'
working_dir = 'D:/WorkFolder/WetConnect_Aug2016'
isolated_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/IsolatedWetlands'
watershed_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/WetCats'
frmto_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/Wetlands_NLCD2011/WetlandCat/FlowTables'

inputs = {'CA':['18'],'CO':['14','15'],'GB':['16'],'GL':['04'],'MA':['02'],'MS':['05','06','07','08','10L','10U','11'],
          'NE':['01'],'PN':['17'],'RG':['13'],'SA':['03N','03S','03W'],'SR':['09'],'TX':['12']}
          
for region in inputs.keys():
    for hydro in inputs[region]:
        print 'Region ' + region + ' and hydro number ' + hydro
        for dirs in os.listdir(nhddir + "/NHDPlus%s/NHDPlus%s"%(region, hydro)):
            if dirs.count("FdrFac") and not dirs.count('.txt') and not dirs.count('.7z'):
                rpu =  dirs[-3:]
                    # Check to see if wetland catchments exist already
                outDbf = frmto_dir + "/WetlandFrmTo" + rpu + ".dbf"
                if not os.path.exists(outDbf):
                        #-- Create garbage cans --
                    garbage = working_dir + '/ESRI_garbage/garbage_' + rpu
                    if not os.path.exists(garbage):
                        os.makedirs(garbage)
                    arcpy.env.workspace = garbage
                        #-- Delete garbage after run --
                    startTime = time.time()   
                    print "Shifting region: " + rpu
                    Wtshds = Raster(watershed_dir + '/WetlandCat_' + rpu + '.tif')     
                    shift1 = arcpy.Shift_management(Wtshds, "shift1.tif", "-30", "0", Wtshds)
                    shift2 = arcpy.Shift_management(Wtshds, "shift2.tif", "-30", "30", Wtshds)
                    shift4 = arcpy.Shift_management(Wtshds, "shift4.tif", "0", "30", Wtshds)
                    shift8 = arcpy.Shift_management(Wtshds, "shift8.tif", "30", "30", Wtshds)
                    shift16 = arcpy.Shift_management(Wtshds, "shift16.tif", "30", "0", Wtshds)
                    shift32 = arcpy.Shift_management(Wtshds, "shift32.tif", "30", "-30", Wtshds)
                    shift64 = arcpy.Shift_management(Wtshds, "shift64.tif", "0", "-30", Wtshds)
                    shift128 = arcpy.Shift_management(Wtshds, "shift128.tif", "-30", "-30", Wtshds)                   
                    
                        # Process: Raster Calculator                    
                    print 'Creating from-to connections'
                    fdr = Raster(nhddir +"/NHDPlus" +region + "/NHDPlus" + hydro + "/NHDPlusFdrFac"  + rpu + "/fdr")
                    flowto1 = ((shift1 != Wtshds) * (fdr == 1)) * shift1
                    flowto1.save("FlowTo1.tif")
                    flowto1 = Raster("FlowTo1.tif")
                    flowto1 = Con(IsNull(flowto1),0,flowto1)
                    
                    flowto2 = ((shift2 != Wtshds) * (fdr == 2)) * shift2
                    flowto2.save("FlowTo2.tif")
                    flowto2 = Raster("FlowTo2.tif")
                    flowto2 = Con(IsNull(flowto2),0,flowto2)
                    
                    flowto4 = ((shift4 != Wtshds) * (fdr == 4)) * shift4
                    flowto4.save("FlowTo4.tif")
                    flowto4 = Raster("FlowTo4.tif")
                    flowto4 = Con(IsNull(flowto4),0,flowto4)
                    
                    flowto8 = ((shift8 != Wtshds) * (fdr == 8)) * shift8
                    flowto8.save("FlowTo8.tif")
                    flowto8 = Raster("FlowTo8.tif")
                    flowto8 = Con(IsNull(flowto8),0,flowto8)
                    
                    flowto16 = ((shift16 != Wtshds) * (fdr == 16)) * shift16
                    flowto16.save("FlowTo16.tif")
                    flowto16 = Raster("FlowTo16.tif")
                    flowto16 = Con(IsNull(flowto16),0,flowto16)
                    
                    flowto32 = ((shift32 != Wtshds) * (fdr == 32)) * shift32
                    flowto32.save("FlowTo32.tif")
                    flowto32 = Raster("FlowTo32.tif")
                    flowto32 = Con(IsNull(flowto32),0,flowto32)
                    
                    flowto64 = ((shift64 != Wtshds) * (fdr == 64)) * shift64
                    flowto64.save("FlowTo64.tif")
                    flowto64 = Raster("FlowTo64.tif")
                    flowto64 = Con(IsNull(flowto64),0,flowto64)
                    
                    flowto128 = ((shift128 != Wtshds) * (fdr == 128)) * shift128
                    flowto128.save("FlowTo128.tif")
                    flowto128 = Raster("FlowTo128.tif")
                    flowto128 = Con(IsNull(flowto128),0,flowto128)
                    
                    FlowToSum = flowto1 + flowto2 + flowto4 + flowto8 + flowto16 + flowto32 + flowto64 + flowto128
                    FlowToSum.save("FlowToSum.tif")
                    FlowToSum = Raster("FlowToSum.tif")
                    FlowToFinal = Con(FlowToSum != 0, FlowToSum)
                    FlowToFinal.save("FlowToFinal.tif")
                    
                    outCombine = Combine([FlowToFinal, Wtshds])
                    outCombine.save(working_dir + "/ScratchDir/WetlandFrmTo" + rpu + ".tif")

                    if not arcpy.Exists(outDbf):
                        arcpy.CopyRows_management(outCombine, outDbf, "")
                    print "Total time to connect catchments in this region: " + str((time.time()-startTime) / 60.0) 
                    
                    try:
                        arcpy.Delete_management("FlowTo1.tif")
                        arcpy.Delete_management("FlowTo2.tif")
                        arcpy.Delete_management("FlowTo4.tif")
                        arcpy.Delete_management("FlowTo8.tif")
                        arcpy.Delete_management("FlowTo16.tif")
                        arcpy.Delete_management("FlowTo32.tif")
                        arcpy.Delete_management("FlowTo64.tif")
                        arcpy.Delete_management("FlowTo128.tif")
                        arcpy.Delete_management("shift1.tif")
                        arcpy.Delete_management("shift2.tif")
                        arcpy.Delete_management("shift4.tif")
                        arcpy.Delete_management("shift8.tif")
                        arcpy.Delete_management("shift16.tif")
                        arcpy.Delete_management("shift32.tif")
                        arcpy.Delete_management("shift64.tif")
                        arcpy.Delete_management("shift128.tif")
                        arcpy.Delete_management("FlowToSum.tif")
                        arcpy.Delete_management("FlowToFinal.tif")
                    except:
                        pass
















                    