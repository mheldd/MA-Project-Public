library(dplyr)

#clear workspace
rm(list = ls())

#run main file to get necesarry functions and parameters
source("C:/Users/manue/OneDrive/Dokumente/MA/R/ma_main.R")

##load data
setwd("C:/Users/manue/PycharmProjects/MA/MA_Project-side/results_perm_dev")

perm_dev_data <- list(read.csv("a_0.125b_1e-05_devstrat_1_all.csv", header = FALSE))

perm_dev_data[[1]]

eval_length <- 150
max_session_id <- max(perm_dev_data[[1]]$V3)

##data transformation
for (i in c(1:length(perm_dev_data))){
  data <- perm_dev_data[[i]]
  colnames(data) <- c("price_p1", "price_p2", "session_id", "num_periods")
  data$prof_1 <- profit(pricetrafo(data$price_p1), pricetrafo(data$price_p2))
  data$prof_2 <- profit(pricetrafo(data$price_p2), pricetrafo(data$price_p1))
  perm_dev_data[[i]] <- data
}


##Ok
##2 Tasks:
##einmal das Gleiche machen, wie bei imp_res_analysis
##und zweitens, die session durations und profits rausextrahieren
##wenn ich das zuerst mach, hab ich danach die gleiche Art von dataframe wie bei imp_res und kann das gleiche Zeug machen!
#check :)

session_df <- data.frame(
  session_id = integer(),
  num_periods = integer(),
  periods_till_learn = integer(),
  total_prof_p1 = integer(),
  total_prof_p2 = integer(),
  prof_pre_dev <- numeric(),
  prof_pre_nondev <- numeric(),
  prof_post_dev <- numeric(),
  prof_post_nondev <- numeric()
  
)


for (i in c(0:max_session_id)){
  session_data <- filter(perm_dev_data[[1]], session_id == i)
  misc <- c(session_data$price_p1[2*eval_length+1], session_data$price_p1[2*eval_length+2], session_data$price_p2[2*eval_length+2])
  pre <- session_data[1:eval_length,]
  post <- session_data[(eval_length+1):(2*eval_length),]
  
  #calculate discounted profits from list of prices over 150 periods pre and post deviation
  prof_pre_dev <- discount(profit(pricetrafo(pre$price_p1), pricetrafo(pre$price_p2)))
  prof_pre_nondev <- discount(profit(pricetrafo(pre$price_p2), pricetrafo(pre$price_p1)))
    
  prof_post_dev <- discount(profit(pricetrafo(post$price_p1), pricetrafo(post$price_p2)))
  prof_post_nondev <- discount(profit(pricetrafo(post$price_p2), pricetrafo(post$price_p1)))
  
  session_df <- rbind(session_df, data.frame(session_id = i, num_periods = session_data$num_periods[1], periods_till_learn = misc[1],
                                             total_prof_p1 = misc[2], total_prof_p2 = misc[3],
                                             prof_pre_dev = prof_pre_dev, prof_pre_nondev = prof_pre_nondev, prof_post_dev = prof_post_dev,
                                             prof_post_nondev = prof_post_nondev))
    
}

##apparently its not profitable lol
##that´s also a result :)
