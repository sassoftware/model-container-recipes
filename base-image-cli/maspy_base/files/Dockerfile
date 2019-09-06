FROM centos

LABEL maspy score box - base

ENV INSTALL_DIR /opt/conda
ENV PATH $INSTALL_DIR/bin:$PATH

USER root
RUN yum update -y
RUN yum install -y wget python3-pandas bzip2 epel-release git numactl net-tools lsof strace vim sysstat
RUN yum clean all

# Miniconda 3
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p $INSTALL_DIR && \
    rm ~/miniconda.sh && \
    $INSTALL_DIR/bin/conda clean -tipsy && \
    ln -s $INSTALL_DIR/etc/profile.d/conda.sh /etc/profile.d/conda.sh

RUN $INSTALL_DIR/bin/pip install --upgrade pip; \
    $INSTALL_DIR/bin/pip install pandas numpy sklearn; \
    $INSTALL_DIR/bin/pip install flask gunicorn;

WORKDIR /pybox/app

COPY app    /pybox/app
COPY model  /pybox/model

# libs directory is fixed for the profile 'mascontainer' in mascfg.py
COPY libs   /opt/sas/viya/libs

RUN chmod 755 /opt/sas/viya/libs/*

EXPOSE 8080:8080
ENTRYPOINT ["/bin/bash", "startServer.sh"]

