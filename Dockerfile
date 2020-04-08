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


RUN python --version
RUN pip3 --version

ADD requirements/dev.txt /tmp/dev.txt
RUN pip3 install -r /tmp/dev.txt \
&& rm /tmp/dev.txt

RUN curl -sL https://deb.nodesource.com/setup_10.x -o /tmp/nodejs-setup
RUN /bin/bash /tmp/nodejs-setup
RUN rm /tmp/nodejs-setup
RUN apt-get -y install nodejs

RUN mkdir -p /usr/local/src/xblock-sdk
WORKDIR /usr/local/src/xblock-sdk
ADD . .

RUN virtualenv .env
RUN chmod u+x .env/bin/activate
RUN .env/bin/activate

RUN make install
EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
