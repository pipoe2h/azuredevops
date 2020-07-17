ARG VARIANT="3.7"
FROM python:${VARIANT}

ARG CALM_DSL_TARBALL="https://github.com/nutanix/calm-dsl/archive/master.zip"
WORKDIR /root
RUN mkdir -p `python3 -m site --user-site`
ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y sudo \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/calm-dsl.zip $CALM_DSL_TARBALL

RUN unzip /tmp/calm-dsl.zip -d /tmp \
    && rm /tmp/calm-dsl.zip \
    && cd /tmp/calm-dsl-master \
    && pip3 install --no-cache-dir -r requirements.txt virtualenv --user \
    && make dist \
    && pip3 install --no-cache-dir dist/calm.dsl*.whl --user \
    && cd ~ \
    && rm -fR /tmp/calm-dsl-master 

CMD ["bash"]