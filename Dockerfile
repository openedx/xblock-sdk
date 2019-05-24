FROM edxops/xenial-common:latest
RUN apt-get update && apt-get install -y \
    gettext \
    lib32z1-dev \
    libjpeg62-dev \
    libxslt-dev \
    libz-dev \
    python3-dev \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*

RUN easy_install pip
ADD requirements/dev.txt /tmp/dev.txt
RUN pip install -r /tmp/dev.txt \
&& rm /tmp/dev.txt

RUN mkdir -p /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk
ADD . .
RUN make install
EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
