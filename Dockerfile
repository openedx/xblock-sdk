FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    gettext \
    zlib1g-dev \
    libjpeg62-dev \
    libxslt1-dev \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    curl \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk

ENV VIRTUAL_ENV=/venvs/xblock-sdk
RUN python3.12 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN curl -sL https://deb.nodesource.com/setup_22.x -o /tmp/nodejs-setup && \
    bash /tmp/nodejs-setup && \
    rm /tmp/nodejs-setup && \
    apt-get install -y nodejs

RUN pip install --upgrade pip setuptools
RUN make install

EXPOSE 8000

ENTRYPOINT ["bash", "-c", "python manage.py migrate && exec python manage.py runserver 0.0.0.0:8000"]
