library(RPostgres)
library(readxl)
library(dplyr)
library(dbplyr)

budget_state_per_capital <- read_excel("Downloads/aihw-93-Health-expenditure-Australia-2021-2022.xlsx", 
                                                             sheet = "Table 5", range = "A1:X14")
budget_state_per_capital <- budget_state_per_capital[-c(1,2), - c(3,4,6,7,9,10,12,13,15,16,18,19,21,22,24)]
colnames(budget_state_per_capital) <- c("Year","NSW", "Vic", "Qld", "WA", "SA", "Tas", "NT", "NAT")
budget_state_per_capital$Year <- 2011:2021
budget_state_per_capital <- budget_state_per_capital[, c(ncol(budget_state_per_capital), 1:(ncol(budget_state_per_capital) - 1))]
budget_state_per_capital <- as.data.frame(budget_state_per_capital)
budget_state_per_capital <- budget_state_per_capital[, order(names(budget_state_per_capital))]

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

#Elimino gli ospedali e tengo gli stati e la nazione
values_national <- values %>%
  filter(ReportingUnitCode %in% c("NSW", "Vic", "Qld", "SA", "WA", "Tas", "NAT"))

values_national <- values_national[1:84,]
values_wide <- dcast(values_national, DataSetId ~ ReportingUnitCode, value.var = "Value")
values_wide <- values_wide[, order(names(values_wide))]
values_wide$Year <- 2011:2022
values_wide <- subset(values_wide, select= -DataSetId)

# Reorder columns such that the last column becomes the first column
values_wide <- values_wide[, c(ncol(values_wide), 1:(ncol(values_wide) - 1))]
values_wide <- values_wide[-12,]
# Initialize an empty list to store the models
models <- list()

# Loop through each column (starting from the second column)
for (i in 2:ncol(values_wide)) {
  # Create a formula for the linear model
  formula <- as.formula(paste(names(values_wide)[i], "~", names(budget_state_per_capital)[i]))
  
  # Fit the linear model
  model <- lm(formula, data = cbind(values_wide, budget_state_per_capital))
  
  # Store the model in the list
  models[[names(values_wide)[i]]] <- model
}

