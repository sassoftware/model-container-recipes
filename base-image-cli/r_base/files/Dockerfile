From continuumio/miniconda3:latest

LABEL R score box - base

USER root

ENV PYTHON_VERSION 3.8

RUN conda install -y python=${PYTHON_VERSION}

RUN pip install --upgrade pip; \
    pip install jsonify; \
    pip install flask gunicorn;

# install r-base
RUN conda install -y r-base=3.5.1

# include R packages
RUN Rscript -e "install.packages('rpart',repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('RCurl',repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('jsonlite',repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('argparse',repos='http://cran.us.r-project.org')"

WORKDIR /pybox/app

COPY app    /pybox/app
COPY model  /pybox/model

EXPOSE 8080:8080
ENTRYPOINT ["/bin/bash", "startServer.sh"]

