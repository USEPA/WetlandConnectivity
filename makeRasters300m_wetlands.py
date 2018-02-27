import sys, arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
sys.path.append(r'J:\GitProjects\Wetland Connectivity\WetlandScripts')
from raster_function import catcsv2raster2
import pandas as pd
import numpy as np
import gc

year = '2001'
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
inTable.loc[inTable['Type']=='Ripar','Type'] = 1
inTable.loc[inTable['Type']=='NRSub','Type'] = 2
inTable.loc[inTable['Type']=='NRSur','Type'] = 3
inTable.loc[inTable['Type']=='NRSub','Type'] = 2

##Drainage classes
#inTable.loc[inTable['FreqSh']=='VALUE_0','FreqSh'] = np.nan
#inTable.loc[inTable['FreqSh']=='VALUE_1','FreqSh'] = 0
#inTable.loc[inTable['FreqSh']=='VALUE_2','FreqSh'] = 1
#inTable.loc[inTable['FreqSh']=='VALUE_3','FreqSh'] = 2

#Frequency classes
inTable.loc[inTable['Freq']=='H','FreqPa'] = 3
inTable.loc[inTable['Freq']=='M','FreqPa'] = 2
inTable.loc[inTable['Freq']=='L','FreqPa'] = 1


#Magnitude classes
inTable.loc[(inTable['Type']==1),'Mag'] = 5 #VF
inTable.loc[(inTable['Type']==3) & (inTable['MagOv'] <= 24),'Mag'] = 5 #VF
inTable.loc[(inTable['Type']==3) & (inTable['MagOv']/24 <= 14) & (inTable['MagOv'] > 24),'Mag'] = 4 #FA
inTable.loc[(inTable['Type']==3) & (inTable['MagOv']/24 > 14) ,'Mag'] = 3 #MO
inTable.loc[(inTable['Type']==2) & (inTable['MagSh'] <= 1),'Mag'] = 5 #VF
inTable.loc[(inTable['Type']==2) & (inTable['MagSh'] > 1) & (inTable['MagSh'] <= 14),'Mag'] = 4 #FA
inTable.loc[(inTable['Type']==2) & (inTable['MagSh'] > 14) & (inTable['MagSh']/365.25 <= 1),'Mag'] = 3 #MO
inTable.loc[(inTable['Type']==2) & (inTable['MagSh']/365.25 > 1) & (inTable['MagSh']/365.25 <= 10),'Mag'] = 2 #SL
inTable.loc[(inTable['Type']==2) & (inTable['MagSh']/365.25 > 10),'Mag'] = 1 #VS

#Impact classes
inTable.loc[(inTable['Type']==1) & (inTable['ImpDrImperv'] + inTable['ImpDrAg']==0.0),'ImpClass'] = 1 #None
inTable.loc[(inTable['Type']==1) & (inTable['ImpDrImperv'] <= 5) & (inTable['ImpDrAg'] <= 5) & (inTable['ImpDrImperv'] + inTable['ImpDrAg'] !=0.0),'ImpClass'] = 2 #Low
inTable.loc[(inTable['Type']==1) & (inTable['ImpClass'].isnull()),'ImpClass'] = 3 #High
inTable.loc[(inTable['Type']!=1) & (inTable['ImpDrImperv'] + inTable['ImpDrAg'] + inTable['ImpPaAg'] + inTable['ImpPaLev'] + inTable['ImpPaCan'] ==0.0),'ImpClass'] = 1 #None
inTable.loc[(inTable['Type']!=1) & (inTable['ImpDrImperv'] <= 5) & (inTable['ImpDrAg'] <= 5) & (inTable['ImpPaAg'] <= 5) & (inTable['ImpPaLev'] \
            <= 5) & (inTable['ImpPaCan'] <= 5) & (inTable['ImpDrImperv'] + inTable['ImpDrAg'] !=0.0),'ImpClass'] = 2 #Low
inTable.loc[(inTable['Type']!=1) & (inTable['ImpClass'].isnull()),'ImpClass'] = 3 #High

