# Welcome to AI Assistant template
# in order to run the code, you will need to load following functions : 

# Visualization
#your_dir = path where you store ai_assistant/Scripts folder
#basic_plots=dget(paste(your_dir,"basic_plots.R",sep=''))
#basic_statistics_exploratory_analysis=dget(paste(your_dir,"basic_statistics_exploratory_analysis.R",sep=''))
#correlations_exploratory_analysis=dget(paste(your_dir,"correlations_exploratory_analysis.R",sep=''))
#expected_freq_exploratory_analysis=dget(paste(your_dir,"expected_freq_exploratory_analysis.R",sep=''))
#histogram_exploratory_analysis=dget(paste(your_dir,"histogram_exploratory_analysis.R",sep=''))
#boxplot_exploratory_analysis=dget(paste(your_dir,"boxplot_exploratory_analysis.R",sep=''))
#plotting_freq_exploratory_analysis=dget(paste(your_dir,"plotting_freq_exploratory_analysis.R",sep=''))
#basic_plots=dget(paste(your_dir,"basic_plots.R",sep=''))
#selected_features_table = dget(paste(your_dir,"selected_features_table.R",sep=''))
#feature_importance_table = dget(paste(your_dir,"feature_importance_table.R",sep=''))
#plot_model_performance = dget(paste(your_dir,"plot_model_performance.R",sep=''))
#quantiles_and_IQR = dget(paste(your_dir,"quantiles_and_IQR.R",sep=''))
#barchart_classes = dget(paste(your_dir,"barchart_classes.R",sep=''))
#model_vs_time = dget(paste(your_dir,"model_vs_time.R",sep=''))  
#histogram_error_ratio_model_performance = dget(paste(your_dir,"histogram_error_ratio_model_performance.R",sep=''))
#histogram_box_avg_score =   dget(paste(your_dir,"histogram_box_avg_score.R",sep=''))
#CalculateAUC =   dget(paste(your_dir,"CalculateAUC.R",sep=''))
#fastAUC = dget(paste(your_dir,"fastAUC.R",sep=''))

#Variable importance : 
#Lasso_feature_selection =  dget(paste(your_dir,"Lasso_feature_selection.R",sep=''))
#Boruta_feature_selection = dget(paste(your_dir,"Boruta_feature_selection.R",sep=''))
#RF_feature_selection =  dget(paste(your_dir,"RF_feature_selection.R",sep=''))

### next, make sure that you're following those requirements :
# 1. Dataset :
# a) you must have columns named Label and datestamp (Posixct format)
# b) Variable importance all methods is list of objects created with Variable importance functions
# 2. Results from modelling stage should have following columns : 
# - Case ID
# - Score
# - Label
# - Sum (culminative sum)
# - datestamp
# - X_coordinates
# - y_coordinates











