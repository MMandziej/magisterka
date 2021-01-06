require(shiny) #loads shiny package
shiny::runApp("load_merged_results_pc.R", launch.browser = FALSE, port = 8087, host = "0.0.0.0") #runs shiny app in port 8087 localhost