#!/bin/sh
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

exec gunicorn --bind 0.0.0.0:8080 server:app \
    --log-level=debug \
    --log-file=/var/log/gunicorn.log \
    --access-logfile=/var/log/gunicorn-access.log \
"$@"

# --daemon

