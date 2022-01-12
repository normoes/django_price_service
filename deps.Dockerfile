ARG DEBIAN_VERSION="${DEBIAN_VERSION:-slim-buster}"
ARG PYTHON_VERSION="${PYTHON_VERSION:-3.8}"
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION}

COPY ./build_requirements.txt /code/build_requirements.txt

RUN apt-get update -qq && apt-get install -yqq --no-install-recommends \
        git \
        gcc \
        build-essential \
    && apt-get autoremove --purge -yqq \
    && apt-get clean \
    && rm -rf /var/tmp/* /tmp/* /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir --upgrade -r /code/build_requirements.txt

# Set python env vars
# No *.pyc.
ENV PYTHONDONTWRITEBYTECODE 1
# Print immediately, no print buffering.
ENV PYTHONUNBUFFERED 1

# No user handling when building the container because of:
# https://stackoverflow.com/questions/48671214/docker-image-size-for-different-user

ENV DOCKER_ENV="True"

WORKDIR /code

VOLUME "/code"
