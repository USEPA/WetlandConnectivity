old_lookup = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/old_LookupTables/'
cat_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/NHDPlusCatchmentTables/'

# overland
master_table = read.csv(paste0(old_lookup,'eco9_all.csv'))
head(master_table)

intable = read.csv(paste0(cat_path, 'ShallowFlow.csv'))
head(intable)
master_table$t_shallow_mean_all = intable$t_shallow_mean_all[match(master_table$COMID, intable$COMID)]
master_table$t_shallow_mean_iso = intable$t_shallow_mean_iso[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'OverlandFlow.csv'))
head(intable)
master_table$t_overland_mean_all = intable$t_overland_mean_all[match(master_table$COMID, intable$COMID)]
master_table$t_overland_mean_iso = intable$t_overland_mean_iso[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'GIW_PERCENT.csv'))
head(intable)
master_table$PCTGIW = intable$PCTGIW[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'PctLeveeInfluence.csv'))
head(intable)
master_table$PctLevee = intable$PctLevee[match(master_table$COMID, intable$COMID)]

#master_table = readRDS('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/ForScott/WetlandMetric.rds')

intable = read.csv(paste0(cat_path, 'DOMFLOW.csv'))
head(intable)
master_table$DomFlow = intable$DomFlow[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'DomFldFreqCls.csv'))
head(intable)
master_table$FldFreqCls = intable$DomCode[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'DomDrainClass.csv'))
head(intable)
master_table$DrainCls = intable$DomCode[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'PctAgDrainBasin.csv'))
head(intable)
master_table$PctAgDrainBasin = intable$PctAgDrainBasin[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'PctAgDrainPath.csv'))
head(intable)
master_table$PctAgDrainPath = intable$PctAgDrainPath[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'PctImpervious.csv'))
head(intable)
master_table$Impervious = intable$Impervious[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'PctWetland.csv'))
head(intable)
master_table$PctWetland = intable$PctWetland[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'WetBasinAreas.csv'))
head(intable)
master_table$meanBasinArea = intable$meanBasinArea[match(master_table$COMID, intable$COMID)]
master_table$totalBasinAreas = intable$totalBasinAreas[match(master_table$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'WetlandAreas.csv'))
head(intable)
master_table$meanWetlandArea = intable$WetldArea_mean[match(master_table$COMID, intable$COMID)]
master_table$totalWetlandAreas = intable$WetldArea_sum[match(master_table$COMID, intable$COMID)]

tmp = master_table

tmp$totalWetlandAreaGIW = tmp$totalWetlandAreas * (tmp$PCTGIW / 100)

classes = readRDS('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/ForScott/WetlandClassesCombinedWithCatchmentID.rds')
comids = readRDS('L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/ForScott/comid_gridcode.rds')

classes = classes[, c('CAT_30M','FINALCOMBI')]
names(classes) = c('GRIDCODE','BinCombos')
classes$COMID = NA
classes$COMID = comids$COMID[match(classes$GRIDCODE, comids$GRIDCODE)]

tmp$BinCombos = classes$BinCombos[match(tmp$COMID, classes$COMID)]

intable = read.csv(paste0(cat_path, 'GIW_PERCENT.csv'))
head(intable)
tmp$PCTGIW = intable$PCTGIW[match(tmp$COMID, intable$COMID)]

intable = read.csv(paste0(cat_path, 'DOMFLOW_GIW.csv'))
head(intable)
tmp$DomFlow_GIW = intable$DomFlow_GIW[match(tmp$COMID, intable$COMID)]


saveRDS(tmp, file = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/ForScott/WetlandMetric_19sep2016.rds')
write.csv(master_table, file = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/ForScott/WetlandMetric.csv', row.names=F)

















