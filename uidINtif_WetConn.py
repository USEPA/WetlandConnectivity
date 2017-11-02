# -*- coding: utf-8 -*-
"""
Created on Wed Nov 09 10:17:14 2016

Burn the NoWetlandDrain rasters with the GRIDCODE of NHDPlus Catchments for zonal 
analysis, then build Raster Attribute table and quantify tha amount of NoWetland
Drain area w/in each zone.

Also, mask the split-cat rasters for NRSA0809 with the NoWetDrain RPU rasters

@author: Rdebbout
"""

import os
import struct
import decimal
import datetime
import itertools
from osgeo import gdal
import numpy as np
import pandas as pd
import arcpy
import georasters as gr
from collections import OrderedDict

inputs = OrderedDict([('10U','MS'),('10L','MS'),('07','MS'),('11','MS'),
                      ('06','MS'),('05','MS'),('08','MS'),('01','NE'),
                      ('02','MA'),('03N','SA'),('03S','SA'),('03W','SA'),
                      ('04','GL'),('09','SR'),('12','TX'),('13','RG'),
                      ('14','CO'),('15','CO'),('16','GB'),('17','PN'),
                      ('18','CA')])

rpus = OrderedDict([(u'01', ['01a']),
                     (u'02', ['02a', '02b']),
                     (u'03N', ['03a', '03b']),
                     (u'03S', ['03c', '03d']),
                     (u'03W', ['03e', '03f']),
                     (u'04', ['04a', '04b', '04c', '04d']),
                     (u'05', ['05a', '05b', '05c', '05d']),
                     (u'06', ['06a']),
                     (u'07', ['07a', '07b', '07c']),
                     (u'08', ['03g', '08a', '08b']),
                     (u'09', ['09a']),
                     (u'10L', ['10a', '10b', '10c', '10d']),
                     (u'10U', ['10e', '10f', '10g', '10h', '10i']),
                     (u'11', ['11a', '11b', '11c', '11d']),
                     (u'12', ['12a', '12b', '12c', '12d']),
                     (u'13', ['13a', '13b', '13c', '13d']),
                     (u'14', ['14a', '14b']),
                     (u'15', ['15a', '15b']),
                     (u'16', ['16a', '16b']),
                     (u'17', ['17a', '17b', '17c', '17d']),
                     (u'18', ['18a', '18b', '18c'])])

def dbfreader(f):

    numrec, lenheader = struct.unpack('<xxxxLH22x', f.read(32))    
    numfields = (lenheader - 33) // 32

    fields = []
    for fieldno in xrange(numfields):
        name, typ, size, deci = struct.unpack('<11sc4xBB14x', f.read(32))
        name = name.replace('\0', '')       # eliminate NULs from string   
        fields.append((name, typ, size, deci))
    yield [field[0] for field in fields]
    yield [tuple(field[1:]) for field in fields]

    terminator = f.read(1)
    assert terminator == '\r'

    fields.insert(0, ('DeletionFlag', 'C', 1, 0))
    fmt = ''.join(['%ds' % fieldinfo[2] for fieldinfo in fields])
    fmtsiz = struct.calcsize(fmt)
    for i in xrange(numrec):
        record = struct.unpack(fmt, f.read(fmtsiz))
        if record[0] != ' ':
            continue                        # deleted record
        result = []
        for (name, typ, size, deci), value in itertools.izip(fields, record):
            if name == 'DeletionFlag':
                continue
            if typ == "N":
                value = value.replace('\0', '').lstrip()
                if value == '':
                    value = 0
                elif deci:
                    value = decimal.Decimal(value)
                else:
                    value = int(value)
            elif typ == 'C':
                value = value.rstrip()                                   
            elif typ == 'D':
                try:
                    y, m, d = int(value[:4]), int(value[4:6]), int(value[6:8])
                    value = datetime.date(y, m, d)
                except:
                    value = None
            elif typ == 'L':
                value = (value in 'YyTt' and 'T') or (value in 'NnFf' and 'F') or '?'
            elif typ == 'F':
                value = float(value)
            result.append(value)
        yield result
        
