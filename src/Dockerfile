FROM python:3.11-slim-bookworm

COPY ./src /app/
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev libpq-dev

# venv & installs

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install pip --upgrade && \
    /opt/venv/bin/python -m pip install -r /app/requirements.txt

# purge unused
RUN apt-get remove -y --purge gcc libc6-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*


RUN chmod +x ./config/entrypoint.sh

CMD ["./config/entrypoint.sh"]