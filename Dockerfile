FROM edxops/xenial-common:latest
RUN apt-get update && apt-get install -y \
    gettext \
    lib32z1-dev \
    libjpeg62-dev \
    libxslt-dev \
    python3-dev \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk
ADD . .
RUN easy_install pip
RUN make install
EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
