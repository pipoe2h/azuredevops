# ARG VARIANT="3.7"
# FROM python:${VARIANT}

FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
RUN echo "APT::Get::Assume-Yes \"true\";" > /etc/apt/apt.conf.d/90assumeyes

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        jq \
        git \
        iputils-ping \
        libcurl4 \
        libicu60 \
        libunwind8 \
        netcat \
        sudo

ARG CALM_DSL_TARBALL="https://github.com/nutanix/calm-dsl/archive/master.zip"
WORKDIR /root
RUN mkdir -p `python3 -m site --user-site`
ENV PATH=/root/.local/bin:$PATH

RUN wget -q -O /tmp/calm-dsl.zip $CALM_DSL_TARBALL \
    && unzip /tmp/calm-dsl.zip -d /tmp \
    && rm /tmp/calm-dsl.zip \
    && cd /tmp/calm-dsl-master \
    && pip3 install --no-cache-dir -r requirements.txt virtualenv --user \
    && make dist \
    && pip3 install --no-cache-dir dist/calm.dsl*.whl --user \
    && cd ~ \
    && rm -fR /tmp/calm-dsl-master

CMD ["bash"]
