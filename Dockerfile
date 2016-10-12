FROM phusion/baseimage:latest
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    lib32z1-dev \
    libjpeg62-dev \
    libxml2-dev \
    libxslt-dev \
    python-dev \
    python-setuptools \
    xz-utils \
&& rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk
ADD . .
RUN easy_install pip
RUN make install
EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
