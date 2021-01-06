# BASIC PLOTS
basic_plots <- function(type, ...){
  if (type == 'histogram') {
    histogram_exploratory_analysis(...)
  } else {
    boxplot_exploratory_analysis(...)
  }
}

# BOXPLOT EXPLANATORY ANALYSIS
boxplot_exploratory_analysis <- function(feature, dataset,Label=F){
  if(is.numeric(dataset[,feature])==F){
    plot_ly(y=dataset[,'Label'],x=dataset[,feature],color=dataset[,feature],type="box",height = 600)%>%
      layout(showlegend=F,yaxis=list(title='Label'),xaxis=list(title=feature))
  }else{
    plot_ly(dataset,y=dataset[,feature],type="box",name=feature,height = 600)%>%
      layout(showlegend=F,yaxis=list(title=feature))
  }
}

# HISTOGRAM EXPLANATORY ANALYSIS
histogram_exploratory_analysis <- function(feature,dataset,bins=50,Label=T){
  if(Label==T){
    if(is.numeric(dataset[,feature])){
      test=hist(dataset[,feature])
      test_0=hist(dataset[,feature][which(dataset$Label==0)],breaks = test$breaks)
      test_1=hist(dataset[,feature][which(dataset$Label==1)],breaks = test$breaks)
      
      plot_ly(x=test_0$breaks[-1],
              y=test_0$counts,
              type="bar",name = "Label = 0",textposition = 'auto',text=paste(100*round(test_0$counts/(test_0$counts+test_1$counts),2),"%",sep = "")
              ,marker=list(color='#dd4b39')
      )%>%
        add_trace(x=test_1$breaks[-1],
                  y=test_1$counts,
                  name = "Label = 1",text=paste(100*round(test_1$counts/(test_0$counts+test_1$counts),2),"%",sep = "")
                  ,marker=list(color='#FFB600')
        )%>%
        layout(#margin = list(b = 500),
          yaxis=list(title="Amount of cases"
                     #,color='white'
          ),xaxis=list(title=feature,
                       tickangle = 45
                       #,color='white'
          ),title=paste("Histogram of ",feature,sep=""),
          barmode="stack"
          #,font=list(color='white')
        )
      
    }else{
      dataset[,feature]=as.character(dataset[,feature])
      dataset[is.na(dataset[,feature]),feature]='N/A'
      plot_ly(x=sort(unique(dataset[which(dataset$Label==0),feature])),
              y=table(dataset[which(dataset$Label==0),feature]),
              type="bar",name = "Label = 0",textposition = 'auto',
              text=paste(100*round(table(dataset[which(dataset$Label==0),feature])/table(dataset[which(dataset[,feature]%in%dataset[which(dataset$Label==0),feature]),feature]),2),"%",sep = "")
              ,marker=list(color='#dd4b39')
      )%>%
        add_trace(x=sort(unique(dataset[which(dataset$Label==1),feature])),
                  y=table(dataset[which(dataset$Label==1),feature]),
                  name = "Label = 1",
                  text=paste(100*round(table(dataset[which(dataset$Label==1),feature])/table(dataset[which(dataset[,feature]%in%dataset[which(dataset$Label==1),feature]),feature]),2),"%",sep = "")
                  ,marker=list(color='#FFB600')
        )%>%
        layout(#margin = list(b = 500),
          yaxis=list(
            title=HTML("<b>Amount of cases</b>")
            #,color='white'
          )
          ,xaxis=list(
            title=HTML(paste("<b>",feature,sep='')),
            tickangle = 45
            #,color='white'
          ),title=HTML(
            paste("<b>Histogram of ",feature,sep=""))
          ,barmode="stack"
          #,font=list(color='white')
        )
      
    }
    
  } else {
    plot_ly(x=dataset[,feature],type="histogram",nbinsx=bins)%>%
      layout(yaxis=list(
        title=HTML("<b>Amount of cases</b>")
        #,color='white'
      ),
      xaxis=list(
        title=HTML(paste("<b>",feature,sep='')),
        tickangle = 45
        #,color='white'
      ),
      title=paste("Histogram of ",feature,sep=""),
      barmode="stack")
    
  }
}

