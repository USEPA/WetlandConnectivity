# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------
# HL7 SnowadjSurp.py
# Created on: 2015-02-25
# Last edited on: 2015-05-27
# Created by: Chas Jones
#
# Note: This program is a work in progress and likely has bugs that have not been fixed.
#
# Description: This program calculates the moisture indices and all Hydrologic
# Landscape intermediate steps based upon Winter (2001), Wolock (2004),
# Wigington (2013), and Leibowitz (2014). This program was translated into
# Python from from Randy Comeleo's .aml files that calculated the same outputs.
#
# VARIABLES INCLUDE:    Region abbreviation
#                       State abbreviations
#                       Base directory location (for GDBs created by script)
#                       Path to original Prism *.txt files (should all be unzipped into one folder)
#                       Path to projection file for spatial reference of choice
# ---------------------------------------------------------------------------
"""
# Import necessary modules
import os, arcpy, datetime
from datetime import date
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput  = True

##################
##
## Step 1: Open mxd
##
print "Start time: %s\n"%(datetime.datetime.now())

yearnum  = date.today().year
monthnum = date.today().month
daynum   = date.today().day

basepath    = r'L:\Priv\CORFiles\Geospatial_Library\Data\Project\WetlandConnectivity'
mxdfolder   = r'%s\mxd' %(basepath)


arcpy.env.parallelProcessingFactor  = "10%"
arcpy.env.workspace         = basepath
Scratch = r'L:\Priv\CORFiles\Geospatial_Library\Data\Project\WetlandConnectivity\Scratch'
arcpy.env.scratchWorkspace  = Scratch
outputCoordinateSystem      = arcpy.SpatialReference("D:\DArcGIS\Data\Projections\NAD_1983_Contiguous_USA_Albers.prj")
############################################

# THESE LISTS WILL LOOP OVER ALL WETLAND CONNECTIVITY RASTERS
YearList        = ['2001','2011']
AnalysisList    = ['Wetlands','Catchments','TinerNARSRegions','Examples']
DataTypeList    = ['Riparian', 'NonRiparian','AllWetlands']
ClassTypeList   = ['','class_byarea','class_bycount']


# ONLY RAN THESE COMBINATIONS BECAUSE THESE RASTERS WERE COMPLETED AND PLACED ON SERVER
YearList        = ['2001']
AnalysisList    = ['Wetlands','TinerNARSRegions']
DataTypeList    = ['NonRiparian','AllWetlands']
AnalysisList    = ['Wetlands','Examples']
AnalysisList    = ['Examples',]

DataTypeList    = ['AllWetlands']
ClassTypeList   = ['',]

for yearstr in YearList:
    for AnalysArea in AnalysisList:
        # TINER WETLAND REGION ANALYSES WERE AT 900M RESOLUTION
        if AnalysArea == 'TinerNARSRegions':
            Resolution = '900m'
        elif AnalysArea == 'Examples':
            Resolution = '30m'
        # ALL OTHERS WERE AT 300M RESOLUTION
        else:
            Resolution = '300m'
        for DataType in DataTypeList:
            InFolder = r'L:\Priv\CORFiles\Geospatial_Library\Data\Project\WetlandConnectivity\SpatialDataInputs\Wetlands_NLCD%s\MapRasters\%s' %(yearstr,AnalysArea)
            if DataType == 'AllWetlands':
                DTfoldername = 'All'
            elif DataType == 'NonRiparian':
                DTfoldername = 'NonRip'
            elif DataType == 'Riparian':
                DTfoldername = 'Rip'

            for ClassType in ClassTypeList:
                # Obtain list of tif files in the InSubFolder
                if AnalysArea == 'TinerNARSRegions' and not ClassType == '':
                    InSubFolder = '%s\\%s\\%s'      %(InFolder, DTfoldername,ClassType)
                elif AnalysArea == 'Examples':
                    InSubFolder = 'L:\Priv\CORFiles\Geospatial_Library\Data\Project\WetlandConnectivity\SpatialDataInputs\ExampleLocations'

                else:
                    InSubFolder = '%s\\%s'           %(InFolder, DTfoldername)

                RasterList  = filter(lambda x: x.endswith(('.tif')) , os.listdir(InSubFolder))

                # Cycle through each tif file IN THE SUBFOLDER
                for InRasterName in RasterList:
                    InRaster = InRasterName.rstrip('_%s.tif' %(Resolution))

                    # By default title text will read 'Error', unless caught and replaced by another name
                    titletext = 'Error'
                    # Get map title based on input raster name
                    if InRaster == 'type':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Flow Type'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'AllWetlands':
                                titletext =  'Dominant Flow Type'
                            elif DataType == 'NonRiparian':
                                titletext =  'Dominant Non-Riparian Flow Type'
#                            elif DataType == 'Riparian':
#                                titletext =  'XXXX'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster == 'mag':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Magnitude'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'AllWetlands':
                                titletext =  'Dominant Magnitude'
                            elif DataType == 'NonRiparian':
                                titletext =  'Dominant Non-Riparian Magnitude'
#                            elif DataType == 'Riparian':
#                                titletext =  'XXXX'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster == 'freq':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Freqency'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'AllWetlands':
                                titletext =  'Dominant Frequency'
                            elif DataType == 'NonRiparian':
                                titletext =  'Dominant Non-Riparian Frequency'
#                            elif DataType == 'Riparian':
#                                titletext =  'XXXX'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster == 'imp':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Impact'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'AllWetlands':
                                titletext =  'Dominant Impact'
                            elif DataType == 'NonRiparian':
                                titletext =  'Dominant Non-Riparian Impact'
#                            elif DataType == 'Riparian':
#                                titletext =  'XXXX'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster == 'ImpPaAgClass':
                        if AnalysArea == 'Wetlands':
                            if DataType == 'NonRiparian':
                                titletext =  'Path Drainage (Non-Riparian)'
#                            elif DataType == 'AllWetlands':
#                                titletext =  'XXXX'
#                            elif DataType == 'Riparian':
#                                titletext =  'XXXX'
#                        elif AnalysArea == 'Wetlands':
#                            titletext =  'Path Drainage???'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster == 'ImpDrImpervClass':
                        titletext =  'Basin Imperviousness'

                    elif InRaster == 'Class_NoImp':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Dominant Class (by Area)'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'NonRiparian':
                                titletext =  'Dominant Class (Non-Riparian by Area)'
                            elif DataType == 'AllWetlands':
                                titletext =  'Dominant Class (All Wetlands by Area)'

                    elif InRaster == 'Class_NoImp_bycount':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Dominant Class (by Count)'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'NonRiparian':
                                titletext =  'Dominant Class (Non-Riparian by Count)'
                            elif DataType == 'AllWetlands':
                                titletext =  'Dominant Class (All Wetlands by Count)'

                    elif InRaster == 'Class_NoImp_16class':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Wetland Connectivity Class'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'NonRiparian':
                                titletext =  'XXX2'
                            elif DataType == 'AllWetlands':
                                titletext =  'XXX1'

                    elif InRaster == 'WetAreaPerUnitArea':
                        if AnalysArea == 'TinerNARSRegions':
                            titletext =  'Proportion of Wetlands'
#                       elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster == 'ImpPaLev':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Path Levees'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'AllWetlands':
                                titletext =  'Path Levees (All)'
                            elif DataType == 'NonRiparian':
                                titletext =  'Path Levees (Non-Riparian)'
#                            elif DataType == 'Riparian':
#                                titletext =  'XXXX'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster == 'ImpPaCan':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Path Canals and Ditches'
                        elif AnalysArea == 'TinerNARSRegions':
                            if DataType == 'AllWetlands':
                                titletext =  'Path Canals and Ditches (All Wetlands)'
                            elif DataType == 'NonRiparian':
                                titletext =  'Path Canals and Ditches (Non-Riparian)'
                            elif DataType == 'Riparian':
                                titletext =  'XXXX'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'
#                        elif AnalysArea == 'TinerNARSRegions':
#                            titletext =  'XXXX'
                    elif InRaster   == 'TypRipPropArea':
                        if AnalysArea == 'TinerNARSRegions':
                            titletext =  'Proportion of Riparian Wetlands by Area'
                    elif InRaster   == 'AllWetlands':
                        titletext =  'All Wetlands'
                    elif InRaster == 'ImpDrAgClass':
                        titletext =  'Basin Drainage'
                    elif InRaster   == 'TypeRip':
                        if AnalysArea == 'Wetlands':
                            titletext =  'Wetland Presence'
#                        elif AnalysArea == 'TinerNARSRegions':
#                            titletext =  'XXXX'
#                        elif AnalysArea == 'Catchments':
#                            titletext =  'XXXX'

                    elif InRaster.endswith ('_Class_NoImp_2001') and AnalysArea == "Examples" :
                        if InRaster.startswith('Pipestem_'):
                            titletext =  'Wetland Connectivity Class (Pipestem Creek, ND)'
                        elif InRaster.startswith('choptank_'):
                            titletext =  'Wetland Connectivity Class (Choptank River headwaters, MD & DE)'

#                    elif InRaster == 'WetlandClass':
#                        titletext =  'Dominant Class (Area)'
#                    elif InRaster == 'WetAreaSqKm':
#                        titletext =  'Wetland Area (km<SUP>2</SUP>)'
#                    elif InRaster == 'DrainAreaSqKm':
#                        titletext =  'Wetland Basin Area (km<SUP>2</SUP>)'
#                    elif InRaster == 'DrainArea_WetArea':
#                        titletext =  'Wetland Basin Area / Wetland Area'
#                    elif InRaster == 'Run':
#                        titletext =  'Path Length (m)'
#                    elif InRaster == 'MagOv':
#                        titletext =  'Magnitude - Overland Flow (hours)'
#                    elif InRaster == 'MagSh':
#                        titletext =  'Magnitude - Shallow Subsurface Flow (days)'
#                    elif InRaster == 'FreqOv':
#                        titletext =  'Frequency - Overland Flow (mm)'
#                    elif InRaster == 'FreqSh':
#                        titletext =  'Frequency - Shallow Subsurface Flow'
#                    elif InRaster == 'ImpDrImperv':
#                        titletext =  'Impact - Basin Imperviousness (%)'
#                    elif InRaster == 'ImpDrAg':
#                        titletext =  'Impact - Basin Drainage'
#                    elif InRaster == 'ImpPaAg':
#                        titletext =  'Impact - Path Drainage'
#                    elif InRaster == 'WetAreaRipPerUnitArea':
#                        if AnalysArea == 'Catchments':
#                            titletext =  'Proportion of Wetland Area Within Catchment Comprised of Riparian Wetlands'
#                        elif AnalysArea == 'TinerNARSRegions':
#                            titletext =  'Proportion of Wetland Area Within Wetland/NARS Region Comprised of Riparian Wetlands'
#                        else:
#                            print '%s %s %s %s error' %(yearstr,AnalysArea,DataType,InRaster)
#                    else:
#                        titletext = InRaster
#                        print InRasterName
#                        print '%s %s %s %s does not exist' %(yearstr,AnalysArea,DataType,InRaster)


                    # Define raster and layer names to be mapped
                    inraster    = '%s\%s'          %(InSubFolder, InRasterName)
                    inlayer     = "%s\%s_%s"       %(Scratch,InRaster,Resolution)

                    # Define Output folder and file name
                    FilenameText= "%d%02d%02d_%s_%s_%s_%s_%s"               %(yearnum,monthnum,daynum,yearstr,AnalysArea,DataType,Resolution,InRaster)
                    OutputFolder= r"%s\Output_pdfs\%0004d%02d%02d_Maps"     %(basepath,yearnum,monthnum,daynum)
                    OutPNGName  = "%s\\%s"                                  %(OutputFolder,FilenameText)

                    # if directory does not exist, create it
                    if not os.path.isdir(OutputFolder):
                        os.makedirs(OutputFolder)

                    # if title next has changed from default, open appropriate mxd file
                    if not titletext == 'Error':
                        # Open existing mxd map document
                        if not (InRaster.startswith ('Class_') or InRaster.endswith ('_Class_NoImp_2001')):
#                            mxdDoc      =  "%s\\20170501_WetCon_mapping.mxd"              %(mxdfolder)
                            o=''
                        elif InRaster == 'Class_NoImp_16class':
                            mxdDoc      =  "%s\\20170501_WetCon_mapping_WetlandClass_allWetlands.mxd" %(mxdfolder)
                        elif InRaster.endswith ('_Class_NoImp_2001'):
                            if  InRaster.startswith('choptank'):
                                mxdDoc      =  "%s\\20170501_WetCon_mapping_WetlandClass_choptank.mxd" %(mxdfolder)
                            elif InRaster.startswith('Pipestem'):
                                mxdDoc      =  "%s\\20170501_WetCon_mapping_WetlandClass_pipestem.mxd" %(mxdfolder)
                        elif DataType == 'AllWetlands':
                            mxdDoc      =  "%s\\20170501_WetCon_mapping_WetlandClass.mxd" %(mxdfolder)
                        elif DataType == 'NonRiparian':
                            mxdDoc      =  "%s\\20170501_WetCon_mapping_WetlandClass.mxd" %(mxdfolder)
                        try:
                            mxd         = arcpy.mapping.MapDocument(mxdDoc)
                            mxd.author  = "Chas Jones, ORISE Postdoc at U.S.E.P.A. ORD WED"

                            # Define data frames and list of layers in mxd
                            df          = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
                            LayerList   = arcpy.mapping.ListLayers(mxd, "*", df)



                            # For each layer in the mxd
                            for RasterOnOff in LayerList:
                                if not RasterOnOff.isGroupLayer:
                                    # Define filepath that is appropriate for the layer of interest
                                    if AnalysArea == 'TinerNARSRegions' and ClassType != '':
                                        targetpath = "%s\\SpatialDataInputs\\Wetlands_NLCD%s\\MapRasters\\%s\\%s\\%s" %(basepath,yearstr,AnalysArea,DTfoldername,ClassType)
                                    elif AnalysArea == 'Examples':
                                        targetpath = InSubFolder
                                    else:
                                        targetpath = "%s\\SpatialDataInputs\\Wetlands_NLCD%s\\MapRasters\\%s\\%s"     %(basepath,yearstr,AnalysArea,DTfoldername)

                                    # if filepath is same as layer of interest and file name is same as layer of interest
                                    if arcpy.Describe(RasterOnOff).path == targetpath and RasterOnOff.name == InRasterName:
                                        # for each layer in mxd, either turn on or off visibility
                                        for IndividLayer in LayerList:
                                            # Make all group layers visible
                                            if IndividLayer.isGroupLayer:
                                                IndividLayer.visible = True

                                            else:
                                                # Some layers have the same name, so if the target path equals the layer filepath
                                                if arcpy.Describe(IndividLayer).path == targetpath:
                                                    # Make make matching names visible
                                                    if RasterOnOff == IndividLayer:
                                                        IndividLayer.visible = True

                                                    # Make non-matching names invisible
                                                    else:
                                                        IndividLayer.visible = False
                                                # if the file path did not match the target path, turn off visibility
                                                else:
                                                    IndividLayer.visible = False

                                                # Make States and TinerWetlandGroups visible in all cases
                                                if IndividLayer.name == 'States' or IndividLayer.name == 'TinerWetlandGroups':
                                                    IndividLayer.visible = True

                                                # Make Streams and watershed boundary and Class visible for example regions
                                                if IndividLayer.name == 'WatershedBoundaries' or IndividLayer.name == 'Rivers' or IndividLayer.name == 'Gage_connPipestemNHDH':
                                                    IndividLayer.visible = True

                                            # If mapping AllWetlands, make TinerWetlandGroups not visible
                                            if RasterOnOff.name == 'AllWetlands_300m.tif' and IndividLayer.name == 'TinerWetlandGroups':
                                                IndividLayer.visible = False

                                        # Refresh view and Table of Contents
                                        arcpy.RefreshTOC()
                                        arcpy.RefreshActiveView()

                                        # Change title text
                                        TextElement1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "Title1")[0]
                                        TextElement1.text = titletext

                                        # Change filename text on bottom of page
                                        TextElement2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT","Filename")[0]
                                        TextElement2.text = FilenameText

                                        # IF FILENAME IS NOT DESIRED TO BE ON FINAL MAP, REMOVE COMMENT FROM THE NEXT LINE
    #                                    TextElement2.text = ""

                                        # Export map to PNG file
                                        arcpy.mapping.ExportToPNG(mxd, OutPNGName, resolution=600)
                        except:
                            pass
print "End time: %s\n"%(datetime.datetime.now())