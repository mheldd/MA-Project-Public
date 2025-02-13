library(dplyr)
library(ggplot2)
library(tidyr)

#clear workspace
rm(list = ls())

#run main file to get necessary functions and parameters
source("C:/Users/manue/OneDrive/Dokumente/MA/R/ma_main.R")

##load data
setwd("C:/Users/manue/PycharmProjects/MA/MA_Project-side/results_imp_res_multi")

imp_res_data <- list(read.csv("b_1e-05_dur_10_devact_1_all.csv", header = FALSE), read.csv("b_1e-05_dur_25_devact_1_all.csv", header = FALSE),
                     read.csv("b_1e-05_dur_10_devact_2_all.csv", header = FALSE), read.csv("b_1e-05_dur_25_devact_2_all.csv", header = FALSE),
                     read.csv("b_1e-05_dur_10_devact_3_all.csv", header = FALSE), read.csv("b_1e-05_dur_25_devact_3_all.csv", header = FALSE),
                     read.csv("b_1e-05_dur_1_devact_14_all.csv", header = FALSE), read.csv("b_1e-05_dur_1_devact_1_all.csv", header = FALSE))


##irgendwie kommt die deviation jetzt eine Runde zu spät lol.
##das is kagga. muss ich vielleicht nochmal machen
#und hab dur 1 vergessen lel


max_session_id <- max(imp_res_data[[1]]$V3)
eval_length <- 150

##data transformation
for (i in c(1:length(imp_res_data))){
  data <- imp_res_data[[i]]
  colnames(data) <- c("price_p1", "price_p2", "session_id", "num_periods")
  data$prof_1 <- profit(pricetrafo(data$price_p1), pricetrafo(data$price_p2))
  data$prof_2 <- profit(pricetrafo(data$price_p2), pricetrafo(data$price_p1))
  imp_res_data[[i]] <- data
}


#################################
##Plooooooooooot






plot_data <- list()

for (data_file in imp_res_data){
  ##vectors of zeros to add aggregate data in
  agg_dev_p <- numeric(300)
  agg_nondev_p <- numeric(300)
  ##loop through sessions to aggregate data
  for (i in c(0 : max_session_id)){
    session_data <- filter(data_file, session_id == i)
    dev_p <- session_data[, c(1)]
    nondev_p <- session_data[, c(2)]
    agg_dev_p <- dev_p + agg_dev_p
    agg_nondev_p <- nondev_p + agg_nondev_p
  }

  ##create the resulting dataframe for plot
  df <- data.frame(
    mean_agg_dev = agg_dev_p/(max_session_id+1),
    mean_agg_nondev = agg_nondev_p/(max_session_id+1),
    period = c(1:300)
  )
  nrow(data_file)
  nrow(df)
  
  ##transform data to long shape for plotting
  df_long <- pivot_longer(df, cols = c("mean_agg_dev", "mean_agg_nondev"), 
                          names_to = "Series", values_to = "Value")
  ##append transformed data to list
  plot_data <- append(plot_data, list(df_long))

}


ggplot(plot_data[[2]], aes(x = period, y = Value, color = Series)) +
  geom_line(size = 1) +
  ylim(0, 14) +
  xlim(145, 190)
  labs(
    title = "Trajectory of Two Time Series",
    x = "Time",
    y = "Value"
  ) +
  theme_minimal()
  
###die ersten 145 observations pro session kann ich ja für diese exercise schon gleich am Anfang wegschneiden. Dann geht plot auch bei 0 los :)

##Sieht eigentlich schon echt beautiful aus, muss da gar nicht mehr viel dran rumfeudeln :)
##Will ich random strat auch testen hier?
##auf jeden Fall rausfinden, warum die deviation eins zu spät kommt in Python. Und 1 period deviation auch beifügen.
##das ist so cool POGGIES :)
##Funfunfun


########################################################################################################################
##Profit
##Ich will discounted profits vorher nachher beider Spieler

#also enddata eigentlich 4 Zahlen


  
profit_data <- list()
  
for (data_file in imp_res_data){
  session_df <- data.frame(
    session_id <- integer(),
    num_periods <- integer(),
    prof_pre_dev <- numeric(),
    prof_pre_nondev <- numeric(),
    prof_post_dev <- numeric(),
    prof_post_nondev <- numeric()
  )
  
  for (i in c(0:max_session_id)){
    session_data <- filter(data_file, session_id == i)
    pre <- session_data[1:eval_length,]
    post <- session_data[(eval_length+1):(2*eval_length),]
      
    #calculate discounted profits from list of prices over 150 periods pre and post deviation
    prof_pre_dev <- discount(profit(pricetrafo(pre$price_p1), pricetrafo(pre$price_p2)))
    prof_pre_nondev <- discount(profit(pricetrafo(pre$price_p2), pricetrafo(pre$price_p1)))
      
    prof_post_dev <- discount(profit(pricetrafo(post$price_p1), pricetrafo(post$price_p2)))
    prof_post_nondev <- discount(profit(pricetrafo(post$price_p2), pricetrafo(post$price_p1)))
      
    session_df <- rbind(session_df, data.frame(session_id = i, num_periods = session_data$num_periods[1],
                                                 prof_pre_dev = prof_pre_dev, prof_pre_nondev = prof_pre_nondev, prof_post_dev = prof_post_dev,
                                                 prof_post_nondev = prof_post_nondev))
    
  }
  profit_data <- append(profit_data, list(session_df))
}

test <- profit_data[[6]]


mean(test$prof_pre_dev)
mean(test$prof_post_dev)
mean(test$prof_pre_nondev)
mean(test$prof_post_nondev)
###yesss, das isses. Damit kann ich dann auch alle Differenzen usw. berechnen.
##Relativer Gewinn ist größer kann man arguen lol. Kann zu edge über competitor führen. Yeesss economic reasoning xD.
##Voll geil :) 

##Das ist richtig geilo schmeilo Pog :)
##Wenn ich discounte, sind cycles ja eh egal, weildie keinen klaren Startpunkt haben. Deswegen ist das der leichtere und gleichzeitig auch bessere approach :)
##Datenanalyse jetzt schon durchgespielt lolololol

##Eigentlich hab ich alles..