def dbf2DF(f, upper=True):
    data = list(dbfreader(open(f, 'rb')))
    if upper == False:    
        return pd.DataFrame(data[2:], columns=data[0])
    else:
        return pd.DataFrame(data[2:], columns=map(str.upper,data[0]))

def makeRat(fn):

    ds = gdal.Open(fn)
    rb = ds.GetRasterBand(1)
    nd = rb.GetNoDataValue()
    data = rb.ReadAsArray()
    # Get unique values in the band and return counts for COUNT val
    u = np.array(np.unique(data, return_counts=True))
    #  remove NoData value
    u = np.delete(u, np.argwhere(u==nd), axis=1)
    
    # Create and populate the RAT
    rat = gdal.RasterAttributeTable()
    rat.CreateColumn('Value', gdal.GFT_Integer, gdal.GFU_Generic)
    rat.CreateColumn('Count', gdal.GFT_Integer, gdal.GFU_Generic)
    for i in range(u[0].size):
        rat.SetValueAsInt(i, 0, int(u[0][i]))
        rat.SetValueAsInt(i, 1, int(u[1][i]))
    
    # Associate with the band
    rb.SetDefaultRAT(rat)
    
    # Close the dataset and persist the RAT
    ds = None 
    
    #return the rat to build DataFrame
    df = rat_to_df(rat)
    return df
       
##############################################################################


def rat_to_df(in_rat):
    """
    __author__ =  "Matt Gregory <matt.gregory@oregonstate.edu >"
    Given a GDAL raster attribute table, convert to a pandas DataFrame
    Parameters
    ----------
    in_rat : gdal.RasterAttributeTable
        The input raster attribute table
    Returns
    -------
    df : pd.DataFrame
        The output data frame
    """
    # Read in each column from the RAT and convert it to a series infering
    # data type automatically
    s = [pd.Series(in_rat.ReadAsArray(i), name=in_rat.GetNameOfCol(i))
         for i in xrange(in_rat.GetColumnCount())]

    # Concatenate all series together into a dataframe and return
    return pd.concat(s, axis=1)
      
def makeMaskTIFs_WetConn(nhd, outDir, mask_ras, fn):
    for zone in inputs:
        hr = inputs[zone]
        cat = "%s/NHDPlus%s/NHDPlus%s/NHDPlusCatchment/cat"%(nhd, hr, zone)
        print cat
        r = arcpy.Raster(cat)
        for rpu in rpus[zone]:
            mask = arcpy.Raster("%s/%s_%s.tif" % (mask_ras, fn, rpu))
            rMask = mask * r
            rMask.save("{}/WetCat_GRID_{}.tif".format(outDir, rpu))
            
def offset_pt(gr1,gr2):
    res = gr1.geot[1] 
    xmin = gr1.bounds[0] 
    a = gr1.bounds[0] % res 
    b = gr2.bounds[0] % res
    c = (a-b)
    if a>b:
        xmin += c
    else:
        xmin -= c
    ymax = gr1.bounds[-1] 
    d = gr1.bounds[-1] % res
    e = gr2.bounds[-1] % res
    f = (d-e)
    if d>e:
        ymax -= f
    else:
        ymax += f    
    return xmin, ymax            

################################################################################

