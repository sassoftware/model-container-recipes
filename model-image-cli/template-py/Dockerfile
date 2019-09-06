ARG base_repo
From ${base_repo}python3-base:latest
LABEL docker image with embedded python model

COPY *.zip /pybox/model

ENTRYPOINT ["/bin/bash", "startServer.sh"]


