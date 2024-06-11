library(RPostgres)
library(readxl)

budget_state_per_capital <- read_excel("Downloads/aihw-93-Health-expenditure-Australia-2021-2022.xlsx", 
                                                             sheet = "Table 5", range = "A1:X14")

budget_state_per_capital$Year <- 2011:2021

colnames(budget_state_per_capital) <- c("Year","NSW", "Vic", "Qld", "WA", "SA", "Tas", "NT", "NAT")
budget_state <- as.data.frame(budget_state_per_capital)

# Connect to the PostgreSQL database
con <- dbConnect(RPostgres::Postgres(),
                 host = "localhost",
                 port = 5433,
                 user = "user",
                 password = "password",
                 dbname = "mydatabase")

#Questa parte mi è servita ad ottenere le tabelle
dbListTables(con)

values <- dbGetQuery(con, "SELECT * FROM values")

#Elimino gli ospedali e tendo gli stati e la nazione
values_national <- values %>%
  filter(ReportingUnitCode %in% c("NSW", "Vic", "Qld", "SA", "WA", "Tas", "NT", "ACT", "NAT"))






# Extracting NAT values for each DataSetId
nat_values <- subset(values, ReportingUnitCode == "NAT", select = c("DataSetId", "Value"))
colnames(nat_values) <- c("DataSetId", "NAT_Value")

# Merge NAT values with original data
values <- merge(values, nat_values, by = "DataSetId")

# Calculate ratios
values$Ratio <- values$Value / values$NAT_Value

# Filter only specific ReportingUnitCodes
values <- subset(values, ReportingUnitCode %in% c("NSW", "Vic", "Qld", "SA", "WA", "Tas", "NT", "ACT"))

# Reorder columns
values <- values[, c("DataSetId", "ReportingUnitCode", "Ratio")]
values <- na.omit(values)
# Add a row with DataSetId: 2313, ReportingUnitCode: ACT, Ratio: NA
new_row <- data.frame(
  DataSetId = 2313,
  ReportingUnitCode = "ACT",
  Ratio = NA
)
values <- rbind(new_row, values)
values <- values[order(values$DataSetId), ]
values$Year <- rep(2011:2022, each = 7)

values_national$Year <- 2011:2022

model <- lm(values_national$Value[1:11]~budget$Current)



australian_population <- c(
  22733463, # 2011
  23130999, # 2012
  23456109, # 2013
  23789322, # 2014
  24117360, # 2015
  24446872, # 2016
  24772206, # 2017
  25088636, # 2018
  25399114, # 2019
  25687041, # 2020
  25851000, # 2021
  26119390  # 2022
)