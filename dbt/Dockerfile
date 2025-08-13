FROM python:3.12-slim

WORKDIR /usr/app

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY . .

ENV DBT_PROFILES_DIR=/usr/app/profiles

# for using airflow ssh operator

RUN apt-get update \
    && apt-get install -y openssh-server \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i -E 's/^HostKey /#HostKey /' /etc/ssh/sshd_config \
 && echo 'HostKey /etc/ssh/ssh_host_rsa_key' >> /etc/ssh/sshd_config

ARG SSH_ID
ARG SSH_PASSWORD

RUN useradd -ms /bin/bash $SSH_ID \
    && echo $SSH_ID:$SSH_PASSWORD | chpasswd \
    && mkdir /var/run/sshd

RUN sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

RUN chown -R $SSH_ID:$SSH_ID /usr/app

EXPOSE 22