#16-class connectivity class
inTable.loc[inTable['Type']==1,'ConClass'] = 1 #RiparVFH
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==1)  & (inTable['MagOv']<=24.0),'ConClass'] = 2 #NRSurVFL
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==2)  & (inTable['MagOv']<=24.0),'ConClass'] = 3 #NRSurVFM
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==3)  & (inTable['MagOv']<=24.0),'ConClass'] = 4 #NRSurVFH
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==1)  & ((inTable['MagOv']/24)<=14) & ((inTable['MagOv'])>24),'ConClass'] = 5 #NRSurFL
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==2)  & ((inTable['MagOv']/24)<=14) & ((inTable['MagOv'])>24),'ConClass'] = 6 #NRSurFM
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==3)  & ((inTable['MagOv']/24)<=14) & ((inTable['MagOv'])>24),'ConClass'] = 7 #NRSurFH
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==1)  & (inTable['MagOv']/24 > 14) & (inTable['MagOv']/24 <= 365),'ConClass'] = 8 #NRSurMOL
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==2)  & (inTable['MagOv']/24 > 14) & (inTable['MagOv']/24 <= 365),'ConClass'] = 9 #NRSurMOM
inTable.loc[(inTable['Type']==3) & (inTable['FreqPa']==3)  & (inTable['MagOv']/24 > 14) & (inTable['MagOv']/24 <= 365),'ConClass'] = 10 #NRSurMOH
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==1)  & (inTable['MagSh']/365.25>10),'ConClass'] = 11 #NRSubVSL
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==2)  & ((inTable['MagSh']/365.25)>10),'ConClass'] = 12 #NRSubVSM
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==3)  & (inTable['MagSh']/365.25>10),'ConClass'] = 13 #NRSubVSH
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==1)  & ((inTable['MagSh']/365.25)<=10) & ((inTable['MagSh']/365.25)>1),'ConClass'] = 14 #NRSubSLL
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==2)  & ((inTable['MagSh']/365.25)<=10) & ((inTable['MagSh']/365.25)>1),'ConClass'] = 15 #NRSubSLM
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==3)  & ((inTable['MagSh']/365.25)<=10) & ((inTable['MagSh']/365.25)>1),'ConClass'] = 16 #NRSubSLH
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==1)  & ((inTable['MagSh']/365.25)<=1) & ((inTable['MagSh'])>14),'ConClass'] = 17 #NRSubMOL
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==2)  & ((inTable['MagSh']/365.25)<=1) & ((inTable['MagSh'])>14),'ConClass'] = 18 #NRSubMOM
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==3)  & ((inTable['MagSh']/365.25)<=1) & ((inTable['MagSh'])>14),'ConClass'] = 19 #NRSubMOH
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==1)  & ((inTable['MagSh'])<=14) & ((inTable['MagSh'])>1),'ConClass'] = 20 #NRSubFAL
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==2)  & ((inTable['MagSh'])<=14) & ((inTable['MagSh'])>1),'ConClass'] = 21 #NRSubFAM
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==3)  & ((inTable['MagSh'])<=14) & ((inTable['MagSh'])>1),'ConClass'] = 22 #NRSubFAH
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==1)  & (inTable['MagSh']<=1),'ConClass'] = 23 #NRSubVFL
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==2)  & (inTable['MagSh']<=1),'ConClass'] = 24 #NRSubVFM
inTable.loc[(inTable['Type']==2) & (inTable['FreqPa']==3)  & (inTable['MagSh']<=1),'ConClass'] = 25 #NRSubVFH


inTemplate = wd2 + 'WetlandsRgnGrp_300m.tif'
#inTemplate = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/SpatialDataInputs/ExampleLocations/pipestem_template_' + year + '.tif'

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
#            outRas = 'L:/Priv/CORFiles/Geospatial_Library\Data\Project\WetlandConnectivity/SpatialDataInputs/ExampleLocations/Pipestem_' + Value + '_' + year + '.tif'
            if not arcpy.Exists(outRas):
                catcsv2raster2(inTable, Value, inTemplate, outRas, dtype='Int', idName='WetId')
            gc.collect()                
#--------------------------------------------------------------------------------------------------------------------   