if __name__=='__main__':
    
    arcpy.CheckOutExtension("Spatial")
    nm = ('L:/Priv/CORFiles/Geospatial_Library/Data/Project/'
         'WetlandConnectivity/NitrogenModeling')
    nhd = 'D:/NHDPlusV21'
    outTifs = '%s/LandscapeRasters/WetlandNoWetDrainMask/gridcoded' % nm
    loc = '%s/LandscapeRasters/WetlandNoWetDrainMask/' % nm
    
    # make masks with gridcode
    makeMaskTIFs_WetConn(nhd, outTifs, loc, 'WetCat_NoWetDrain')
    
    # create Area tables from attribute table for each VPU
    out = '%s/LandscapeRasters/WetlandNoWetDrainMask/out_RD/AreaTables' % nm
    for zone in inputs:
        if not os.path.exists('%s/NoWetArea_%s.csv' % (out, zone)):
            print zone
            hr = inputs[zone]
            final = pd.DataFrame()
            for rpu in rpus[zone]:
                tbl = makeRat('%s/WetCat_GRID_%s.tif' % (outTifs, rpu))
                final = pd.concat([final,tbl])
            catDF = dbf2DF("%s/NHDPlus%s/NHDPlus%s/NHDPlusCatchment/Catchment.dbf"%(nhd, hr, zone))[['GRIDCODE','FEATUREID']]
            both = pd.merge(catDF, final, left_on='GRIDCODE', right_on='Value', how='left')
            both.drop(['GRIDCODE','Value'],axis=1, inplace=True)
            both.columns = ['COMID','Count']
            both.fillna(0,inplace=True)
            both['AreaSqKM'] = (both.Count * 900) * 1e-6
            both.to_csv('%s/NoWetArea_%s.csv' % (out, zone),index=False)
    move = '%s/Allocation_Accumulation' % nm
    for zone in inputs:
        print zone
        hr = inputs[zone]
        tbl = pd.read_csv('%s/NoWetArea_%s.csv' % (out, zone))
        tbl.columns = ['COMID','CatCount', 'CatAreaSqKm']
        tbl = tbl[['COMID','CatAreaSqKm','CatCount']]
        tbl.to_csv('%s/NoWetArea_%s.csv' % (move, zone),index=False)
    
    # mask the split catchment tifs for NoWetDrain area
    
    split_dir = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/NRSA/NRSA0809'

    pts = dbf2DF('%s/NRSA_0809_adj_PTS.dbf' % split_dir)


    for zone in inputs:
        for rpu in rpus[zone]:
            print rpu
            mask = gr.from_file("%s/WetCat_NoWetDrain_%s.tif" % (loc, rpu))
            geot = mask.geot
            rpu_sites = pts.ix[pts.RPU == rpu].SITE_ID.tolist()
            for site in rpu_sites:
                split = gr.from_file('%s/SplitCats_tifs/ws%s.tif' % (split_dir,site))
                xmin,ymax = offset_pt(split,mask)
                nrows, ncols = split.shape
                beg_row, beg_col = gr.map_pixel(xmin,ymax,geot[1],geot[-1],geot[0],geot[3])
                mask_slice = mask.raster[beg_row:beg_row+nrows,beg_col:beg_col+ncols]
                split.raster.mask = mask_slice.mask
                if (split.raster.data[~split.raster.mask] == 255).all():
                    print site
                    continue
                split.to_tiff('%s/NRSA_splits_0809_tifs/hold/ws%s' % (loc, site))
 
#    
#rpu = '12b'
#site = 'FW08TX031'
#
#for x in split.raster.data[split.raster.mask]:
#    if x != 255:
#        print x
#        
#from shapely.geometry import Point        
#import geopandas as gpd
#
#tt = gpd.GeoDataFrame({'val':[47]},geometry=[Point(xmin,ymax)],crs={'init':'epsg:5070'})
#tt.to_file('%s/NRSA_splits_0809_tifs/hold/A.shp' % (loc))
#split.bounds
#
#gr1 = split.copy()
#gr2 = mask.copy()
#
#def offset_pt(gr1,gr2):
#    
#    xmin = gr1.bounds[0] + ((gr1.bounds[0] % gr1.geot[1]) - (gr2.bounds[0] % gr1.geot[1]))
#    ymax = gr1.bounds[-1] - ((gr1.bounds[-1] % gr1.geot[1]) - (gr2.bounds[-1] % gr1.geot[1]))
#    return xmin, ymax  
#
#import numpy as np
#count = 0
#for f in os.listdir('%s/NRSA_splits_0809_tifs/new' % loc):
#    if '.tif' in f:
#        uno = gr.from_file('%s/NRSA_splits_0809_tifs/new/%s' % (loc,f))
#        if not os.path.exists('%s/NRSA_splits_0809_tifs/%s' % (loc,f)):
#            print f
#            continue
#        dos = gr.from_file('%s/NRSA_splits_0809_tifs/%s' % (loc,f))
#        if not np.ma.allequal(uno.raster,dos.raster) == True:
#            print f
#        count+=1