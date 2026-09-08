FROM node:24.13.1-bookworm-slim@sha256:a81a03dd965b4052269a57fac857004022b522a4bf06e7a739e25e18bce45af2 AS node_runtime
FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node_runtime /usr/local/LICENSE /usr/local/share/doc/node/LICENSE
COPY requirements.lock.txt /opt/eps-baseline/requirements.lock.txt
RUN pip install --no-cache-dir -r /opt/eps-baseline/requirements.lock.txt
WORKDIR /work