# BASIC STATISTICS EXPLANATORY ANALYSIS
basic_statistics_exploratory_analysis <- function(feature, dataset, Label = T) {
  if (is.numeric(dataset[,feature]) == F) {
    if (Label == T) {
      dataset[is.na(dataset[,feature]), feature] = 'N/A'
      table = round(as.data.frame.matrix(addmargins(prop.table(table(dataset[,feature],dataset$Label)),
                                                    margin = 2)),4)
      table = datatable(table,
                        filter = "bottom",
                        escape = F,
                        options = list(
                          dom = "Blfrtip",
                          scrollX = T,
                          lengthMenu = list(c(10, 20, 50, -1), # declare values
                                            c(10, 20,50, "All")), # declare titles # end of lengthMenu customization
                          pageLength = 10)) %>%
        formatPercentage(digits = 2,columns = c(1, 2, 3))
      return(table)
    } else {
      dataset[is.na(dataset[,feature]), feature] = 'N/A'
      table = as.data.frame(prop.table(table(dataset[,feature])))
      colnames(table) = c(feature, "Frequency")
      table$Frequency = round(table$Frequency, 4)
      table = datatable(table,
                        filter = "bottom",
                        escape = F,
                        options = list(dom = "Blfrtip",
                                       scrollX = T,
                                       lengthMenu = list(c(10, 20, 50, -1), # declare values
                                                         c(10, 20, 50, "All")), # declare titles # end of lengthMenu customization
                                       pageLength = 10)) %>%
        formatPercentage(digits = 2, columns = c(2))
      return(table)
    }
  } else {
    overall = data.frame(matrix(nrow = 10, ncol = 2))
    colnames(overall) = c("Measure", "Value")
    overall[,1] = c("Min", "Max"," Mean", "Median", "1st Quartile", "3rd Quartile",
                    "Missing values", "St.Dev", "Skewness", "Kurtosis")
    overall[,2] = c(min(dataset[,feature], na.rm = T),
                    max(dataset[,feature], na.rm = T),
                    base::mean(dataset[,feature], na.rm = T),
                    median(dataset[,feature], na.rm = T),
                    quantile(dataset[,feature], probs = 0.25, na.rm = T),
                    quantile(dataset[,feature], probs = 0.75, na.rm = T),
                    sum(is.na(dataset[,feature])),
                    sd(dataset[,feature], na.rm = T),
                    skewness(dataset[,feature], na.rm = T),
                    kurtosis(dataset[,feature], na.rm = T))
    
    overall = datatable(overall,
                        filter = "bottom",
                        escape = F,
                        options = list(dom = "Blfrtip",
                                       scrollX = T,
                                       lengthMenu = list(c(10, 20 ,50, -1), # declare values
                                                         c(10, 20, 50, "All")), # declare titles # end of lengthMenu customization
                                       pageLength = 10))
    return(overall)
  }
}


# CALCULATE AUC
CalculateAUC <- function(models_list){
  output = as.data.frame(matrix(nrow = length(models_list), ncol=2))
  colnames(output) = c("Dataset", "AUC")
  if (length(models_list) == 6) {
    output[,1]=c("Test all features", "Train all features", "Test selected features", "Train selected features",
                 "Test no population", "Train no population")
  } else if(length(models_list) == 2) {
    output[,1] = c("Test", "Train")
  } else {
    output[,1] = c("Gradient Boosted Machine", "Neural Network", "Regression Random Forest",
                   "Penalized Regression", "Classification Random Forest")
  }
  for (i in (1:length(models_list))) {
    output[i,2] = fastAUC(models_list[[i]]['Score'], models_list[[i]]['Label'])
  }
  output = datatable(output, rownames = FALSE, options = list(dom = 't', pageLength = -1),
                     caption = htmltools::tags$caption(
                       style = 'caption-side: top; text-align: center; font-size:16px;font-weight: bold; color:black;',
                       'Area under curve')) %>%
    formatRound(digits = 2, columns = 2)
  return(output)
}

# FAST AUC
fastAUC <- function(probs, class) {
  x <- probs
  y <- class
  x1 = x[y==1]; n1 = length(x1); 
  x2 = x[y==0]; n2 = length(x2);
  r = rank(c(x1,x2))  
  auc = (sum(r[1:n1]) - n1*(n1+1)/2) / n1 / n2
  return(auc)
}


