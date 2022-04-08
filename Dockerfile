<<<<<<< HEAD
FROM base-env-image as builder
# base-env-image -> ${CI_REGISTRY_IMAGE}/env
=======
FROM alpine:3.15
ENTRYPOINT ["/sbin/tini","--","/usr/local/searx/dockerfiles/docker-entrypoint.sh"]
EXPOSE 8080
VOLUME /etc/searx
VOLUME /var/log/uwsgi
>>>>>>> 03eb9c2461194b81ce978253aceaab587cca975f

COPY . /src/
RUN pip install --force-reinstall --prefix /install /src

FROM python:3.9-slim
LABEL maintainer="dev@e.email"
LABEL description="A privacy-respecting, hackable metasearch engine."

RUN apt-get update -y && apt-get install -y libxslt1.1
RUN pip install gunicorn==20.0.4

COPY --from=builder /install/ /usr/local/

EXPOSE 80
STOPSIGNAL SIGINT

<<<<<<< HEAD
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "--pythonpath", "/usr/local/lib/python3.9/site-packages", "searx.webapp:app"]
=======
COPY requirements.txt ./requirements.txt

RUN apk upgrade --no-cache \
 && apk add --no-cache -t build-dependencies \
    build-base \
    py3-setuptools \
    python3-dev \
    libffi-dev \
    libxslt-dev \
    libxml2-dev \
    openssl-dev \
    tar \
    git \
 && apk add --no-cache \
    ca-certificates \
    su-exec \
    python3 \
    py3-pip \
    libxml2 \
    libxslt \
    openssl \
    tini \
    uwsgi \
    uwsgi-python3 \
    brotli \
 && pip3 install --upgrade pip wheel setuptools \
 && pip3 install --no-cache -r requirements.txt \
 && apk del build-dependencies \
 && rm -rf /root/.cache

COPY searx ./searx
COPY dockerfiles ./dockerfiles

ARG TIMESTAMP_SETTINGS=0
ARG TIMESTAMP_UWSGI=0
ARG VERSION_GITCOMMIT=unknown

RUN /usr/bin/python3 -m compileall -q searx; \
    touch -c --date=@${TIMESTAMP_SETTINGS} searx/settings.yml; \
    touch -c --date=@${TIMESTAMP_UWSGI} dockerfiles/uwsgi.ini; \
    if [ ! -z $VERSION_GITCOMMIT ]; then\
      echo "VERSION_STRING = VERSION_STRING + \"-$VERSION_GITCOMMIT\"" >> /usr/local/searx/searx/version.py; \
    fi; \
    find /usr/local/searx/searx/static -a \( -name '*.html' -o -name '*.css' -o -name '*.js' \
    -o -name '*.svg' -o -name '*.ttf' -o -name '*.eot' \) \
    -type f -exec gzip -9 -k {} \+ -exec brotli --best {} \+

# Keep these arguments at the end to prevent redundant layer rebuilds
ARG LABEL_DATE=
ARG GIT_URL=unknown
ARG SEARX_GIT_VERSION=unknown
ARG LABEL_VCS_REF=
ARG LABEL_VCS_URL=
LABEL maintainer="searx <${GIT_URL}>" \
      description="A privacy-respecting, hackable metasearch engine." \
      version="${SEARX_GIT_VERSION}" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.name="searx" \
      org.label-schema.version="${SEARX_GIT_VERSION}" \
      org.label-schema.url="${LABEL_VCS_URL}" \
      org.label-schema.vcs-ref=${LABEL_VCS_REF} \
      org.label-schema.vcs-url=${LABEL_VCS_URL} \
      org.label-schema.build-date="${LABEL_DATE}" \
      org.label-schema.usage="https://github.com/searx/searx-docker" \
      org.opencontainers.image.title="searx" \
      org.opencontainers.image.version="${SEARX_GIT_VERSION}" \
      org.opencontainers.image.url="${LABEL_VCS_URL}" \
      org.opencontainers.image.revision=${LABEL_VCS_REF} \
      org.opencontainers.image.source=${LABEL_VCS_URL} \
      org.opencontainers.image.created="${LABEL_DATE}" \
      org.opencontainers.image.documentation="https://github.com/searx/searx-docker"
>>>>>>> 03eb9c2461194b81ce978253aceaab587cca975f
