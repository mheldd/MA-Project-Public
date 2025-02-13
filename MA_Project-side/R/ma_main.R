##Start

##This file is for necessarry functions and parameters.
##Needs to be run for the other files to work.

delta <- 0.95
a <- 2
my <- 1/4
cst <- 1
prices <- c(1.427725,   1.46647214, 1.50521929, 1.54396643, 1.58271357, 1.62146071,
           1.66020786, 1.698955,   1.73770214, 1.77644929, 1.81519643, 1.85394357,
           1.89269071, 1.93143786, 1.970185)



prices[15]

profit <- function(pi, pj) {
  demand <- (exp((a-pi)/my))/(exp((a-pi)/my)+exp((a-pj)/my)+1)
  prof <- demand*(pi-cst)
  return(prof)
}

pricetrafo <- function(p){
  price <- prices[p+1]
  return(price)
}

detect_cycle <- function(prices) {
  for (i in c(1:8)){
    a <- c(prices[1:(2*i)], prices[1:(2*i)], prices[1:(2*i)])
    b <- prices[1:(6*i)]
    print(i)
    print("a")
    print(a)
    print("b")
    print(b)
    if (identical(a, b)) {
      return(i)
      break
    }
  }
  return(99)
}

discount <- function(profit_series){
  disc_sum <- 0
  n <-0
  for (i in profit_series){
    disc_sum = i*(delta^n) + disc_sum
    n = n + 1
  }
  return(disc_sum)
}


pinash <- profit(1.47293, 1.47293)
pimono <- profit(1.92498, 1.92498)

delprof <- function(average_profit){
  return((average_profit-pinash)/(pimono-pinash))
}