# PLOT MODEL PERFORMANCE
plot_model_performance <- function(results_list, red_cut_off=0.3, amber_cut_off=0.7){
  model_perf = plot_ly(
    x=results_list[[1]]$X_coordinates,
    y=results_list[[1]]$y_coordinates,
    type='scatter',
    mode='line',
    name="Test dataset",
    line=list(color='#197519')) %>% #'#dd4b39'
    
    add_trace(
      x=results_list[[2]]$X_coordinates,
      y=results_list[[2]]$y_coordinates,
      name="Train dataset",
      line=list(color='#2a88ad')) %>% # 'rgb(255, 153, 0)'
    
    add_segments(x=red_cut_off,
                 xend=red_cut_off,
                 y=0, yend=1,
                 name="Red bucket",
                 line=list(color='#a83e32', width=3)) %>%
    add_segments(x=amber_cut_off,
                 xend=amber_cut_off,
                 y=0, yend=1,
                 name="Amber bucket",
                 line=list(color='#e8b43a', width=3)) %>%
    
    layout(title='<b>Model performance</b>',
           titlefont=list(size=22,
                          color='black',
                          face='bold'),
           margin=list(t=50),
           xaxis=list(tickformat="%",
                      title="% of cases"),
           yaxis=list(tickformat="%",
                      title="% of errors found"))
  return(model_perf)
}

