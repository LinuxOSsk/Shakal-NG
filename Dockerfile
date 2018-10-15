FROM ubuntu:bionic

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8

RUN apt-get update && apt-get -y install \
 build-essential \
 python3-dev \
 python3-pip \
 libjpeg-dev \
 libfreetype6-dev \
 git \
 curl \
 gettext \
 vim &&\
 apt-get clean

ADD . /opt/shakal/

RUN cd /opt/shakal &&\
 pip3 install --no-cache-dir -r requirements.dev.txt --src /usr/local/src

RUN useradd -ms /bin/bash -u 1000 shakal && chown -R 1000:1000 /opt/shakal

USER shakal
WORKDIR /opt/shakal
EXPOSE 8000

CMD "/bin/bash"
