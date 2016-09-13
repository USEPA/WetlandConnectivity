wetlands_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/WetlandTables/'
lookup_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/LookupTables/'
cat_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/NHDPlusCatchmentTables/'
accum_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/Accumulation/'

library(dplyr)
master_table = read.csv(paste0(lookup_path,'eco9_all.csv'))

files = list.files(accum_path, pattern = 'nlcd'); rpus = c()
for(i in 1:length(files)){
  #print(files[i])
  rpus[i] = substr(files[i], 15, 17)
}

#-------------------------------------------------------------------------------------------------------
#Summarize FlowClass by COMID
majority = function(x){
  result = names(which.max(table(x)))
  return(result)
}

for(i in 1:length(rpus)){
  print(rpus[i])
  travel = read.csv(paste0(wetlands_path, 'FlowClass_', rpus[i], '.csv'))
  travel = travel[!is.na(travel$DomFlow), ]
  cat_lookup = read.csv(paste0(lookup_path, 'Wetlands_NHDPlusCat_Lookup_', rpus[i], '.csv'))
  travel$COMID = cat_lookup$COMID[match(travel$WETID, cat_lookup$WET_ID)]
  if (i==1){
    final = group_by(travel,COMID)
    final = summarize(final, DominantFlow = majority(DomFlow))
    final$WSA_9 = master_table$WSA_9[match(final$COMID, master_table$COMID)]
  }
  if (i> 1){
    temp = group_by(travel,COMID)
    temp = summarize(temp, DominantFlow = majority(DomFlow))
    temp$WSA_9 = master_table$WSA_9[match(temp$COMID, master_table$COMID)]
    final = rbind(final, temp)
  }
}

master_table$DominantFlow = final$DominantFlow[match(master_table$COMID, final$COMID)]
master_table$DomCode = NA
master_table$DomCode[master_table$DominantFlow=='Overland'] = 1
master_table$DomCode[master_table$DominantFlow=='Shallow'] = 2
master_table$DomCode[master_table$DominantFlow=='ShallowDeep'] = 3

write.csv(master_table, file = paste0(cat_path, 'DominantFlowClass.csv'), row.names=F)

rmNA = na.omit(master_table)
write.csv(rmNA, file = paste0(cat_path, 'DominantFlowClass_narm.csv'), row.names=F)

#-------------------------------------------------------------------------------------------------------



library(dplyr)

wd = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/StreamCat/FTP_Staging/StreamCat/HydroRegions/'
out_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/NHDPlusCatchmentTables/'
lookup_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/LookupTables/'


files = list.files(wd , patter = 'NLCD2011_Region')

for(i in 1:length(files)){
  print(files[i])
  
  tmp = read.csv(paste0(wd, files[i]))
  tmp = tmp[, c('COMID', 'PctWdWet2011Cat', 'PctHbWet2011Cat')]
  tmp$PctWetland = tmp$PctWdWet2011Cat + tmp$PctHbWet2011Cat
  
  if(i==1){
    out = tmp
  }else{
    out = rbind(out, tmp)
  }  
}

out = select(out, -PctWdWet2011Cat, -PctHbWet2011Cat)

in_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/NHDPlusCatchmentTables/'
file = 'PctWetland.csv'

out = read.csv(paste0(in_path, file))

master_table = read.csv(paste0(lookup_path,'eco9_all.csv'))
master_table$PctWetland = out$PctWetland[match(master_table$COMID, out$COMID)]

write.csv(master_table, file = paste0(out_path, 'PctWetland.csv'), row.names=F)




