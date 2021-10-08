FROM edxops/focal-common:latest
RUN apt-get update && apt-get install -y \
    gettext \
    lib32z1-dev \
    libjpeg62-dev \
    libxslt1-dev \
    zlib1g-dev \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip && \
    pip3 install --upgrade pip setuptools && \
    rm -rf /var/lib/apt/lists/*

COPY . /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk

ENV VIRTUAL_ENV=/venvs/xblock-sdk
RUN python3.8 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip && pip install -r /usr/local/src/xblock-sdk/requirements/dev.txt

RUN curl -sL https://deb.nodesource.com/setup_14.x -o /tmp/nodejs-setup && \
    /bin/bash /tmp/nodejs-setup && \
    rm /tmp/nodejs-setup && \
    apt-get -y install nodejs && \
    echo $PYTHONPATH && \
    make install

EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
