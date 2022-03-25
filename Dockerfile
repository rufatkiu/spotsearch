FROM base-env-image as builder
# base-env-image -> ${CI_REGISTRY_IMAGE}/env

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

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "--pythonpath", "/usr/local/lib/python3.9/site-packages", "searx.webapp:app"]
