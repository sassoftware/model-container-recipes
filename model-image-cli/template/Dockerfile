ARG base_repo
From ${base_repo}maspy-base:latest
LABEL docker image with embedded SAS model

# copy both zip and/or astore file (if any) to model directory
COPY *.* /pybox/model/

ENTRYPOINT ["/bin/bash", "startServer.sh"]


