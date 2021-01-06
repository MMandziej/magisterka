# Setting up dashboard
ui <- dashboardPage(
  skin = 'blue',
  dashboardHeader(title = "PQC Monitoring - LK",
                  dropdownMenuOutput("messageMenu")),
  # Setting up side bar on the left
  dashboardSidebar(sidebarMenu(
    menuItem("Overview", tabName = "stats", icon = icon("stats", lib = "glyphicon")),
    menuItem("Model Performance", tabName = "modelperformance", icon = icon("wrench", lib = "glyphicon")),
    menuItem("Population comparison", tabName = "pop_comparison", icon = icon("scale", lib="glyphicon")),
    menuItem("QC comparison", tabName = "qc_comparison", icon = icon("child", lib="font-awesome"))
  )),
  
  # Setting up dashboard body
  dashboardBody(
    includeCSS("scripts/custom_boat.css"),
    tabItems(
      # First tab content - Overview
      tabItem(tabName = "stats",
              # column(6, offset = 4, titlePanel(paste("Distribution of cases - " , Sys.Date()))),
              fluidRow(
                valueBoxOutput("cases_scored"),
                valueBoxOutput("cases_completed"),
                valueBoxOutput("cases_sent_to_review")
              ),
              # Overview - Filter on time aggregation
              fluidRow(
                column(width = 2, offset = 0,
                       align = "left",
                       selectInput("time_frame", "Select time aggregation",
                                   choices = c('days', 'weeks'))),
                
                column(width = 3,
                       dateRangeInput("daterange1", "Select time range",
                                      start = "2020-01-28", end = Sys.Date()+1,
                                      min = "2020-01-28", max = Sys.Date()+1))),
              # Plot of cases statistics
              fluidRow(
                plotlyOutput('plot')),
              
              # Production savings user inputs and summary table
              pageWithSidebar(
                headerPanel(h1('Time and cash savings generated on production stage', align = "center")),
                #br(), br(),
                sidebarPanel(
                  width = 4,
                  numericInput('avg_proc_time', 'Average case processing time (hours)', 1, min = 0.5, max = 8),
                  numericInput('cost_rate', 'Hourly cost rate of signatory work (PLN)', 300, min = 100, max = 1000)
                ),
                mainPanel(DT::dataTableOutput("production_savings"),  width = 4)
              )
      ),
      
      # Second tab content - Model performance
      tabItem(tabName = "modelperformance",
              fluidPage(column(10, offset = 4, titlePanel("Model performance vs time"))),
              # User inputs
              fluidRow(#column(width = 2,
                #        selectInput("perf_chart_time", "Select time aggregation",
                #                    choices = c('weeks', 'days'))),
                column(width = 2,
                       selectInput("main_plot_type", "Select chart type",
                                   choices = list('Model performance' = 'model_performance',
                                                  'Average score' = 'average_score'),
                                   selected = 'model_performance')),
                column(width = 3,
                       sliderInput("threshold", "Select percent of population [%]",
                                   min=0, max = 100, value=75))),
              
              # Weekly Average scores main plot
              fluidRow(column(width=12, plotlyOutput('main_plot'))),
              
              # Weekly Average scores table with results per period 
              fluidPage(column(10, offset = 3, titlePanel("Model performance vs [%] population selected"))),
              fluidRow(column(width = 10, offset = 1, DT::dataTableOutput("table"))),
              
              # Monitoring production data plot
              fluidPage(column(11, offset = 4, titlePanel("Production data - summary"))),
              fluidRow(column(width=10, offset = 1, plotlyOutput('production_plot'))),
              
              ### NEXT SECTION - FEATURE DISTRIBUTION VS TIME ### 
              fluidPage(column(10, offset = 4, titlePanel("Features distribution vs time"))),
              # User inputs
              fluidRow(column(width = 2, selectInput("barchart_time", "Select time aggregation",
                                                     choices = c('weeks', 'days'))),
                       column(width = 2,
                              selectInput("barchart_feature", "Select feature",
                                          choices = colnames(general_data)[! colnames(general_data) %in% c(
                                            'GRID', 'DRSentToQCDate', 'BackupTime', 'QCAssignedName', 'week')])),
                       column(width = 3, dateRangeInput("barchart_date_range", "Select time range",
                                                        start = "2020-06-01", end = Sys.Date(),
                                                        min = "2020-06-01", max = Sys.Date()))),
              
              # Stacked bar chart histogram test side by side
              fluidRow(column(6, plotlyOutput('barchart_classes_prop_T')),
                       column(6, plotlyOutput('barchart_classes_prop_F'))),
              
              ### NEXT SECTION - HISTOGRAM PER LABEL AND K-S TEST ###
              fluidPage(column(10, offset = 4, titlePanel("Features distribution vs label distribution"))),
              # User inputs
              fluidRow(column(2, selectInput("histogram_time", "Select time aggregation",
                                             choices = c('weeks', 'days'))),
                       column(2, selectInput("histogram_feature", "Select feature",
                                             choices = colnames(general_data)[! colnames(general_data) %in% c(
                                               'GRID', 'DRSentToQCDate', 'BackupTime', 'QCAssignedName', 'week')])),
                       column(2, selectInput("selected_time", "Select specific time",
                                             choices = sort(unique(general_data$BackupTime)), width = '80%')), # possible to make more narrow
                       column(2, selectInput("selected_time_lag", "Select specific time to compare distribution",
                                             choices = sort(unique(general_data$BackupTime)), width = '80%'))), # possible to make more narrow
              # Histogram chart and Kolmogorov-Smirnov results
              fluidRow(column(6, plotlyOutput("histogram_classes")),
                       strong("Kolmogorov-Smirnov test of distribution stability in time:"), # Title
                       column(6,
                              fluidPage(htmlOutput("distribution_test")),
                              br(), br(),
                              strong("Average scores and feature distribution stability in last period:"),
                              fluidPage(
                                useShinyalert(),
                                actionButton(offset = 1, "pqc_alert", "Check scores values"),
                                useShinyalert(),  
                                actionButton(offset = 1, "dist_alert", "Check features distribution"))))#,
              # Alerts
      #         fluidPage(column(4,
      #                          useShinyalert(),  
      #                          actionButton("pqc_alert", "Check scores values")),
      #                   column(4,
      #                          useShinyalert(),  
      #                          actionButton("dist_alert", "Check feature distribution values"))),
      ),
   
      # Third tab content - population comparison
      tabItem(
        tabName = "pop_comparison",
        fluidPage(column(10, offset = 4, titlePanel("Sent to QC vs discarded cases"))),
        
        # Pop comparison main plot
        fluidRow(column(width=12, plotlyOutput('main_plot_pop_comparison'))),
        
        # Weekly Average scores table with results per period 
        fluidPage(column(10, offset = 4, titlePanel("Error amounts table"))),
        fluidRow(column(width = 9, offset = 1, DT::dataTableOutput("table_pop_comparison")))
      ),
      
      # Fourth tab content - QC Comparison
      tabItem(
        tabName = "qc_comparison",
        fluidRow(
          # User inputs
          column(1, selectInput("person", "Select filter type",
                                choices = c('QC', 'Analyst'), selected='QC')),
          
          column(4, selectInput("QC_name", "Select person name",
                                choices = unique(general_data$QCAssignedName))),
          column(4, offset = 1, selectInput("QC_name2", "Select person name",
                                            choices = unique(general_data$QCAssignedName)))),
        # QC tables side by side
        fluidRow(
          column(6, DT::dataTableOutput('cases_of_qc')),
          column(6, DT::dataTableOutput('cases_of_qc2'))),
        # User inputs
        fluidRow(column(4, selectInput("QC_feature", "Select feature",
                                       choices = colnames(general_data)[! colnames(general_data) %in% c(
                                         'GRID', 'DRSentToQCDate', 'BackupTime', 'QCAssignedName', 'week')])),
                 column(width = 8,
                        dateRangeInput("daterange_QC1", "Select time range",
                                       start = substr(
                                         as.character(min(general_data$BackupTime)),
                                         1, 10),
                                       end = Sys.Date(),
                                       min = substr(
                                         as.character(min(general_data$BackupTime)), 1, 10),
                                       max = Sys.Date()))),
        # Feature impact charts for each label class 
        fluidRow(
          column(6, plotlyOutput('histogram_exploratory_analysis_QC')),
          column(6, plotlyOutput('histogram_exploratory_analysis_QC2'))),
        # Impact table with average scores for each class and loess chart 
        fluidRow(
          column(12, DT::dataTableOutput('impact_on_score_dt'))),
        fluidRow(
          column(12, plotlyOutput("feature_impact")))
      )
    )
  )
)


