library(dplyr)

flow_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/FlowPathTables/'
accum_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/WetlandPath/Accumulation/'
wetlands_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/FinalTables/WetlandTables/'
lookup_path = 'L:/Priv/CORFiles/Geospatial_Library/Data/Project/WetlandConnectivity/LookupTables/'

files = list.files(accum_path, pattern = 'nlcd'); rpus = c()
for(i in 1:length(files)){
  #print(files[i])
  rpus[i] = substr(files[i], 15, 17)
}

#-------------------------------------------------------------------------------------------------------
#Make overland tables for wetlands and include geographically connected wetlands with travel time = 0
for(i in 1:length(rpus)){
  print(rpus[i])
  fp = read.csv(paste0(flow_path, 'OverlandFlow_', rpus[i], '.csv'))
  fp = select(fp, PATHID, WETID, t_overland)
  np = read.csv(paste0(lookup_path, 'WetlandsNoPath_StreamLink_Lookup_', rpus[i], '.csv'))
  np = select(np, WET_ID, STRMLNK_ID)
  names(np) <- c('WETID', 'PATHID')
  np = np[ , c('PATHID', 'WETID')] #Reorder to match fp
  np$t_overland = 0
  fp = rbind(fp,np)
  write.csv(fp, file = paste0(wetlands_path, 'OverlandFlow_', rpus[i], '.csv'), row.names=F)
}
#-------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------
#Make shallow tables for wetlands and include geographically connected wetlands with travel time = 0
#Also remove connector paths (i.e., paths without wetlands)
for(i in 1:length(rpus)){
  print(rpus[i])
  fp = read.csv(paste0(flow_path, 'ShallowFlow_', rpus[i], '.csv'))
  fp = select(fp, PATHID, t_shallow)
  np = read.csv(paste0(lookup_path, 'AllWetlands_StreamLink_Lookup_', rpus[i], '.csv'))
  np = select(np, WET_ID, STRMLNK_ID)
  names(np) <- c('WETID', 'PATHID')
  #np = np[ , c('PATHID', 'WETID')] #Reorder to match fp
  fp = merge(fp, np, by='PATHID', all.y=T)  
  fp[is.na(fp$PATHID), 't_shallow'] = 0    
  fp = fp[ , c('PATHID','WETID','t_shallow')]
  write.csv(fp, file = paste0(wetlands_path, 'ShallowFlow_', rpus[i], '.csv'), row.names=F)
}
#-------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------
#Make FlowClass tables - remove path-only and add GCW point types
#Also remove connector paths (i.e., paths without wetlands)
for(i in 1:length(rpus)){
  print(rpus[i])
  fp = read.csv(paste0(flow_path, 'FlowClass_', rpus[i], '.csv'))
  fp = select(fp, PATHID, DomFlow)
  np = read.csv(paste0(lookup_path, 'WetlandsWithPath_StreamLink_Lookup_', rpus[i], '.csv'))
  np = select(np, WET_ID, STRMLNK_ID)
  names(np) <- c('WETID', 'PATHID')
  #np = np[ , c('PATHID', 'WETID')] #Reorder to match fp
  fp = merge(fp, np, by='PATHID', all.y=T)     
  fp = fp[ , c('PATHID','WETID','DomFlow')]  
  pt = read.csv(paste0(wetlands_path, 'Wetland_NoPath_FlowClass', rpus[i], '.csv'))
  pt$PATHID = NA
  pt = pt[ , c('PATHID','WETID','DomFlow')]   
  fp = rbind(fp, pt)  
  write.csv(fp, file = paste0(wetlands_path, 'FlowClass_', rpus[i], '.csv'), row.names=F)
}
#-------------------------------------------------------------------------------------------------------