function(dataset,Variable_importance_all_methods=NA,colnames_feature_selection=NA,stage,nn_results=NA,gbm_results=NA,rf_results=NA){
  if(stage=="Exploratory_analysis"){
    ui <- dashboardPage(
      
      skin='red',  
      dashboardHeader(title = "AI Asistant", dropdownMenuOutput("messageMenu")),
      
      # Setting up side bar on the left
      dashboardSidebar(sidebarMenu(
        menuItem("Statistics", tabName = "stats", icon = icon("stats",lib="glyphicon")),
        menuItem("Correlations", tabName = "Correlations", icon = icon("compass"))
        
      )),
      
      # Setting up dashboard body
      
      dashboardBody(tags$style(HTML(".content {background-color:#fff;")),
                    #shinyDashboardThemes(
                    #  theme = "grey_dark"
                    #),
                    tabItems(
                      tabItem(tabName="feature_definition",
                              fluidRow(
                                tabBox(
                                  title = "Feture definition",
                                  # The id lets us use input$tabset1 on the server to find the current tab
                                  id = "tabset0", height = "1800px", width = "300px",
                                  tabPanel("Feture definition",
                                           
                                           box(height = "700px",
                                               width = 9,
                                               DT::dataTableOutput("feature_definition")
                                           ),
                                           box(height = "700px",
                                               width=3,
                                               tableOutput("amount_table3"),
                                               DT::dataTableOutput(outputId = "feature_stats1"),
                                               DT::dataTableOutput(outputId = "feature_stats2")
                                           )
                                           
                                           
                                  )
                                )
                              )
                      ),
                      tabItem(tabName="stats",
                              fluidRow(
                                tabBox(
                                  title = "Statistics",
                                  id = "tabset1", height = "0px", width = "300px",
                                  tabPanel("Basic Statistics",
                                           
                                           box(width = 3,
                                               tags$style('#Feature_statistics{background-color:#ddd}'),
                                               selectInput("Feature_statistics", "Select feature",
                                                           choices = colnames(dataset)[-1]),
                                               
                                               DT::dataTableOutput("statistics")
                                           ),
                                           
                                           
                                           
                                           box(height = "700px",width=9,selectInput("basic_plots_select","Select type of plot",
                                                                                    choices = c("histogram","boxplot")),
                                               plotlyOutput('basic_plots')
                                               
                                           )
                                  )
                                )
                              )
                      ),tabItem(tabName="Correlations",
                                fluidRow(
                                  tabBox(
                                    title = "Correlations",
                                    id = "tabset3", height = "0px", width = "300px",
                                    tabPanel("Correlations",height="1000px",
                                             box(width = 3,
                                                 selectInput("feature1", "Select feature",
                                                             choices = colnames(dataset)[-1]
                                                 ),
                                                 selectInput("feature2", "Select feature",
                                                             choices = colnames(dataset)[-1]
                                                 )
                                                 ,verbatimTextOutput("correlations")
                                             )
                                             
                                             
                                             
                                             ,box(height = "700px",width=9,plotlyOutput(outputId = "correlations_plot"))
                                    )
                                  )
                                )
                      )
                    )
      )
    )
    
    server <- function(input, output,session)
      
    {
      
      output$histograms<-renderPlotly({histogram_exploratory_analysis(feature = input$Feature_statistics,dataset = dataset,Label=ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$statistics=DT::renderDataTable({basic_statistics_exploratory_analysis(feature = input$Feature_statistics,dataset = dataset,Label =ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$correlations_plot<-renderPlotly({
        plotting_freq_exploratory_analysis(input$feature1,input$feature2,dataset = dataset)
      })
      output$correlations=renderPrint({
        correlations_exploratory_analysis(input$feature1,input$feature2,dataset = dataset)
      })
      output$boxplot=renderPlotly({
        boxplot_exploratory_analysis(input$Feature_statistics,dataset = dataset)
      })
      output$basic_plots=renderPlotly({
        basic_plots(type = input$basic_plots_select,input$Feature_statistics,dataset = dataset,Label=ifelse('Label'%in%colnames(dataset),T,F))
      })
      
    }
    
    
    # Run the application 
    shinyApp(ui = ui, server = server)
  }else if(stage=="Feature_selection"){
    ui <- dashboardPage(
      
      skin='red',  
      dashboardHeader(title = "AI Asistant", dropdownMenuOutput("messageMenu")),
      
      # Setting up side bar on the left
      dashboardSidebar(sidebarMenu(
        menuItem("Statistics", tabName = "stats", icon = icon("stats",lib="glyphicon")),
        menuItem("Correlations", tabName = "Correlations", icon = icon("compass")),
        menuItem("Feature selection", tabName = "feature_selection", icon = icon("broom"))
      )),
      
      # Setting up dashboard body
      
      dashboardBody(tags$style(HTML(".content {background-color:#fff;")),
                    tabItems(
                      tabItem(tabName="feature_definition",
                              fluidRow(
                                tabBox(
                                  title = "Feture definition",
                                  # The id lets us use input$tabset1 on the server to find the current tab
                                  id = "tabset0", height = "1800px", width = "300px",
                                  tabPanel("Feture definition",
                                           
                                           box(height = "700px",
                                               width = 9,
                                               DT::dataTableOutput("feature_definition")
                                           ),
                                           box(height = "700px",
                                               width=3,
                                               tableOutput("amount_table3"),
                                               DT::dataTableOutput(outputId = "feature_stats1"),
                                               DT::dataTableOutput(outputId = "feature_stats2")
                                           )
                                           
                                           
                                  )
                                )
                              )
                      ),
                      tabItem(tabName="stats",
                              fluidRow(
                                tabBox(
                                  title = "Statistics",
                                  id = "tabset1", height = "0px", width = "300px",
                                  tabPanel("Basic Statistics",
                                           
                                           box(width = 3,
                                               selectInput("Feature_statistics", "Select feature",
                                                           choices = colnames(dataset)[-1]),
                                               
                                               DT::dataTableOutput("statistics")
                                           ),
                                           
                                           
                                           
                                           box(height = "700px",width=9,selectInput("basic_plots_select","Select type of plot",
                                                                                    choices = c("histogram","boxplot")),
                                               plotlyOutput('basic_plots')
                                               
                                           )
                                  )
                                )
                              )
                      ),tabItem(tabName="Correlations",
                                fluidRow(
                                  tabBox(
                                    title = "Correlations",
                                    id = "tabset3", height = "0px", width = "300px",
                                    tabPanel("Correlations",height="1000px",
                                             box(width = 3,
                                                 selectInput("feature1", "Select feature",
                                                             choices = colnames(dataset)[-1]
                                                 ),
                                                 selectInput("feature2", "Select feature",
                                                             choices = colnames(dataset)[-1]
                                                 )
                                                 ,verbatimTextOutput("correlations")
                                             )
                                             
                                             
                                             
                                             ,box(height = "700px",width=9,plotlyOutput(outputId = "correlations_plot"))
                                    )
                                  )
                                )
                      ),tabItem(tabName="feature_selection",
                                fluidRow(
                                  tabBox(
                                    title = "Feature Selection",
                                    # The id lets us use input$tabset1 on the server to find the current tab
                                    id = "tabset5", height = "800px", width = "300px",
                                    tabPanel("Feature Selection", 
                                             box(width = 4,
                                                 selectInput("Feature_selection_feature", "Select feature",
                                                             choices = colnames_feature_selection[-1]
                                                 ),
                                                 selectInput("Feature_selection_model", "Select model",
                                                             choices = c("Lasso","Boruta","RF")),
                                                 dataTableOutput("features_selected_for_the_model")
                                             )
                                             
                                             
                                             
                                             ,box(height = "700px",width=8,
                                                  dataTableOutput("confirmed_rejected"),
                                                  plotlyOutput(outputId = "significance_level_features"))
                                             
                                    )
                                  )
                                )
                      )
                    )
      )
    )
    
    server <- function(input, output,session)
      
    {
      
      output$histograms<-renderPlotly({histogram_exploratory_analysis(feature = input$Feature_statistics,dataset = dataset,Label=ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$statistics=DT::renderDataTable({basic_statistics_exploratory_analysis(feature = input$Feature_statistics,dataset = dataset,Label =ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$correlations_plot<-renderPlotly({
        plotting_freq_exploratory_analysis(input$feature1,input$feature2,dataset = dataset)
      })
      output$correlations=renderPrint({
        correlations_exploratory_analysis(input$feature1,input$feature2,dataset = dataset)
      })
      output$boxplot=renderPlotly({
        boxplot_exploratory_analysis(input$Feature_statistics,dataset = dataset)
      })
      output$basic_plots=renderPlotly({
        basic_plots(type = input$basic_plots_select,input$Feature_statistics,dataset = dataset,Label=ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$features_selected_for_the_model=renderDataTable({
        selected_features_table(method = input$Feature_selection_model,Variable_importance_all_methods = Variable_importance_all_methods)
      })
      output$confirmed_rejected=renderDataTable({
        datatable(feature_importance_table(input$Feature_selection_feature,Variable_importance_all_methods = Variable_importance_all_methods),
                  options=list(dom='t'))
      })
      output$significance_level_features=renderPlotly({
        if(input$Feature_selection_model=="Lasso"){
          plot_ly(data=Variable_importance_all_methods[[1]],
                  x=~V3,
                  y=~Overall,
                  text=~V2,
                  name = Variable_importance_all_methods[[1]]$V2,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=10,name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50))
        }else if(input$Feature_selection_model=="Boruta"){
          plot_ly(data=Variable_importance_all_methods[[2]],
                  x=(1:nrow(Variable_importance_all_methods[[2]])),
                  y=~meanImp,name=Variable_importance_all_methods[[2]]$V7,
                  text=~V7,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=min(Variable_importance_all_methods[[2]][Variable_importance_all_methods[[2]]$decision=="Confirmed",1]),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50))
        }else if(input$Feature_selection_model=="RF"){
          plot_ly(data=Variable_importance_all_methods[[3]],
                  x=(1:nrow(Variable_importance_all_methods[[3]])),
                  y=Variable_importance_all_methods[[3]][,1],
                  text=~V2,
                  name=Variable_importance_all_methods[[3]]$V2,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=quantile(Variable_importance_all_methods[[3]][,1],probs = 0.1),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50)
            )
        }else if(input$Feature_selection_model=="GBM"){
          plot_ly(data=Variable_importance_all_methods[[4]],x=(1:nrow(Variable_importance_all_methods[[4]])),y=~dropout_loss,name=Variable_importance_all_methods[[4]]$variable,type='scatter',mode='lines+markers')%>%
            add_trace(y=quantile(Variable_importance_all_methods[[4]]$dropout_loss,probs = 0.1),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50)
            )
        }else if(input$Feature_selection_model=="NN"){
          plot_ly(data=Variable_importance_all_methods[[5]],x=(1:nrow(Variable_importance_all_methods[[5]])),y=~dropout_loss,name=Variable_importance_all_methods[[5]]$variable,type='scatter',mode='lines+markers')%>%
            add_trace(y=quantile(Variable_importance_all_methods[[5]]$dropout_loss,probs = 0.1),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50)
            )
        }
      })
    }
    
    
    # Run the application 
    shinyApp(ui = ui, server = server)
  }else if(stage=="Model_results"){
    ui <- dashboardPage(
      
      skin='red',
      dashboardHeader(title = "AI Asistant", dropdownMenuOutput("messageMenu")),
      
      # Setting up side bar on the left
      dashboardSidebar(sidebarMenu(
        menuItem("Statistics", tabName = "stats", icon = icon("stats",lib="glyphicon")),
        menuItem("Correlations", tabName = "Correlations", icon = icon("compass")),
        menuItem("Feature selection", tabName = "feature_selection", icon = icon("broom")),
        menuItem("Gradient Boosted Machine", tabName = "gbm", icon = icon("chess-king")),
        menuItem("Neural Network", tabName = "nn", icon = icon("chess-queen")),
        menuItem("Classification Random Forest", tabName = "rfc", icon = icon("chess-bishop")),
        menuItem("Summary", tabName = "summary", icon = icon("crown")),
        menuItem("Population changes", tabName = "population_changes", icon = icon("chart-bar")),
        menuItem("Model Performance", tabName = "model_performance", icon = icon("balance-scale"))
      )),
      
      # Setting up dashboard body
      
      dashboardBody(
        tags$head(tags$link(rel="shortcut icon", href="https://assets1.risnews.com/styles/content_sm/s3/2018-11/AI-20171012113039221.jpg?itok=oPpT7_5r")),
        tags$style(HTML(".content {background-color:#fff;")),
        tabItems(
          tabItem(tabName="feature_definition",
                  fluidRow(
                    tabBox(
                      title = "Feture definition",
                      # The id lets us use input$tabset1 on the server to find the current tab
                      id = "tabset0", height = "1800px", width = "300px",
                      tabPanel("Feture definition",
                               
                               box(height = "700px",
                                   width = 9,
                                   DT::dataTableOutput("feature_definition")
                               ),
                               box(height = "700px",
                                   width=3,
                                   tableOutput("amount_table3"),
                                   DT::dataTableOutput(outputId = "feature_stats1"),
                                   DT::dataTableOutput(outputId = "feature_stats2")
                               )
                               
                               
                      )
                    )
                  )
          ),
          tabItem(tabName="stats",
                  fluidRow(
                    tabBox(
                      title = "Statistics",
                      id = "tabset1", height = "0px", width = "300px",
                      tabPanel("Basic Statistics",
                               
                               box(width = 3,
                                   tags$style(
                                     
                                     '#Feature_statistics{
                          background-color: #D04A02 !important;
                          }'
                                     
                                   ),
                                   selectInput("Feature_statistics", "Select feature",
                                               choices = colnames(dataset)[-1]),
                                   
                                   DT::dataTableOutput("statistics")
                               ),
                               
                               
                               
                               box(height = "700px",width=9,selectInput("basic_plots_select","Select type of plot",
                                                                        choices = c("histogram","boxplot")),
                                   plotlyOutput('basic_plots')
                                   
                               )
                      )
                    )
                  )
          ),tabItem(tabName="Correlations",
                    fluidRow(
                      tabBox(
                        title = "Correlations",
                        id = "tabset3", height = "0px", width = "300px",
                        tabPanel("Correlations",height="1000px",
                                 box(width = 3,
                                     selectInput("feature1", "Select feature",
                                                 choices = colnames(dataset)[-1]
                                     ),
                                     selectInput("feature2", "Select feature",
                                                 choices = colnames(dataset)[-1]
                                     )
                                     ,verbatimTextOutput("correlations")
                                 )
                                 
                                 
                                 
                                 ,box(height = "700px",width=9,plotlyOutput(outputId = "correlations_plot"))
                        )
                      )
                    )
          ),tabItem(tabName="feature_selection",
                    fluidRow(
                      tabBox(
                        title = "Feature Selection",
                        # The id lets us use input$tabset1 on the server to find the current tab
                        id = "tabset5", height = "800px", width = "300px",
                        tabPanel("Feature Selection", 
                                 box(width = 4,
                                     selectInput("Feature_selection_feature", "Select feature",
                                                 choices = colnames_feature_selection[-1]
                                     ),
                                     selectInput("Feature_selection_model", "Select model",
                                                 choices = c("Lasso","Boruta","RF")),
                                     dataTableOutput("features_selected_for_the_model")
                                 )
                                 
                                 
                                 
                                 ,box(height = "700px",width=8,
                                      dataTableOutput("confirmed_rejected"),
                                      plotlyOutput(outputId = "significance_level_features"))
                                 
                        )
                      )
                    )
          ),tabItem(tabName="gbm",
                    fluidRow(
                      tabBox(
                        title = "Gradient Boosted Machine",
                        # The id lets us use input$tabset1 on the server to find the current tab
                        id = "tabset7", height = "900px", width = "300px",
                        tabPanel("Gradient Boosted Machine", 
                                 box(width = 2,
                                     dataTableOutput("gbm_AUC")          
                                 )
                                 ,
                                 box(width = 10,height = "700px",
                                     plotlyOutput("gbm_plot",height = "700px"))
                                 
                        )
                      )
                    )
          ),tabItem(tabName="nn",
                    fluidRow(
                      tabBox(
                        title = "Neural Network",
                        # The id lets us use input$tabset1 on the server to find the current tab
                        id = "tabset8", height = "900px", width = "300px",
                        tabPanel("Neural Network", 
                                 box(width = 2,
                                     dataTableOutput("nn_AUC")          
                                 )
                                 ,
                                 box(width = 10,height = "700px",
                                     plotlyOutput("nn_plot",height = "700px"))
                                 
                        )
                      )
                    )
          ),tabItem(tabName="rfc",
                    fluidRow(
                      tabBox(
                        title = "Classification Random Forest",
                        # The id lets us use input$tabset1 on the server to find the current tab
                        id = "tabset9", height = "900px", width = "300px",
                        tabPanel("Classification Random Forest", 
                                 box(width = 2,
                                     dataTableOutput("rf_AUC")          
                                 )
                                 ,
                                 box(width = 10,height = "700px",
                                     plotlyOutput("rf_plot",height = "700px"))
                                 
                        )
                      )
                    )
          ),tabItem(tabName="summary",
                    fluidRow(
                      tabBox(
                        title = "Summary",
                        # The id lets us use input$tabset1 on the server to find the current tab
                        id = "tabset9", height = "1800px", width = "300px",
                        tabPanel("Summary", 
                                 box(width=4,
                                     tableOutput("amount_table")),
                                 column(width=4,offset=4
                                 ),
                                 box(width=12,
                                     dataTableOutput("excel_table_train")),
                                 box(width=12,
                                     dataTableOutput("excel_table_test")),
                                 box(width = 2,
                                     dataTableOutput("best_models_AUC")          
                                 )
                                 ,
                                 box(width = 10,height = "600px",
                                     plotlyOutput("best_models_plot",height = "600px")),
                                 box(width=12,
                                     sliderInput(inputId = "detailed_table_percent",
                                                 label = HTML('<font size="4">',"Select percent of populations [%]",'</font size>'),
                                                 max = 100,
                                                 min=0,
                                                 value=75),
                                     dataTableOutput("detailed_table"))
                                 
                        )
                      )
                    )
          ),
          tabItem(tabName="population_changes",
                  fluidRow(
                    tabBox(
                      title = "Population changes",
                      id = "tabset1", height = "0px", width = "300px",
                      tabPanel("Population changes",
                               
                               box(width = 5,
                                   selectInput("Feature_statistics_monitoring", "Select feature",
                                               choices = colnames(dataset)[-c(1,length(dataset))]),
                                   
                                   DT::dataTableOutput("statistics_all"),
                                   DT::dataTableOutput("statistics_1"),
                                   DT::dataTableOutput("statistics_0")
                               ),
                               
                               
                               
                               box(height = "700px",width=7,
                                   plotlyOutput('barchart_classes_all'),
                                   plotlyOutput('barchart_classes_1'),
                                   plotlyOutput('barchart_classes_0')
                               )
                      )
                    )
                  )
          ),tabItem(tabName="model_performance",
                    fluidRow(
                      tabBox(
                        title = "Model performance",
                        id = "tabset3", height = "0px", width = "300px",
                        tabPanel("Model performance",
                                 column(width=3,align='center',
                                        selectInput("model_vs_time_type", "Select type of metric",
                                                    choices = c('model_performance',
                                                                'part_of_population',
                                                                'error_ratio',
                                                                'auc',
                                                                'F1',
                                                                'acc',
                                                                'average_score')
                                        )),
                                 column(width=3,align='center',
                                        sliderInput(inputId = "threshold",
                                                    label = HTML('<font size="4">',"Select percent of population [%]",'</font size>'),
                                                    max = 100,
                                                    min=0,
                                                    value=75)),
                                 column(width=3,align='center',
                                        selectInput("time_frame", "Select time frames to group cases",
                                                    choices = c('day',
                                                                'week',
                                                                'month')
                                        )),
                                 box(width=12,
                                     plotlyOutput("model_vs_time")),
                                 box(width=5,
                                     plotlyOutput("histogram_error_ratio_model_performance")),
                                 box(width = 7,align = 'center',
                                     column(6,
                                            selectInput("histogram_box_avg_score_type", "Select type of plot",
                                                        choices = c('histogram',
                                                                    'box')
                                            )),
                                     column(6,
                                            sliderInput(inputId = "last_x_days",
                                                        label = HTML('<font size="4">',"Select amount of days",'</font size>'),
                                                        max = as.numeric(as.POSIXct(as.character(today()))-min(gbm_results[[1]]$datestamp)),
                                                        min=as.numeric(as.POSIXct(as.character(today()))-max(gbm_results[[1]]$datestamp)),
                                                        value=150)),
                                     column(12,
                                            plotlyOutput("histogram_box_avg_score"))
                                 )
                        )
                      )
                    )
          )
          
        )
      )
    )
    
    
    server <- function(input, output,session)
      
    {
      
      output$histograms<-renderPlotly({histogram_exploratory_analysis(feature = input$Feature_statistics,dataset = dataset,Label=ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$statistics=DT::renderDataTable({basic_statistics_exploratory_analysis(feature = input$Feature_statistics,dataset = dataset,Label =ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$correlations_plot<-renderPlotly({
        plotting_freq_exploratory_analysis(input$feature1,input$feature2,dataset = dataset)
      })
      output$correlations=renderPrint({
        correlations_exploratory_analysis(input$feature1,input$feature2,dataset = dataset)
      })
      output$boxplot=renderPlotly({
        boxplot_exploratory_analysis(input$Feature_statistics,dataset = dataset)
      })
      output$basic_plots=renderPlotly({
        basic_plots(type = input$basic_plots_select,input$Feature_statistics,dataset = dataset,Label=ifelse('Label'%in%colnames(dataset),T,F))
      })
      output$features_selected_for_the_model=renderDataTable({
        selected_features_table(method = input$Feature_selection_model,Variable_importance_all_methods = Variable_importance_all_methods)
      })
      output$confirmed_rejected=renderDataTable({
        datatable(feature_importance_table(input$Feature_selection_feature,Variable_importance_all_methods = Variable_importance_all_methods),
                  options=list(dom='t'))
      })
      output$significance_level_features=renderPlotly({
        if(input$Feature_selection_model=="Lasso"){
          plot_ly(data=Variable_importance_all_methods[[1]],
                  x=~V3,
                  y=~Overall,
                  text=~V2,
                  name = Variable_importance_all_methods[[1]]$V2,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=10,name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50))
        }else if(input$Feature_selection_model=="Boruta"){
          plot_ly(data=Variable_importance_all_methods[[2]],
                  x=(1:nrow(Variable_importance_all_methods[[2]])),
                  y=~meanImp,name=Variable_importance_all_methods[[2]]$V7,
                  text=~V7,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=min(Variable_importance_all_methods[[2]][Variable_importance_all_methods[[2]]$decision=="Confirmed",1]),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50))
        }else if(input$Feature_selection_model=="RF"){
          plot_ly(data=Variable_importance_all_methods[[3]],
                  x=(1:nrow(Variable_importance_all_methods[[3]])),
                  y=Variable_importance_all_methods[[3]][,1],
                  text=~V2,
                  name=Variable_importance_all_methods[[3]]$V2,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=quantile(Variable_importance_all_methods[[3]][,1],probs = 0.1),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50)
            )
        }else if(input$Feature_selection_model=="GBM"){
          plot_ly(data=Variable_importance_all_methods[[4]],x=(1:nrow(Variable_importance_all_methods[[4]])),y=~dropout_loss,name=Variable_importance_all_methods[[4]]$variable,type='scatter',mode='lines+markers')%>%
            add_trace(y=quantile(Variable_importance_all_methods[[4]]$dropout_loss,probs = 0.1),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50)
            )
        }else if(input$Feature_selection_model=="NN"){
          plot_ly(data=Variable_importance_all_methods[[5]],x=(1:nrow(Variable_importance_all_methods[[5]])),y=~dropout_loss,name=Variable_importance_all_methods[[5]]$variable,type='scatter',mode='lines+markers')%>%
            add_trace(y=quantile(Variable_importance_all_methods[[5]]$dropout_loss,probs = 0.1),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50)
            )
        }
      })
      #gbm_data <- reactive({
      #  switch(input$gbm_results,
      #         "All errors" = 1,
      #         "Minor" = 2,
      #         "Major" = 3,
      #         "Critical" = 4)
      #})
      output$gbm_AUC=renderDataTable({
        CalculateAUC(gbm_results)
      })
      output$gbm_plot=renderPlotly({
        plot_model_performance(gbm_results)
      })
      #nn_data <- reactive({
      #  switch(input$nn_results,
      #         "All errors" = 1,
      #         "Minor" = 2,
      #         "Major" = 3,
      #         "Critical" = 4)
      #})
      output$nn_AUC=renderDataTable({
        CalculateAUC(nn_results)
      })
      output$nn_plot=renderPlotly({
        plot_model_performance(nn_results)
      })
      #rf_data <- reactive({
      #  switch(input$rf_results,
      #         "All errors" = 1,
      #         "Minor" = 2,
      #         "Major" = 3,
      #         "Critical" = 4)
      #})
      output$rf_AUC=renderDataTable({
        CalculateAUC(rf_results)
      })
      output$rf_plot=renderPlotly({
        plot_model_performance(rf_results)
      })
      output$amount_table=renderTable({
        amount_table=data.frame(matrix(nrow = 2,ncol = 3))
        colnames(amount_table)=c("Whole dataset","Train data","Test data")
        row.names(amount_table)=c("Number of cases[errors]","Error Ratio")
        amount_table$`Whole dataset`[1]=paste(nrow(nn_results[[1]])+nrow(nn_results[[2]]),'[',sum(nn_results[[1]]$Label)+sum(nn_results[[2]]$Label),']',sep='')
        amount_table$`Train data`[1]=paste(nrow(nn_results[[2]]),'[',sum(nn_results[[2]]$Label),']',sep='')
        amount_table$`Test data`[1]=paste(nrow(nn_results[[1]]),'[',sum(nn_results[[1]]$Label),']',sep='')
        amount_table$`Whole dataset`[2]=paste(round(100*(sum(nn_results[[1]]$Label)+sum(nn_results[[2]]$Label))/(nrow(nn_results[[1]])+nrow(nn_results[[2]])),digits = 2),'%',sep='')
        amount_table$`Train data`[2]=paste(round(100*sum(nn_results[[2]]$Label)/nrow(nn_results[[2]]),digits = 2),'%',sep='')
        amount_table$`Test data`[2]=paste(round(100*sum(nn_results[[1]]$Label)/nrow(nn_results[[1]]),digits = 2),'%',sep='')
        amount_table
      },rownames = T)
      output$excel_table_train=renderDataTable({
        best_models_train=list(gbm_results[[2]],nn_results[[2]],rf_results[[2]])
        excel_table_train=as.data.frame(matrix(nrow=3,ncol=13))
        excel_table_train$V1=c("Gradient Boosted Machine","Neural Network","Classification Random Forest")
        for (i in 1:3){
          excel_table_train$V2[i]=best_models_train[[i]]$Sum[round(0.05*nrow(best_models_train[[i]]))]
          excel_table_train$V3[i]=round(best_models_train[[i]]$Sum[round(0.05*nrow(best_models_train[[i]]))]/max(best_models_train[[i]]$Sum),4)
          excel_table_train$V4[i]=best_models_train[[i]]$Sum[round(0.25*nrow(best_models_train[[i]]))]
          excel_table_train$V5[i]=round(best_models_train[[i]]$Sum[round(0.25*nrow(best_models_train[[i]]))]/max(best_models_train[[i]]$Sum),4)
          excel_table_train$V6[i]=best_models_train[[i]]$Sum[round(0.50*nrow(best_models_train[[i]]))]
          excel_table_train$V7[i]=round(best_models_train[[i]]$Sum[round(0.50*nrow(best_models_train[[i]]))]/max(best_models_train[[i]]$Sum),4)
          excel_table_train$V8[i]=best_models_train[[i]]$Sum[round(0.75*nrow(best_models_train[[i]]))]
          excel_table_train$V9[i]=round(best_models_train[[i]]$Sum[round(0.75*nrow(best_models_train[[i]]))]/max(best_models_train[[i]]$Sum),4)
          excel_table_train$V10[i]=best_models_train[[i]]$Sum[round(0.80*nrow(best_models_train[[i]]))]
          excel_table_train$V11[i]=round(best_models_train[[i]]$Sum[round(0.80*nrow(best_models_train[[i]]))]/max(best_models_train[[i]]$Sum),4)
          excel_table_train$V12[i]=best_models_train[[i]]$Sum[round(0.85*nrow(best_models_train[[i]]))]
          excel_table_train$V13[i]=round(best_models_train[[i]]$Sum[round(0.85*nrow(best_models_train[[i]]))]/max(best_models_train[[i]]$Sum),4)
        }
        sketch_train = htmltools::withTags(table(
          class = 'display',
          thead(
            tr(
              th(rowspan = 2, 'Model'),
              th(class = 'dt-center',colspan = 2, paste('5%[',round(0.05*nrow(best_models_train[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('25%[',round(0.25*nrow(best_models_train[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('50%[',round(0.5*nrow(best_models_train[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('75%[',round(0.75*nrow(best_models_train[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('80%[',round(0.8*nrow(best_models_train[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('85%[',round(0.85*nrow(best_models_train[[1]])),']',sep=''))
            ),
            tr(
              lapply(rep(c('Errors found', '% of total errors'), 6), th)
            )
          )
        ))
        datatable(excel_table_train,container = sketch_train,rownames = F,options = list(dom='t',columnDefs=list(list(className="dt-center"))),
                  caption = htmltools::tags$caption(
                    style = 'caption-side: top; text-align: center; font-size:22px;font-weight: bold; color:black;',
                    'Model performance on specifyied checkpoints for train dataset'))%>%
          formatPercentage(digits = 2,columns = c(3,5,7,9,11,13))
      })
      
      output$excel_table_test=renderDataTable({
        best_models_test=list(gbm_results[[1]],nn_results[[1]],rf_results[[1]])
        excel_table_test=as.data.frame(matrix(nrow=3,ncol=13))
        excel_table_test$V1=c("Gradient Boosted Machine","Neural Network","Classification Random Forest")
        for (i in 1:3){
          excel_table_test$V2[i]=best_models_test[[i]]$Sum[round(0.05*nrow(best_models_test[[i]]))]
          excel_table_test$V3[i]=round(best_models_test[[i]]$Sum[round(0.05*nrow(best_models_test[[i]]))]/max(best_models_test[[i]]$Sum),4)
          excel_table_test$V4[i]=best_models_test[[i]]$Sum[round(0.25*nrow(best_models_test[[i]]))]
          excel_table_test$V5[i]=round(best_models_test[[i]]$Sum[round(0.25*nrow(best_models_test[[i]]))]/max(best_models_test[[i]]$Sum),4)
          excel_table_test$V6[i]=best_models_test[[i]]$Sum[round(0.50*nrow(best_models_test[[i]]))]
          excel_table_test$V7[i]=round(best_models_test[[i]]$Sum[round(0.50*nrow(best_models_test[[i]]))]/max(best_models_test[[i]]$Sum),4)
          excel_table_test$V8[i]=best_models_test[[i]]$Sum[round(0.75*nrow(best_models_test[[i]]))]
          excel_table_test$V9[i]=round(best_models_test[[i]]$Sum[round(0.75*nrow(best_models_test[[i]]))]/max(best_models_test[[i]]$Sum),4)
          excel_table_test$V10[i]=best_models_test[[i]]$Sum[round(0.80*nrow(best_models_test[[i]]))]
          excel_table_test$V11[i]=round(best_models_test[[i]]$Sum[round(0.80*nrow(best_models_test[[i]]))]/max(best_models_test[[i]]$Sum),4)
          excel_table_test$V12[i]=best_models_test[[i]]$Sum[round(0.85*nrow(best_models_test[[i]]))]
          excel_table_test$V13[i]=round(best_models_test[[i]]$Sum[round(0.85*nrow(best_models_test[[i]]))]/max(best_models_test[[i]]$Sum),4)
        }
        sketch = htmltools::withTags(table(
          class = 'display',
          thead(
            tr(
              th(rowspan = 2, 'Model'),
              th(class = 'dt-center',colspan = 2, paste('5%[',round(0.05*nrow(best_models_test[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('25%[',round(0.25*nrow(best_models_test[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('50%[',round(0.5*nrow(best_models_test[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('75%[',round(0.75*nrow(best_models_test[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('80%[',round(0.8*nrow(best_models_test[[1]])),']',sep='')),
              th(class = 'dt-center',colspan = 2, paste('85%[',round(0.85*nrow(best_models_test[[1]])),']',sep=''))
            ),
            tr(
              lapply(rep(c('Errors found', '% of total errors'), 6), th)
            )
          )
        ))
        
        
        
        datatable(excel_table_test,container = sketch,rownames = F,options = list(dom='t',columnDefs=list(list(className="dt-center"))),
                  caption = htmltools::tags$caption(
                    style = 'caption-side: top; text-align: center; font-size:22px;font-weight: bold; color:black;',
                    'Model performance on specifyied checkpoints for test dataset'))%>%
          formatPercentage(digits = 2,columns = c(3,5,7,9,11,13))
        
      })
      
      output$best_models_plot=renderPlotly({
        best_models=list(gbm_results[[1]],nn_results[[1]],rf_results[[1]])
        plot_ly(x=best_models[[1]]$X_coordinates,y=best_models[[1]]$y_coordinates,type='scatter',mode='line',name="Gradient Boosted Machine",line=list(color='#dd4b39'))%>%
          add_trace(x=best_models[[2]]$X_coordinates,y=best_models[[2]]$y_coordinates,name="Neural Network",line=list(color='#FFB600'))%>%
          add_trace(x=best_models[[3]]$X_coordinates,y=best_models[[3]]$y_coordinates,name="Classification Random Forest",line=list(color='#7D7D7D'))%>%
          layout(title='<b>Model performance</b>',titlefont=list(size=22,color='black',face='bold'),margin=list(t=50),xaxis=list(tickformat="%",title="% of cases"),yaxis=list(tickformat="%",title="% of errors found"))
      })
      best_model = reactive({
        nn_auc = fastAUC(probs = nn_results[[1]]$Score,class = nn_results[[1]]$Label)
        gbm_auc = fastAUC(probs = gbm_results[[1]]$Score,class = gbm_results[[1]]$Label)
        rf_auc = fastAUC(probs = rf_results[[1]]$Score,class = rf_results[[1]]$Label)
        return(c(nn_results,gbm_results,rf_results)[which.max(c(nn_auc,gbm_auc,rf_auc))])
      })
      
      
      output$detailed_table=renderDataTable({
        fraction=input$detailed_table_percent/100
        detailed_table=data.frame(matrix(nrow = 2,ncol=7))
        colnames(detailed_table)=c("No. cases selected",
                                   "Errors found",
                                   "Errors not found",
                                   "% of errors found",
                                   "Error ratio in population selected for QC",
                                   "Error ratio in population not selected for QC",
                                   "Error ratio in whole population using Predictive QC")
        rownames(detailed_table)=c("Test dataset",
                                   "Train dataset")
        for(i in 1:nrow(detailed_table)){
          detailed_table$`No. cases selected`[i]=round(fraction*nrow(best_model()[[i]]))
          detailed_table$`Errors found`[i]=sum(best_model()[[i]][round(fraction*nrow(best_model()[[i]])),]$Sum)
          detailed_table$`Errors not found`[i]=sum(best_model()[[i]]$Label)-detailed_table$`Errors found`[i]
          detailed_table$`Error ratio in population selected for QC`[i]=detailed_table$`Errors found`[i]/detailed_table$`No. cases`[i]
          detailed_table$`Error ratio in population not selected for QC`[i]=detailed_table$`Errors not found`[i]/(nrow(best_model()[[i]])-detailed_table$`No. cases`[i])
          detailed_table$`% of errors found`[i]=detailed_table$`Errors found`[i]/(detailed_table$`Errors found`[i]+detailed_table$`Errors not found`[i])
          detailed_table$`Error ratio in whole population using Predictive QC`[i] = detailed_table$`Errors not found`[i]/nrow(best_model()[[i]])
        }
        
        
        
        
        datatable(detailed_table,rownames = T,options = list(dom='t',columnDefs=list(list(className="dt-center"))),
                  caption = htmltools::tags$caption(
                    style = 'caption-side: top; text-align: center; font-size:22px;font-weight: bold; color:black;',
                    paste('Detailed results for', input$detailed_table_percent,'% of the population')))%>%
          formatPercentage(digits = 2,columns = c(4,5,6,7))
        
      })
      
      output$statistics_all=renderDataTable({
        quantiles_and_IQR(dataset = dataset,time_feature = "datestamp",feature = input$Feature_statistics_monitoring,Label = 'all')
      })
      output$statistics_1=renderDataTable({
        quantiles_and_IQR(dataset = dataset,time_feature = "datestamp",feature = input$Feature_statistics_monitoring,Label = 1)
      })
      output$statistics_0=renderDataTable({
        quantiles_and_IQR(dataset = dataset,time_feature = "datestamp",feature = input$Feature_statistics_monitoring,Label = 0)
      })
      output$barchart_classes_all<-renderPlotly({
        barchart_classes(dataset = dataset,time_feature = "datestamp",feature = input$Feature_statistics_monitoring,Label = 'all')
      })
      output$barchart_classes_1<-renderPlotly({
        barchart_classes(dataset = dataset,time_feature = "datestamp",feature = input$Feature_statistics_monitoring,Label = 1)
      })
      output$barchart_classes_0<-renderPlotly({
        barchart_classes(dataset = dataset,time_feature = "datestamp",feature = input$Feature_statistics_monitoring,Label = 0)
      })
      #2nd page
      
      output$model_vs_time=renderPlotly({
        model_vs_time(PQC_results = best_model()[[2]],RQC_results = best_model()[[1]],threshold = input$threshold/100,type = input$model_vs_time_type,time_frame = input$time_frame)
      })
      
      output$histogram_error_ratio_model_performance = renderPlotly({
        histogram_error_ratio_model_performance(PQC_results = best_model()[[2]],RQC_results = best_model()[[1]],threshold = input$threshold/100,type = input$model_vs_time_type)
      })
      
      output$histogram_box_avg_score=renderPlotly({
        histogram_box_avg_score(RQC_results = best_model()[[1]],PQC_results = best_model()[[2]],type = input$histogram_box_avg_score_type,last_x_days = input$last_x_days)
      })
      
      
      
      
      
      
    }
    # Run the application 
    shinyApp(ui = ui, server = server)
  }
  
}
