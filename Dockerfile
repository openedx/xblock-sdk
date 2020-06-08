FROM edxops/xenial-common:latest
RUN apt-get update && apt-get install -y \
    gettext \
    lib32z1-dev \
    libjpeg62-dev \
    libxslt-dev \
    libz-dev \
    python3.5 \
    python3-dev \
    python3-pip && \
    pip3 install --upgrade pip setuptools && \
    rm -rf /var/lib/apt/lists/*


COPY . /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk

RUN pip install -r /usr/local/src/xblock-sdk/requirements/dev.txt 

RUN curl -sL https://deb.nodesource.com/setup_10.x -o /tmp/nodejs-setup
RUN /bin/bash /tmp/nodejs-setup
RUN rm /tmp/nodejs-setup
RUN apt-get -y install nodejs
RUN echo $PYTHONPATH

RUN make install
EXPOSE 8000
ENTRYPOINT ["python3", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
