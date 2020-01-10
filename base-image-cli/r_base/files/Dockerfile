From continuumio/miniconda3:latest

LABEL R score box - base

USER root

RUN pip install --upgrade pip; \
    pip install jsonify; \
    pip install flask gunicorn;

# install r-base
RUN conda install -y r-base

# include R packages
RUN Rscript -e "install.packages('rpart',repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('RCurl',repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('jsonlite',repos='http://cran.us.r-project.org')"

WORKDIR /pybox/app

COPY app    /pybox/app
COPY model  /pybox/model

EXPOSE 8080:8080
ENTRYPOINT ["/bin/bash", "startServer.sh"]

