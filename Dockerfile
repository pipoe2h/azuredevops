ARG VARIANT="3.7"
FROM python:${VARIANT}

ARG USER_ID
ARG GROUP_ID

RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
USER user

ARG CALM_DSL_TARBALL="https://github.com/nutanix/calm-dsl/archive/master.zip"
# WORKDIR /home/user
# RUN mkdir -p `python3 -m site --user-site`
# ENV PATH=/home/user/.local/bin:$PATH

# RUN wget -q -O /tmp/calm-dsl.zip $CALM_DSL_TARBALL \
#     && unzip /tmp/calm-dsl.zip -d /tmp \
#     && rm /tmp/calm-dsl.zip \
#     && cd /tmp/calm-dsl-master \
#     && pip3 install --no-cache-dir -r requirements.txt virtualenv --user \
#     && make dist \
#     && pip3 install --no-cache-dir dist/calm.dsl*.whl --user \
#     && cd ~ \
#     && rm -fR /tmp/calm-dsl-master

RUN wget -q -O /tmp/calm-dsl.zip $CALM_DSL_TARBALL \
    && unzip /tmp/calm-dsl.zip -d /tmp \
    && rm /tmp/calm-dsl.zip \
    && cd /tmp/calm-dsl-master \
    && pip3 install --no-cache-dir -r requirements.txt virtualenv \
    && make dist \
    && pip3 install --no-cache-dir dist/calm.dsl*.whl \
    && cd ~ \
    && rm -fR /tmp/calm-dsl-master

CMD ["bash"]