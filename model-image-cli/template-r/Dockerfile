ARG base_repo
From ${base_repo}r-base:latest
LABEL docker image with embedded R model

COPY *.zip /pybox/model

ENTRYPOINT ["/bin/bash", "startServer.sh"]