# CUT OFF DISTRIBUTION TABLE 
cut_off_distribution_table <- function(results_list,
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

function(dataset,
         Variable_importance_all_methods=NA,
         colnames_feature_selection=NA,
         stage="Model_results",
         nn_results=NA,
         gbm_results=NA,
         rf_results=NA){

  if(stage=="Model_results"){
    ui <- dashboardPage(
      skin='red',
      dashboardHeader(title="AI Assistant",
                      dropdownMenuOutput("messageMenu")),
      
      # Setting up side bar on the left
      dashboardSidebar(sidebarMenu(
        menuItem("Statistics", tabName = "stats", icon = icon("stats", lib="glyphicon")),
        menuItem("Neural Network", tabName = "nn", icon = icon("chess-queen")),
        menuItem("Summary", tabName = "summary", icon = icon("crown"))#,
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
                                   tags$style('#Feature_statistics{background-color: #D04A02 !important;}'),
                                   selectInput("Feature_statistics", "Select feature",
                                               choices = colnames(dataset)[-1]),
                                   DT::dataTableOutput("statistics")),
                               
                               box(height = "700px", width=9,
                                   selectInput("basic_plots_select","Select type of plot",
                                               choices = c("histogram","boxplot")),
                                   plotlyOutput('basic_plots')))))),
          tabItem(tabName="nn",
                    fluidRow(
                      tabBox(
                        title = "Neural Network",
                        # The id lets us use input$tabset1 on the server to find the current tab
                        id = "tabset8", height = "900px", width = "300px",
                        tabPanel("Neural Network",
                                 # CHANGED
                                 selectInput("Category_selection_nn", "Select labels",
                                             choices = nn_results[[1]][['CategoryName']], # CHANGED
                                             selected = "Control"
                                 ),
                                 # CHANGED PC
                                 column(width = 2,
                                        sliderInput("red_cut_off", "Select red bucket cut off [%]",
                                                    min=0, max = 100, value=30)),
                                 column(width = 2,
                                        sliderInput("amber_cut_off", "Select amber cut off [%]",
                                                    min=0, max = 100, value=70)),
                                 box(width=2,
                                     tableOutput("amount_table_nn")),
                                 column(width = 1), #,offset=4
                                 box(width = 2,
                                     dataTableOutput("nn_AUC")          
                                 ),
                                 # CHANGED PC - added table
                                 fluidPage(column(10, offset = 4, titlePanel("Buckets distribution - summary"))),
                                 fluidRow(column(width = 7, offset = 2, DT::dataTableOutput("nn_cut_off_table"))),
                                 
                                 box(width = 10, height = "700px",
                                     plotlyOutput("nn_plot",height = "700px")),
                        )
                      )
                    )),
          tabItem(tabName="summary",
                    fluidRow(
                      tabBox(
                        title = "Summary",
                        # The id lets us use input$tabset1 on the server to find the current tab
                        id = "tabset9", height = "1800px", width = "300px",
                        tabPanel("Summary",
                                 # CHANGED
                                 selectInput("Category_selection_summary", "Select labels",
                                             choices = nn_results[[1]][['CategoryName']], # CHANGED
                                             selected = "Control"),
                                 box(width=4, tableOutput("amount_table")),
                                 column(width=4, offset=4),
                                 box(width=12, dataTableOutput("excel_table_train")),
                                 box(width=12, dataTableOutput("excel_table_test")),
                                 box(width=2, dataTableOutput("best_models_AUC")),
                                 box(width=10, height="600px", plotlyOutput("best_models_plot", height="600px")),
                                 # box(width=12, sliderInput(inputId = "detailed_table_percent",
                                 #                           label = HTML('<font size="4">',"Select percent of populations [%]",'</font size>'),
                                 #                 max = 100,
                                 #                 min=0,
                                 #                 value=75),
                                 #     dataTableOutput("detailed_table"))
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
      
      # feature selection charts
      feature_selection_data = reactive({
        lasso <- filter(Variable_importance_all_methods[[1]], CategoryName == input$Category_selection_fs)
        lasso <- lasso[,-which(colnames(lasso) %in% c('X1', 'CategoryName'))]
        row.names(lasso) <- lasso$V2
        
        boruta <- filter(Variable_importance_all_methods[[2]], CategoryName == input$Category_selection_fs)
        boruta <- boruta[,-which(colnames(boruta) %in% c('X1', 'CategoryName', 'check'))]
        row.names(boruta) <- boruta$V2
        
        random_forest <- filter(Variable_importance_all_methods[[3]], CategoryName == input$Category_selection_fs)
        random_forest <- random_forest[,-which(colnames(random_forest) %in% c('X1', 'CategoryName'))]
        row.names(random_forest) <- random_forest$V2
        
        feature_selection_filtered <- list(lasso, boruta, random_forest)
      })
      
      output$features_selected_for_the_model = renderDataTable({
        selected_features_table(method = input$Feature_selection_model,
                                Variable_importance_all_methods = feature_selection_data())
      })
      output$confirmed_rejected = renderDataTable({
        datatable(feature_importance_table(input$Feature_selection_feature,
                                           Variable_importance_all_methods = feature_selection_data()),
                  options=list(dom='t'))
      })
      output$significance_level_features = renderPlotly({
        if (input$Feature_selection_model=="Lasso") {
          plot_ly(data=feature_selection_data()[[1]],
                  x=~V3,
                  y=~Overall,
                  text=~V2,
                  name = feature_selection_data()[[1]]$V2,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=10,name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50))
        } else if(input$Feature_selection_model=="Boruta"){
          plot_ly(data=feature_selection_data()[[2]],
                  x=(1:nrow(feature_selection_data()[[2]])),
                  y=~meanImp,
                  name=feature_selection_data()[[2]]$V7,
                  text=~V7,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=min(feature_selection_data()[[2]][feature_selection_data()[[2]]$decision=="Confirmed",1]),name='Cut-off',mode='lines')%>%
            layout(showlegend=F,yaxis=list(title="Significance level"),xaxis=list(title="Features"),
                   title=paste("<b> Features selected by ",input$Feature_selection_model,sep=""),titlefont=list(size=22,color='black',face='bold'),margin=list(t=50))
        }else if(input$Feature_selection_model=="RF"){
          plot_ly(data=feature_selection_data()[[3]],
                  x=(1:nrow(feature_selection_data()[[3]])),
                  y=feature_selection_data()[[3]][,1],
                  text=~V2,
                  name=feature_selection_data()[[3]]$V2,
                  type='scatter',
                  mode='lines+markers')%>%
            add_trace(y=quantile(feature_selection_data()[[3]][,1],probs = 0.1),name='Cut-off',mode='lines')%>%
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
      
      # CHANGED
      nn_results_data = reactive({
        dataset1_nn <- filter(nn_results[[1]], CategoryName == input$Category_selection_nn)
        dataset1_nn <- dataset1_nn[,-which(colnames(dataset1_nn) %in% c('CategoryName'))]
        dataset2_nn <- filter(nn_results[[2]], CategoryName == input$Category_selection_nn)
        dataset2_nn <- dataset2_nn[,-which(colnames(dataset2_nn) %in% c('CategoryName'))]
        nn_results_filtered <- list(dataset1_nn, dataset2_nn)
      })
      
      # Frequencies on NN tab
      output$amount_table_nn=renderTable({
        amount_table=data.frame(matrix(nrow = 2,ncol = 3))
        colnames(amount_table)=c("Whole dataset", "Train data", "Test data")
        row.names(amount_table)=c("Number of cases[errors]", "Error Ratio")
        amount_table$`Whole dataset`[1] = paste(nrow(nn_results_data()[[1]]) + nrow(nn_results_data()[[2]]),'[',sum(nn_results_data()[[1]]$Label)+sum(nn_results_data()[[2]]$Label),']',sep='')
        amount_table$`Train data`[1] = paste(nrow(nn_results_data()[[2]]),'[',sum(nn_results_data()[[2]]$Label),']',sep='')
        amount_table$`Test data`[1]=paste(nrow(nn_results_data()[[1]]),'[',sum(nn_results_data()[[1]]$Label),']',sep='')
        amount_table$`Whole dataset`[2]=paste(round(100*(sum(nn_results_data()[[1]]$Label)+sum(nn_results_data()[[2]]$Label))/(nrow(nn_results_data()[[1]])+nrow(nn_results_data()[[2]])),digits = 2),'%',sep='')
        amount_table$`Train data`[2]=paste(round(100*sum(nn_results_data()[[2]]$Label)/nrow(nn_results_data()[[2]]),digits = 2),'%',sep='')
        amount_table$`Test data`[2]=paste(round(100*sum(nn_results_data()[[1]]$Label)/nrow(nn_results_data()[[1]]),digits = 2),'%',sep='')
        amount_table
      }, rownames = T)
      
      gbm_results_data = reactive({
        dataset1_gbm <- filter(gbm_results[[1]], CategoryName == input$Category_selection_gbm) # CHANGED
        dataset1_gbm <- dataset1_gbm[,-which(colnames(dataset1_gbm) %in% c('CategoryName'))]
        dataset2_gbm <- filter(gbm_results[[2]], CategoryName == input$Category_selection_gbm) # CHANGED
        dataset2_gbm <- dataset2_gbm[,-which(colnames(dataset2_gbm) %in% c('CategoryName'))]
        gbm_results_filtered <- list(dataset1_gbm, dataset2_gbm)
      })
      
      rf_results_data = reactive({
        dataset1_rf <- filter(rf_results[[1]], CategoryName == input$Category_selection_rf) # CHANGED 
        dataset1_rf <- dataset1_rf[,-which(colnames(dataset1_rf) %in% c('CategoryName'))]
        dataset2_rf <- filter(rf_results[[2]], CategoryName == input$Category_selection_rf) # CHANGED
        dataset2_rf <- dataset2_rf[,-which(colnames(dataset2_rf) %in% c('CategoryName'))]
        rf_results_filtered <- list(dataset1_rf, dataset2_rf)
      })
      
      #gbm_data <- reactive({
      #  switch(input$gbm_results,
      #         "All errors" = 1,
      #         "Minor" = 2,
      #         "Major" = 3,
      #         "Critical" = 4)
      #})
      output$gbm_AUC=renderDataTable({
        CalculateAUC(gbm_results_data())
      })
      output$gbm_plot=renderPlotly({
        plot_model_performance(gbm_results_data())
      })
      #nn_data <- reactive({
      #  switch(input$nn_results,
      #         "All errors" = 1,
      #         "Minor" = 2,
      #         "Major" = 3,
      #         "Critical" = 4)
      #})
      
      output$nn_AUC=renderDataTable({
        CalculateAUC(nn_results_data())
      })
      
      # CHANGE PC - ADDED PARAMS
      output$nn_plot=renderPlotly({
        plot_model_performance(nn_results_data(),
                               red_cut_off = input$red_cut_off / 100,
                               amber_cut_off = input$amber_cut_off / 100)
      })
      
      # CHANGED PC - ADDED TABLE 
      output$nn_cut_off_table <- DT::renderDataTable({
        table_cut_offs <- cut_off_distribution_table(
          results_list = nn_results_data(), 
          red_cut_off = input$red_cut_off / 100,
          amber_cut_off = input$amber_cut_off / 100)
        
        table_cut_offs
      })
      
      #rf_data <- reactive({
      #  switch(input$rf_results,
      #         "All errors" = 1,
      #         "Minor" = 2,
      #         "Major" = 3,
      #         "Critical" = 4)
      #})
      output$rf_AUC=renderDataTable({
        CalculateAUC(rf_results_data())
      })
      output$rf_plot=renderPlotly({
        plot_model_performance(rf_results_data())
      })
      
      # CHANGED
      summary_results_data = reactive({
        dataset1_sm <- filter(nn_results[[1]], CategoryName == input$Category_selection_summary) # CHANGED
        dataset1_sm <- dataset1_sm[,-which(colnames(dataset1_sm) %in% c('CategoryName'))]
        dataset2_sm <- filter(nn_results[[2]], CategoryName == input$Category_selection_summary) # CHANGED
        dataset2_sm <- dataset2_sm[,-which(colnames(dataset2_sm) %in% c('CategoryName'))]
        summary_results_filtered <- list(dataset1_sm, dataset2_sm)
      })
      
      
      # Frequencies table on summary tab
      output$amount_table=renderTable({
        amount_table=data.frame(matrix(nrow = 2,ncol = 3))
        colnames(amount_table)=c("Whole dataset", "Train data", "Test data")
        row.names(amount_table)=c("Number of cases[errors]", "Error Ratio")
        amount_table$`Whole dataset`[1]=paste(nrow(summary_results_data()[[1]])+nrow(summary_results_data()[[2]]),'[',sum(summary_results_data()[[1]]$Label)+sum(summary_results_data()[[2]]$Label),']',sep='')
        amount_table$`Train data`[1]=paste(nrow(summary_results_data()[[2]]),'[',sum(summary_results_data()[[2]]$Label),']',sep='')
        amount_table$`Test data`[1]=paste(nrow(summary_results_data()[[1]]),'[',sum(summary_results_data()[[1]]$Label),']',sep='')
        amount_table$`Whole dataset`[2]=paste(round(100*(sum(summary_results_data()[[1]]$Label)+sum(summary_results_data()[[2]]$Label))/(nrow(summary_results_data()[[1]])+nrow(summary_results_data()[[2]])),digits = 2),'%',sep='')
        amount_table$`Train data`[2]=paste(round(100*sum(summary_results_data()[[2]]$Label)/nrow(summary_results_data()[[2]]),digits = 2),'%',sep='')
        amount_table$`Test data`[2]=paste(round(100*sum(summary_results_data()[[1]]$Label)/nrow(summary_results_data()[[1]]),digits = 2),'%',sep='')
        amount_table
      }, rownames = T)
      
      # CHANGED
      gbm_results_table = reactive({
        dataset1_gbm <- filter(gbm_results[[1]], CategoryName == input$Category_selection_summary) # CHAHGED
        dataset1_gbm <- dataset1_gbm[,-which(colnames(dataset1_gbm) %in% c('CategoryName'))]
        dataset2_gbm <- filter(gbm_results[[2]], CategoryName == input$Category_selection_summary) # CHANGED
        dataset2_gbm <- dataset2_gbm[,-which(colnames(dataset2_gbm) %in% c('CategoryName'))]
        gbm_results_filtered <- list(dataset1_gbm, dataset2_gbm)
      })
      nn_results_table = reactive({
        dataset1_nn <- filter(nn_results[[1]], CategoryName == input$Category_selection_summary)
        dataset1_nn <- dataset1_nn[,-which(colnames(dataset1_nn) %in% c('CategoryName'))]
        dataset2_nn <- filter(nn_results[[2]], CategoryName == input$Category_selection_summary)
        dataset2_nn <- dataset2_nn[,-which(colnames(dataset2_nn) %in% c('CategoryName'))]
        nn_results_filtered <- list(dataset1_nn, dataset2_nn)
      })
      
      rf_results_table = reactive({
        dataset1_rf <- filter(rf_results[[1]], CategoryName == input$Category_selection_summary) # CHANGED
        dataset1_rf <- dataset1_rf[,-which(colnames(dataset1_rf) %in% c('CategoryName'))]
        dataset2_rf <- filter(rf_results[[2]], CategoryName == input$Category_selection_summary) # CHANGED
        dataset2_rf <- dataset2_rf[,-which(colnames(dataset2_rf) %in% c('CategoryName'))]
        rf_results_filtered <- list(dataset1_rf, dataset2_rf)
      })
      
      # Error catching table
      output$excel_table_train=renderDataTable({
        best_models_train = list(gbm_results_table()[[2]], nn_results_table()[[2]], rf_results_table()[[2]])
        excel_table_train = as.data.frame(matrix(nrow=3,ncol=13))
        excel_table_train$V1 = c("Gradient Boosted Machine","Neural Network","Classification Random Forest")
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
        datatable(excel_table_train, container = sketch_train,rownames = F,options = list(dom='t',columnDefs=list(list(className="dt-center"))),
                  caption = htmltools::tags$caption(
                    style = 'caption-side: top; text-align: center; font-size:22px;font-weight: bold; color:black;',
                    'Model performance on specifyied checkpoints for train dataset'))%>%
          formatPercentage(digits = 2,columns = c(3,5,7,9,11,13))
      })
      
      output$excel_table_test=renderDataTable({
        best_models_test = list(gbm_results_table()[[1]], nn_results_table()[[1]], rf_results_table()[[1]])
        excel_table_test = as.data.frame(matrix(nrow=3,ncol=13))
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
        best_models=list(gbm_results_table()[[1]], nn_results_table()[[1]], rf_results_table()[[1]])
        plot_ly(x=best_models[[1]]$X_coordinates, y=best_models[[1]]$y_coordinates, type='scatter',mode='line',name="Gradient Boosted Machine",line=list(color='#dd4b39'))%>%
          add_trace(x=best_models[[2]]$X_coordinates,y=best_models[[2]]$y_coordinates,name="Neural Network",line=list(color='#FFB600'))%>%
          add_trace(x=best_models[[3]]$X_coordinates,y=best_models[[3]]$y_coordinates,name="Classification Random Forest",line=list(color='#7D7D7D'))%>%
          layout(title='<b>Model performance</b>',titlefont=list(size=22,color='black',face='bold'),margin=list(t=50),xaxis=list(tickformat="%",title="% of cases"),yaxis=list(tickformat="%",title="% of errors found"))
      })
      output$detailed_table=renderDataTable({
        fraction = input$detailed_table_percent/100
        detailed_table = data.frame(matrix(nrow = 1,ncol=6))
        colnames(detailed_table)=c("No. cases", "Errors found","Errors not found","% of errors found",
                                   "Error ratio in population selected for QC","Error ratio in population not selected for QC")
        
        detailed_table$`No. cases`=round(fraction*nrow(gbm_results_table()[[1]]))
        detailed_table$`Errors found`=sum(gbm_results_table()[[1]][round(fraction*nrow(gbm_results_table()[[1]])),]$Sum)
        detailed_table$`Errors not found`=sum(gbm_results_table()[[1]]$Label)-detailed_table$`Errors found`
        detailed_table$`Error ratio in population selected for QC`=detailed_table$`Errors found`/detailed_table$`No. cases`
        detailed_table$`Error ratio in population not selected for QC`=detailed_table$`Errors not found`/(nrow(gbm_results[[1]])-detailed_table$`No. cases`)
        detailed_table$`% of errors found`=detailed_table$`Errors found`/(detailed_table$`Errors found`+detailed_table$`Errors not found`)
        
        
        
        
        datatable(detailed_table,rownames = F,options = list(dom='t',columnDefs=list(list(className="dt-center"))),
                  caption = htmltools::tags$caption(
                    style = 'caption-side: top; text-align: center; font-size:22px;font-weight: bold; color:black;',
                    paste('Detailed results for', input$detailed_table_percent,'% of the population')))%>%
          formatPercentage(digits = 2,columns = c(4,5,6,7,8))
        
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
        model_vs_time(PQC_results = gbm_results[[2]],RQC_results = gbm_results[[1]],threshold = input$threshold/100,type = input$model_vs_time_type,time_frame = input$time_frame)
      })
      
      output$histogram_error_ratio_model_performance = renderPlotly({
        histogram_error_ratio_model_performance(PQC_results = gbm_results[[2]],RQC_results = gbm_results[[1]],threshold = input$threshold/100,type = input$model_vs_time_type)
      })
      
      output$histogram_box_avg_score=renderPlotly({
        histogram_box_avg_score(RQC_results = gbm_results[[1]],PQC_results = gbm_results[[2]],type = input$histogram_box_avg_score_type,last_x_days = input$last_x_days)
      })
      
    }
    # Run the application 
    shinyApp(ui = ui, server = server)
  }
  
}