server <- function(input, output, session) {
  ### Alerts ###
  #unique_intervals <- sort(unique(full_backlog$pqc_timestamp))
  #mean_lastn <- mean(full_backlog[full_backlog$pqc_timestamp == unique_intervals[length(unique_intervals)], ][['pqc']])
  #quants <- quantile(full_backlog[full_backlog$pqc_timestamp < unique_intervals[length(unique_intervals)], ][['pqc']], probs=c(0.25, 0.75))

  # Calculate number of cases discarded from QC review
  discared_cases <- reactive({
    disc_cases <- nrow(full_backlog %>% filter(Stage == 'production',
                                               Should_be_send_to_QC == "0"))
    disc_cases
  })

  observeEvent(input$pqc_alert, {
    out <- dist_alert_check(results = full_backlog,
                            dataset = general_data,
                            time_feat = 'BackupTime',
                            time_frame = 'days')
    
    shinyalert("Latest scores assesment:", out[[3]],
               type = 'info', timer = 5000, html = TRUE, imageWidth = 200, imageHeight = 200)
  })
  
  observeEvent(input$dist_alert, {
    out <- dist_alert_check(results = full_backlog,
                            dataset = general_data,
                            time_feat = 'BackupTime',
                            time_frame = 'days')
    
    shinyalert("Feature distribution assesment:",
               paste(out[[1]], out[[2]]),
               type = 'info', timer = 5000, html = TRUE, imageWidth = 200, imageHeight = 200)
  })
  
  
  ### Overview tab ###
  output$cases_scored <- renderValueBox({
    valueBox(nrow(full_backlog), subtitle="Number of cases scored",
             icon("tasks", lib="glyphicon"), color="green")
  })
  
  output$cases_completed <- renderValueBox({
    valueBox(nrow(subset(full_backlog, subset=!(Stage=='production'))) + sum(stats$count_completed),
             subtitle="Number of cases completed",
             icon("thumbs-up", lib="glyphicon"), color="orange")
  })
  
  output$cases_sent_to_review <- renderValueBox({
    valueBox(
      nrow(subset(full_backlog, subset=!(Stage=='production'))) +
        sum(subset(full_backlog, Stage=='production')$Should_be_send_to_QC == 1),
      subtitle="Number of cases sent to QC",
      icon("share-alt", lib="glyphicon"), color="blue")
  })
  
  stats_react = reactive({
    stats$date = floor_date(stats$date, unit = input$time_frame)
    stats = stats %>% group_by(date) %>%
      summarize(count_sent_qc = sum(count_sent_qc),
                count_completed = sum(count_completed),
                count_scored = sum(count_scored))
    as.data.frame(stats)
    stats_filtered <- filter(stats, date >= input$daterange1[1] & date < input$daterange1[2])
  })
  
  # Production savings table
  output$production_savings <- DT::renderDataTable({
    data <- calculate_production_savings(no_cases_discarded = discared_cases(),
                                         avg_proc_time = input$avg_proc_time,
                                         cost_rate = input$cost_rate)
    data
  }, rownames = FALSE)
  
  ### Model performance tab ###
  bar_chart_time_periods <- reactive({
    tp <- sort(unique(floor_date(general_data$BackupTime, unit=input$histogram_time))) 
    tp
  })
  
  # feature distribution charts
  wf_to_score_final_selected_features = reactive({
    if (input$barchart_time == 'weeks') {
      wf_to_score_final <- filter(general_data, week >= input$barchart_date_range[1] & week < input$barchart_date_range[2]) # a / a_merged
    } else {
      wf_to_score_final <- filter(general_data, BackupTime >= input$barchart_date_range[1] & BackupTime < input$barchart_date_range[2]) # a / a_merged
    }
    wf_to_score_final
  })
  
  # histogram stacked chart
  histogram_data = reactive({
    tp <- general_data[which(floor_date(general_data$BackupTime,
                                        unit = input$histogram_time)==as.POSIXct(input$selected_time)),]
    tp
  })
  
  observe(
    updateSelectInput(session, inputId = "selected_time", choices = bar_chart_time_periods())
  )
  
  observe(
    updateSelectInput(session, inputId = "selected_time_lag", choices = bar_chart_time_periods())
  )
  
  # Overview chart
  output$plot <- renderPlotly(
    plot_ly(stats_react(), x = ~as.character(date), y = ~count_sent_qc, type = 'bar', name = 'Sent to QC') %>%
      add_trace(y = ~count_scored, name = 'Scored Cases') %>%
      add_trace(y = ~count_completed, name = 'Completed Cases') %>%
      layout(yaxis = list(title = HTML('<b>Number of cases</b>')), barmode = 'group',
             xaxis = list(title = HTML('<b>Completed Date</b>')), barmode = 'group')
  )
  
  # Model performance in time chart
  output$main_plot <- renderPlotly({
    main_plot_vs_time(full_backlog = full_backlog,
                      threshold = input$threshold / 100,
                      type = input$main_plot_type) # c('model_performance', 'average_score')
    #time_frame = input$perf_chart_time) # c('weeks', 'days')
  })
  
  # Model summary table
  output$table <- DT::renderDataTable({
    data <- create_summary_stages_table(full_backlog = full_backlog,
                                        threshold = input$threshold / 100)
    data
  })
  
  # Plot of production data
  output$production_plot <- renderPlotly({
    cases_avg_score_plot(scored_cases_backlog = full_backlog)
  })
  
  # Side by side barcharts vs time - distribution plot
  output$barchart_classes_prop_T = renderPlotly({
    new_plot <- barchart_classes(dataset = wf_to_score_final_selected_features(),
                                 time_feature = 'BackupTime',
                                 feature = input$barchart_feature,
                                 time_frame = input$barchart_time,
                                 prop = T)
    
    new_plot <- layout(new_plot,
                       title = HTML(paste("<b>Class percentage shares of", input$barchart_feature, "vs time</b>")),
                       xaxis = list(title = HTML("<b>Completed date</b>")),
                       yaxis = list(title = HTML("<b>% of cases for each group</b>")))
  })
  # Side by side barcharts vs time - count plot
  output$barchart_classes_prop_F = renderPlotly({
    new_plot <- barchart_classes(dataset = wf_to_score_final_selected_features(),
                                 time_feature = 'BackupTime',
                                 feature = input$barchart_feature,
                                 time_frame = input$barchart_time,
                                 prop = F)
    
    new_plot <- layout(new_plot,
                       title = HTML(paste("<b>Class numbers of", input$barchart_feature, "vs time</b>")),
                       xaxis = list(title = HTML("<b>Completed date</b>")),
                       yaxis = list(title = HTML("<b>Number of cases for each group</b>")))
  })
  
  # Side by side histogram specific time and KS test
  output$histogram_classes = renderPlotly({
    hist_plot <- histogram_exploratory_analysis(feature = input$histogram_feature,
                                                dataset = histogram_data(), 
                                                bins = 50,
                                                Label = T)
    hist_plot <- layout(hist_plot,
                        title = HTML(paste("<b>Histogram of", input$histogram_feature, "</b>")),
                        xaxis = list(title = HTML("<b>", input$histogram_feature, "</b>")),
                        yaxis = list(title = HTML("<b>Number of cases</b>")))
  })
  
  # Kolmogorov-Smirnov distribution stability test
  output$distribution_test <- renderText({
    decision <- dist_check_new(dataset = general_data,
                               time_feat = 'BackupTime',
                               feature = input$histogram_feature,
                               time_frame = input$histogram_time, #weeks/days
                               selected_time = as.POSIXct(input$selected_time),
                               selected_lag_time = as.POSIXct(input$selected_time_lag))
    
    # Paste HTML formatted decision on the basis of funcion result
    if (grepl("No enough data", decision) == T) {
      paste(HTML("<font color=\"#eb9234\"><b>Not enough data</b></font>",
                 str_sub(decision, start = 15)))
    } else if (grepl("assumptions for Chi-Squared homogenity tests were violated", decision) == T) {
      paste(HTML("<font color=\"#eb9234\"><b>Statistical assumptions for Chi-Squared homogenity tests were violated.</b></font>",
                 str_sub(decision, start = 72)))
    } else if (grepl("No statistically significant", decision) == T) {
      paste(HTML("<font color=\"#1fb864\"><b>No statistically significant difference</b></font>",
                 str_sub(decision, start = 40)))
    } else {
      paste(HTML("<font color=\"#FF0000\"><b>Statistically significant difference</b></font>",
                 str_sub(decision, start = 37)))}
  })
  
  ### Population comparison tab ###
  # Population comparison main plot
  output$main_plot_pop_comparison <- renderPlotly({
    main_plot_vs_time_pop_comparison(full_backlog = full_backlog)
  })
  
  # Population comparison error table
  output$table_pop_comparison <- DT::renderDataTable({
    
    production_dataset <- full_backlog
    production_data <- production_dataset %>% filter(Stage == 'production') %>% group_by(Should_be_send_to_QC) %>%
      summarize(CasesCount=n(),
                LabelCount = sum(Label=="1"),
                ErrorRate = 100 * sum(Label=="1") / CasesCount
      )
    data <- data.frame(
      c("Not sent to QC", "Sent to QC"),
      production_data$CasesCount,
      production_data$LabelCount,
      paste(round(production_data$ErrorRate, 2), "%", sep="")
    )
    colnames(data) <- c("Dataset", "Cases amount", "Error amount", "Error rate")
    data
  })
  
  
  ### QC Comparison tab ###
  # Update user inuts 
  observe({
    if (input$person != 'QC') {
      updateSelectInput(session, "QC_name", choices = unique(general_data$AnalystAssignedName))
      updateSelectInput(session, "QC_name2", choices = unique(general_data$AnalystAssignedName), 'All')
    } else {
      updateSelectInput(session, "QC_name", choices = unique(general_data$QCAssignedName))
      updateSelectInput(session, "QC_name2", choices = unique(general_data$QCAssignedName), 'All')
    }
  })
  
  # QC table side by side
  general_data_react = reactive({
    general_data_react <- filter(general_data, BackupTime >= as.Date(input$daterange_QC1[1]) &
                                   BackupTime < as.Date(input$daterange_QC1[2]))
    general_data_react
  })
  
  output$cases_of_qc = DT::renderDataTable({
    if(input$person == 'QC') {
      dataset = general_data_react() %>%
        filter(QCAssignedName == input$QC_name)
    } else {
      dataset = general_data_react() %>%
        filter(AnalystAssignedName == input$QC_name)
    }
    datatable(dataset,
              options = list(scrollX=T,
                             columnDefs=list(list(className="dt-center"))))
  })
  
  output$cases_of_qc2 = DT::renderDataTable({
    if(input$person == 'QC') {
      if(input$QC_name2 != 'all'){
        dataset = general_data_react() %>%
          filter(QCAssignedName == input$QC_name2)
      } else {
        dataset = general_data_react() }
    } else {
      if(input$QC_name2 != 'all'){
        dataset = general_data_react() %>%
          filter(AnalystAssignedName == input$QC_name2)
      } else {
        dataset = general_data_react()
      }
    }
    datatable(dataset, options = list(scrollX=T,
                                      columnDefs=list(list(className="dt-center"))))
  })
  
  # Impact plot per label side by side
  output$histogram_exploratory_analysis_QC = renderPlotly({
    if(input$person == 'QC') {
      dataset = general_data_react() %>%
        filter(QCAssignedName == input$QC_name)
    } else {
      dataset = general_data_react() %>%
        filter(AnalystAssignedName == input$QC_name)
    }
    
    histogram_exploratory_analysis(feature = input$QC_feature,
                                   dataset = dataset,
                                   bins = 20,
                                   Label = TRUE)
  })
  
  output$histogram_exploratory_analysis_QC2 = renderPlotly({
    if(input$person == 'QC') {
      if(input$QC_name2!='all') {
        dataset = general_data_react() %>%
          filter(QCAssignedName == input$QC_name2)
      } else {
        dataset = general_data_react()}
    } else {
      if(input$QC_name2!='all') {
        dataset = general_data_react() %>%
          filter(AnalystAssignedName == input$QC_name2)
      } else {
        dataset = general_data_react()}
    }
    
    histogram_exploratory_analysis(feature = input$QC_feature,
                                   dataset = dataset,
                                   bins = 20,
                                   Label = TRUE)
  })
  # Impact table
  output$impact_on_score_dt = DT::renderDataTable({
    dataset = general_data
    datatable(impact_on_score(input$QC_feature, dataset))
  })
  # Impact chart
  output$feature_impact = renderPlotly({
    plot_variable_impact(general_data, x_feature = input$QC_feature, y_feature = 'pqc')
  })
  
}

# Run the app
shinyApp(ui = ui, server = server)