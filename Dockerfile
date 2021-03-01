FROM edxops/focal-common:latest
RUN apt-get update && apt-get install -y \
    gettext \
    lib32z1-dev \
    libjpeg62-dev \
    libxslt1-dev \
    zlib1g-dev \
    python3 \
    python3-dev \
    python3-pip && \
    pip3 install --upgrade pip setuptools && \
    rm -rf /var/lib/apt/lists/*

COPY . /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk

RUN ln -s /usr/bin/python3.8 /usr/bin/python && \
    /usr/bin/python3 -m pip install --upgrade pip && \
    pip install -r /usr/local/src/xblock-sdk/requirements/dev.txt

RUN curl -sL https://deb.nodesource.com/setup_14.x -o /tmp/nodejs-setup && \
    /bin/bash /tmp/nodejs-setup && \
    rm /tmp/nodejs-setup && \
    apt-get -y install nodejs && \
    echo $PYTHONPATH && \
    make install

EXPOSE 8000
ENTRYPOINT ["python3", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
