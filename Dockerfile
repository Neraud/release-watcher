FROM python:3.11.4-alpine3.18

ENV CONFIG_PATH=/data/config.yaml

RUN adduser app -D -u 1000
USER app

ADD --chown=app . /opt/release_watcher

RUN python3 -m pip install /opt/release_watcher

ENTRYPOINT [ "/opt/release_watcher/entrypoint.sh" ]
