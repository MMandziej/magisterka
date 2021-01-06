ui = fluidPage(
  useShinyjs(),#useShinyalert(),
  tags$style(type = "text/css",
             'body{background-color: #3F3F3F;text-align: justify;}'),
  fluidRow(
    column(width = 12,
           style = "background: linear-gradient(90deg, #27282C, #1F1F22); color : white; font-size: 36px",
           #style = "background: linear-gradient(135deg, #EA8D2A, #DD660E);")
           img(src="http://gx-zweappplv109.glblcloud.ad.pwcinternal.com:8008/static/img/icons/pwc.png",
               height = 69.25, width = 70, align = "left"),
           h1("Lion King's shiny applications", style = "margin-left: 8.4%")
    )
  ),
  fluidRow(
    column(width = 4,
           offset = 1,
           br(),br(),
           align = "left",
           actionButton(
             width = "90%",
             inputId = 'ai_assistant',
             onclick ="location.href='http://gx-zweappplv109.glblcloud.ad.pwcinternal.com:8081/'",
             label = "AI Assistant (PC Stage)",
             icon = icon("calculator"),
             style = "white-space: normal; text-align: left; background: linear-gradient(135deg, #EA8D2A, #DD660E);color : white; border-color:#3f3f3f; font-size: 34px;padding: 12px 12px;")
           ,br(),br()),
    column(width = 6,br(),br(),
           helpText(HTML("Development of machine learning models contain multi-level processes, where each step requires in depth analysis. it's very important to make sure that the dataset is properly prepared and the impact of each feature is well examined by Data Scientists. Then, comfortably model development stage can be followed then different models can be compared to choose the best one available.
<br>
<b>AI Assistant</b> enables Data Scientists to easily conduct exploratory data analysis to understand structure of the data and analyze correlations, run different feature selection methods to understand importance of the features, compare performance of different models and check model's stability in time.
"),
                    style = "background: linear-gradient(90deg, #BEBFC7, #9E9FA7);color : black; border-color:#3f3f3f; font-size: 14px;border-radius: 4px;padding: 5px;"))
  ),
  fluidRow(
    column(width = 4,
           offset = 1,
           br(),br(),
           align = "left",
           actionButton(
             width = "90%",
             inputId = 'lion_king_monitoring',
             onclick ="location.href='http://gx-zweappplv109.glblcloud.ad.pwcinternal.com:8083/'",
             label = "Predictive QC Monitoring (DR Stage)",
             icon = icon("chart-bar"),
             style = "white-space: normal; text-align: left; background: linear-gradient(135deg, #EA8D2A, #DD660E);color : white; border-color:#3f3f3f; font-size: 34px;padding: 12px 12px;")
           ,br(),br()),
    column(width = 6,br(),br(),
           helpText(HTML("Monitoring of machine learning models refers to the way its performance is tracked and any shift of data is being represented. It's valuable both for data scientists and production. Proper monitoring ensures stability in production and enables users to be on track with population changes. Developed monitoring page includes basic data regarding Predictive Sampling, model performance results and comparison of QC's results and PS scores."),
                    style = "background: linear-gradient(90deg, #BEBFC7, #9E9FA7);color : black; border-color:#3f3f3f; font-size: 14px;border-radius: 4px;padding: 5px;"))
  )
)
server = function(input,output,session){
  # observeEvent(input$boat_automation_log_inspection, {
  #   shinyalert("Please enter the password.", type = "input",
  #              callbackR = function(x){
  #                if(x=="password"){
  #                  #shell.exec("http://gx-zweappplv109.glblcloud.ad.pwcinternal.com:8012/")
  #                  #browseURL("http://gx-zweappplv109.glblcloud.ad.pwcinternal.com:8012/")
  #                  runjs("location.href='http://gx-zweappplv109.glblcloud.ad.pwcinternal.com:8005/'")
  #                }else{
  #                  shinyalert("Oops!", "Something went wrong.", type = "error")
  #                }
  #              })
  # 
  # })
}

shinyApp(ui,server)