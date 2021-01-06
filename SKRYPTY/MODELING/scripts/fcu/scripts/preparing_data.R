library(readxl)
library(dplyr)
library(plyr)
library(plotly)
library(stringr)



## Loading PostgreSQL driver
drv <- dbDriver("PostgreSQL")

## Connecting to db
con <-
  dbConnect(
    drv,
    dbname = "lionqc",
    host = "40.121.134.61",
    port = 5432,
    user = "postgres",
    password = 'Mjord@n23'
  )


# Reading all cutoffs in the directory
files <- list.files(pattern = "cut off.xlsx", full.names = T)
cut_offs_all<- NULL
cut_offs_all <- sapply(files, read_excel, simplify=FALSE) %>% rbind.fill(.id = "id")


# Creating table on db and storing all cutoffs on that table
dbWriteTable(con, "cutoff_all", cut_offs_all, row.names=FALSE)


# HT for 2020
ht_20<- read_excel("28022020 HT.xlsx")
ht_20_final<- data.frame(ht_20$Role, ht_20$Team,ht_20$Employee,ht_20$Date)
colnames(ht_20_final) <- c("Role", "Team", "Employee", "Date")

# HT for 2019
ht_19<- read_excel("HT.xlsx")
ht_19_final <- data.frame(ht_19$CurrentRole,ht_19$TeamNo,ht_19$INGName,ht_19$CurrentDate)
colnames(ht_19_final) <- c("Role", "Team", "Employee", "Date")


# HT for 2018_2017
ht_17_18<- read_excel("HT_2017_2018.xlsx")
ht_17_18_final <- data.frame(ht_17_18$CurrentRole,ht_17_18$TeamNo,ht_17_18$IPName,ht_17_18$CurrentDate)
colnames(ht_17_18_final) <- c("Role", "Team", "Employee", "Date")


# Creating names as they are in other ht files
employee_name<-NULL
for(i in 1:dim(ht_17_18_final)[1])
{
surname<- str_split(ht_17_18_final$Employee[i],",")[[1]][1]
name<- str_split(ht_17_18_final$Employee[i],",")[[1]][2]
name_final<- str_split(name," ")[[1]][2]
name_first<- substr(name_final,1,1)
emp_name<- paste(surname,","," ",name_first,"."," ","(",name_final,")",sep = "")

employee_name <- rbind(employee_name,emp_name)
}

row.names(employee_name) <- NULL

ht_17_18_final$Employee<-employee_name

## Binding all holiday tracker data into one df
holiday_tracker_all<-NULL
holiday_tracker_all<- bind_rows(ht_17_18_final,ht_19_final,ht_20_final)

# Creating new table on db and storing holiday_tracker_all
dbWriteTable(con, "holiday_tracker_all", holiday_tracker_all)