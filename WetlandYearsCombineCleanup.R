fullcombine = read.csv('H:/WorkingData/Wetlands17c_Combine.csv')
willamette = read.csv('H:/WorkingData/WillametteComtine.csv')
head(fullcombine)
head(willamette)
Willamette_combine = fullcombine[fullcombine$VALUE %in% willamette$Value,]
head(Willamette_combine)
names(Willamette_combine)[4] = 'WetlandID_2001'
names(Willamette_combine)[5] = 'WetlandID_2011'
Willamette_combine = Willamette_combine[c(-1)]
write.csv(Willamette_combine, 'H:/WorkingData/Willamette_CombinedWetlands.csv', row.names=FALSE)
