From centos

LABEL R score box - base

ENV INSTALL_DIR /opt/conda
ENV PATH $INSTALL_DIR/bin:$PATH

USER root
RUN yum update -y
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y wget bzip2 libcurl-devel R
RUN yum clean all

# include R packages
RUN Rscript -e "install.packages('RCurl',repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('jsonlite',repos='http://cran.us.r-project.org')"

# Miniconda 3
# use python 3.6.7 instead of default 3.7
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p $INSTALL_DIR && \
    rm ~/miniconda.sh && \
    $INSTALL_DIR/bin/conda clean -tipsy && \
    $INSTALL_DIR/bin/conda install -y python=3.6.7 && \
    ln -s $INSTALL_DIR/etc/profile.d/conda.sh /etc/profile.d/conda.sh

RUN $INSTALL_DIR/bin/pip install --upgrade pip; \
    $INSTALL_DIR/bin/pip install numpy jsonify pandas; \
    $INSTALL_DIR/bin/pip install flask gunicorn;

WORKDIR /pybox/app

COPY app    /pybox/app
COPY model  /pybox/model

EXPOSE 8080:8080
ENTRYPOINT ["/bin/bash", "startServer.sh"]

