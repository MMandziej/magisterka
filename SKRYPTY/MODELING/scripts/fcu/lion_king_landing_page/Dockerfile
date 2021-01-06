FROM rocker/r-ver:3.5.1 

RUN apt-get update && apt-get install -y \
    sudo \
    libmagick++-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libssh2-1-dev \
    libpython3-dev \
    python3-pip \ 
    tesseract-ocr \
    libnss3 \
    libnss3-dbg \
    libnss3-dev \
    libnss3-tools

RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

# install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install


# install R packages required 
# (change it dependeing on the packages you need)
RUN R -e "install.packages('shiny', repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('shinyjs', repos='http://cran.rstudio.com/')"

#copy the current folder into the path of the app
COPY . /usr/local/src/app
#set working directory to the app
WORKDIR /usr/local/src/app

#set the unix commands to run the app
CMD ["Rscript","runApp.R"]