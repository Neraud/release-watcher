FROM python:3.11.4-alpine3.18

ENV CONFIG_PATH=/data/config.yaml

ADD . /opt/release_watcher

RUN python3 -m pip install /opt/release_watcher

ENTRYPOINT [ "/opt/release_watcher/entrypoint.sh" ]
