cut_off_distribution_table = function(results_list,
                                      red_cut_off=0.3,
                                      amber_cut_off=0.7){
  
  # DIVIDE TRAIN AND TEST DATA
  train_dataset <- results_list[[2]]
  test_dataset <- results_list[[1]]
  
  # GET SUM OF POSITIVE OBSERVATIONS ON BOTH DATASETS
  train_labels <- sum(train_dataset$Label)
  test_labels <- sum(test_dataset$Label)
  
  # DISTINGUISH CUT OFFS
  red_train <- train_dataset %>% filter(X_coordinates <= red_cut_off)
  red_test <- test_dataset %>% filter(X_coordinates <= red_cut_off)
  amber_train <- train_dataset %>% filter(X_coordinates > red_cut_off, X_coordinates <= amber_cut_off)
  amber_test <- test_dataset %>% filter(X_coordinates > red_cut_off, X_coordinates <= amber_cut_off)
  green_train <- train_dataset %>% filter(X_coordinates > amber_cut_off)
  green_test <- test_dataset %>% filter(X_coordinates > amber_cut_off)
  
  # CALCULATE ERROR COUNTS AND PERCENTAGES IN BUCKEST
  buckets <- c('Red', 'Amber', 'Green')
  cases_count_train <- c(nrow(red_train), nrow(amber_train), nrow(green_train))
  error_count_train <- c(sum(red_train$Label), sum(amber_train$Label), sum(green_train$Label))
  error_perc_train <- c(round(sum(red_train$Label) / train_labels, 3)*100,
                        round(sum(amber_train$Label) / train_labels, 3)*100,
                        round(sum(green_train$Label) / train_labels, 3)*100)

  cases_count_test <- c(nrow(red_test), nrow(amber_test), nrow(green_test))
  error_count_test <- c(sum(red_test$Label), sum(amber_test$Label), sum(green_test$Label))
  error_perc_test <- c(round(sum(red_test$Label) / test_labels, 3)*100,
                       round(sum(amber_test$Label) / test_labels, 3)*100,
                       round(sum(green_test$Label) / test_labels, 3)*100)
  
  # create output table
  output_table <- data.frame(buckets, cases_count_train, error_count_train, error_perc_train,
                             cases_count_test, error_count_test, error_perc_test)
  
  names(output_table)[names(output_table) == "buckets"] <- "Bucket"
  names(output_table)[names(output_table) == "cases_count_train"] <- "Cases train [count]"
  names(output_table)[names(output_table) == "error_count_train"] <- "Errors train [count]"
  names(output_table)[names(output_table) == "error_perc_train"] <- "Errors train [%]"
  names(output_table)[names(output_table) == "cases_count_test"] <- "Cases test [count]"
  names(output_table)[names(output_table) == "error_count_test"] <- "Errors test [count]"
  names(output_table)[names(output_table) == "error_perc_test"] <- "Errors test [%]"
  
  return(output_table)
}