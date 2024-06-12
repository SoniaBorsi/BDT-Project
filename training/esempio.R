library(RPostgres)
library(readxl)
library(dplyr)
library(dbplyr)
library(reshape2)
#Da riscrivere per ottenere il file a prescindere dalla cartella Downloads.
#Ho preso direttamente le sezioni A1:X14
budget_state_per_capital <- read_excel("Downloads/aihw-93-Health-expenditure-Australia-2021-2022.xlsx", 
                                                             sheet = "Table 5", range = "A1:X14")
#Ottengo le colonne e righe necessarie
budget_state_per_capital <- budget_state_per_capital[-c(1,2), - c(3,4,6,7,9,10,12,13,15,16,18,19,21,22,24)]
#Rinomino le colonne
colnames(budget_state_per_capital) <- c("Year","NSW", "Vic", "Qld", "WA", "SA", "Tas", "NT", "NAT")
#Riscrivo la colonna anno
budget_state_per_capital$Year <- 2011:2021
#Ordino le colonne in ordine alfabetico
budget_state_per_capital <- budget_state_per_capital[, order(names(budget_state_per_capital))]
#Metto la colonna anno come prima colonna
budget_state_per_capital <- budget_state_per_capital[, c(ncol(budget_state_per_capital), 1:(ncol(budget_state_per_capital) - 1))]
#Mi assicuro che sia un data.frame
budget_state_per_capital <- as.data.frame(budget_state_per_capital)


# Ottengo i dati da PostgreSQL
con <- dbConnect(RPostgres::Postgres(),
                 host = "localhost",
                 port = 5433,
                 user = "user",
                 password = "password",
                 dbname = "mydatabase")

#Visualizzo la lista delle tabelle
dbListTables(con)

#Ottengo la tabella values
values <- dbGetQuery(con, "SELECT * FROM values")

#Elimino gli ospedali e tengo gli stati e la nazione
values_national <- values %>%
  filter(ReportingUnitCode %in% c("NSW", "Vic", "Qld", "SA", "WA", "Tas", "NAT"))

#Elimino delle ripetizioni
values_national<- values_national[1:84,]
#Cambio la natura della tabella
values_wide <- dcast(values_national, DataSetId ~ ReportingUnitCode, value.var = "Value")
#Elimino la colonna DataSetId
values_wide <- subset(values_wide, select= -DataSetId)
#Ordino le colonne in ordine alfabetico
values_wide <- values_wide[, order(names(values_wide))]
#Aggiungo la colonna anno
values_wide$Year <- 2011:2022
#Metto la colonna anno come prima colonna
values_wide <- values_wide[, c(ncol(values_wide), 1:(ncol(values_wide) - 1))]
#Elimino un l'anno 2022 così che sia uguale al dataset della spesa sanitaria
values_wide <- values_wide[-12,]

#Inizio a fittare i modelli

# Initialize an empty list to store the models
models <- list()
coefficients_list <- list()
# Loop through each column (starting from the second column)
for (i in 2:ncol(values_wide)) {
  # Create a formula for the linear model
  x <- as.numeric(budget_state_per_capital[,i])
  y <- as.numeric(values_wide[,i])
  
  # Fit the linear model
  model <- lm(y~x)
  
  # Store the model in the list
  models[[names(values_wide)[i]]] <- model
  
  coefficients_list[[i]] <- coef(model)
}

#Australian population prediction
Population_prediction <- read_excel("Downloads/Projected population, Australia.xlsx", 
                                    range = "A2:D31")
Population_prediction <- as.data.frame(Population_prediction)
Population_historic <- read_excel("Downloads/ABS_ERP_COMP_Q_1.0.0_10..Q.xlsx", 
                                        range = "B8:D51", col_names = FALSE)
Population_historic <- Population_historic[,-2]
colnames(Population_historic) <- c("Year", "Population")
Population_historic <- Population_historic %>%
  filter(grepl("Q1", Year))
Population_historic$Year <- 2011:2021
Population_historic <- as.data.frame(Population_historic)
Population_historic[,2] <- as.numeric(Population_historic[,2])
Population_historic[,2] <- as.numeric(Population_historic[,2])*(rep(1000, times = 11))


#Otteniamo tre previsioni diverse per il budget a seconda dei tre scenari della popolazione

modello_budget <- lm(budget_state_per_capital$NAT~Population_historic$Population)
intercept <- coef(modello_budget)[1]
slope <- coef(modello_budget)[2]
# Create three different prediction models
predictions_high <-   intercept + slope * Population_prediction$`High series`
predictions_medium <- intercept + slope * Population_prediction$`Medium series`
predictions_low <- intercept + slope * Population_prediction$`Low series`

surgeries_pred_state_low <- list()
surgeries_pred_state_medium <- list()
surgeries_pred_state_high <- list()
surgeries_pred_state <- list()
for (i in 2:length(models)){
  intercept <- coefficients_list[[i]][1]
  slope <- coefficients_list[[i]][2]
  
  surgeries_pred_state_high[[names(values_wide)[i]]][[names(values_wide)[i]]] <-   intercept + slope * predictions_high
  surgeries_pred_state_medium[[names(values_wide)[i]]] <- intercept + slope * predictions_medium
  surgeries_pred_state_low[[names(values_wide)[i]]] <- intercept + slope * predictions_low
  surgeries_pred_state[[names(values_wide)[i]]] <- list(surgeries_pred_state_high,surgeries_pred_state_medium,surgeries_pred_state_low)
}

