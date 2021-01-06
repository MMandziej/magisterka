## HT transformation
# Change polish characters to ordinary characters
# to replaced -> only latest file
for(i in 1:nrow(ht_all)){
  ht_all$Employee[i] = mgsub(ht_all$Employee[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
}

# Filtering data
ht_all <- ht_all[-which(is.na(ht_all$Team)),]
ht_all <- ht_all[-which(is.na(ht_all$Employee)),]
ht_all <- ht_all[-which(ht_all$Team %in% c("Mgmt", "Process", "MI", "SME", "PMO")), ]
ht_all$Date <- as.POSIXct(substr(ht_all$Date, 1, 10), tz = 'UTC')

# create experience table
group_project <- aggregate(ht_all$Date, by=list(Category=ht_all$Employee), FUN=min) # date of join to project
group_team <- aggregate(Date~Employee+Team+Role, ht_all, FUN=min) # date of join to team
colnames(group_project) <- c("Employee", "MinDateProject")
colnames(group_team) <- c("Employee", "Team", "Role", "MinDateTeam")
group_project$MinDateProject <- as.POSIXct(substr(group_project$MinDateProject, 1, 10), tz = 'UTC')
group_team$MinDateTeam <- as.POSIXct(substr(group_team$MinDateTeam, 1, 10), tz = 'UTC')

ht_experience <- inner_join(x = group_project, 
                            y = group_team, 
                            by = 'Employee')
# rearrange cols
ht_experience <- ht_experience[, c('Employee', 'Team', 'Role', 'MinDateProject', 'MinDateTeam')]

for(i in 1:nrow(ht_experience)){
  ht_experience$Employee[i] = mgsub(ht_experience$Employee[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
}

ht_experience_tl <- ht_experience %>% filter(Role == 'TL')
ht_experience_analyst <- ht_experience %>% filter(Role == 'Analyst')
ht_experience_merged <- merge(ht_experience, ht_experience_tl, by = 'Team')
# prepare TL - Analyst mapping
tl_analyst_mapping = merge(ht_experience_analyst, ht_experience_tl, by = 'Team')
tl_analyst_mapping <- tl_analyst_mapping %>% select_(~Team, ~Employee.x, ~MinDateProject.x, ~MinDateTeam.x,
                                                     ~Employee.y, ~MinDateProject.y, ~MinDateTeam.y)
colnames(tl_analyst_mapping) <- c('Team', 'Analyst', 'AnalystMinDateProject', 'AnalystMinDateTeam',
                                  'TeamLeader', 'TLMinDateProject', 'TLMinDateTeam')

write.xlsx(tl_analyst_mapping, paste("data/tl_analyst_mapping_", Sys.Date(), ".xlsx", sep = ''), row.names = F)