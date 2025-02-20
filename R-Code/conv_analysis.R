library(dplyr)
library(knitr)

profit(pimono,pimono)
#clear workspace
rm(list = ls())

#run main file to get necesarry functions and parameters
source("C:/Users/manue/OneDrive/Dokumente/MA/R/ma_main.R")

##load data
setwd("C:/Users/manue/PycharmProjects/MA/Py-Code/results_conv")


conv_data <- list(
  read.csv("a_0.1_b_2e-05_q_99_all.csv", header = FALSE),
  read.csv("a_0.1_b_1e-05_q_99_all.csv", header = FALSE),
  read.csv("a_0.1_b_7e-06_q_99_all.csv", header = FALSE),
  read.csv("a_0.125_b_2e-05_q_99_all.csv", header = FALSE),
  read.csv("a_0.125_b_1e-05_q_99_all.csv", header = FALSE),
  read.csv("a_0.125_b_7e-06_q_99_all.csv", header = FALSE),
  read.csv("a_0.15_b_2e-05_q_99_all.csv", header = FALSE),
  read.csv("a_0.15_b_1e-05_q_99_all.csv", header = FALSE),
  read.csv("a_0.15_b_7e-06_q_99_all.csv", header = FALSE)
)


profit(1.47,1.47)

##data transformation
for (i in c(1:length(conv_data))){
  data <- conv_data[[i]]
  colnames(data) <- c("price_p1", "price_p2", "session_id", "num_periods")
  data$prof_1 <- profit(pricetrafo(data$price_p1), pricetrafo(data$price_p2))
  data$prof_2 <- profit(pricetrafo(data$price_p2), pricetrafo(data$price_p1))
  conv_data[[i]] <- data
}


session_df_list <- list()

for (d in conv_data){
  session_df <- data.frame(
    session_id = integer(),
    av_price = integer(),
    av_profit = numeric(),
    cycle_len = integer(),
    num_periods = integer()
  )
  for (i in c(0 : max(d$session_id))){
    session_data <- filter(d, session_id == i)
    session_prices <- session_data[,c(1,2)]
    vector_representation <- as.vector(t(session_prices))
    len <- detect_cycle(vector_representation)
    
    if (len == 99){
      eval <- session_prices
      len <- NA
    }
      else {
        eval <- session_prices[c(1:len),]
      }
    
    prof <- (profit(pricetrafo(eval$price_p1), pricetrafo(eval$price_p2)) + profit(pricetrafo(eval$price_p2), pricetrafo(eval$price_p1)))/2
    agg <- (eval$price_p1+eval$price_p2)/2
    session_df <- rbind(session_df, data.frame(session_id = i, av_price = mean(agg), av_profit = mean(prof), cycle_len = len, num_periods = session_data$num_periods[1]))
  }
  session_df_list <- append(session_df_list, list(session_df))
}

################
###Find longest and shortest session
most <- c()
least <- c()
for (x in session_df_list){
  most <- append(most, max(x$num_periods))
  least <- append(least, min(x$num_periods))
}
print(max(most))
print(min(least))
##############
###how many sessions show no cycle?


av_df <- data.frame(
profit_average = numeric(),
price_average = numeric(),
average_periods = integer(),
average_cycle_length = numeric(),
no_cycle = integer()
)

for (s in session_df_list){
  av_av_profit = round(mean(s$av_profit), digits = 3)
  av_av_price =  round(mean(s$av_price), digits = 1)
  av_periods = round(mean(s$num_periods), digits = 0)
  av_cycle = round(mean(s$cycle_len, na.rm = TRUE), digits = 1)
  no_cycle = sum(is.na(s$cycle_len))
  av_df <- rbind(av_df, data.frame(profit_average = av_av_profit, price_average = av_av_price, average_periods = av_periods, average_cycle_length = av_cycle, no_cycle = no_cycle))
}

###number of sessions with no cycle
no_cycle <- av_df$no_cycle
print(no_cycle)

av_df$no_cycle <- NULL


###Declare row names for latex table
parameter_names <- c(
  "$\\alpha = 0.1, ~ \\beta = 2\\times10^{-5}$",
  "$\\alpha = 0.1, ~ \\beta = 10^{-5}$",
  "$\\alpha = 0.1, ~ \\beta = 7\\times10^{-6}$",
  "$\\alpha = 0.125, ~ \\beta = 2\\times10^{-5}$",
  "$\\alpha = 0.125, ~ \\beta = 10^{-5}$",
  "$\\alpha = 0.125, ~ \\beta = 7\\times10^{-6}$",
  "$\\alpha = 0.15, ~ \\beta = 2\\times10^{-5}$",
  "$\\alpha = 0.15, ~ \\beta = 10^{-5}$",
  "$\\alpha = 0.15, ~ \\beta = 7\\times10^{-6}$"
)

###Add number of observations as another column
av_df <- av_df %>%
  add_column(parameters = parameter_names, .before = "profit_average") %>%
  add_column(n_sessions= 84, .after = "average_cycle_length")

##Declare column names
c_names <- c("Parameters", "Average Profit", "Average Price", "Average Periods", "Average Cycle Length", "Number of Sessions")

##Create Latex Table
kable(av_df, format = "latex", escape = FALSE, booktabs = TRUE, sep = "", align = "l|ccccc",
      col.names = c_names, caption = "An example table caption.")


#################################################################
#Histogram for price level analysis:



combined <- append(conv_data[[5]]$price_p1, conv_data[[5]]$price_p2)
combined <- data.frame(values = combined)

quant <- quantile(combined, probs = c(0,0.25,0.5,0.75,1))
quant

library(ggplot2)

ggplot(combined, aes(x=values, y=after_stat(density * 100))) +
  geom_histogram(aes(y=after_stat(density * 100)), binwidth = 1, fill="skyblue", color="black") +
  labs(title="", x="Prices", y="Percentage") +
  theme_minimal()

setwd("C:/Users/manue/OneDrive/Dokumente/MA/Thesis_tex")

ggsave("histogram.pdf", width=6, height=4)








