ARG DEBIAN_VERSION="${DEBIAN_VERSION:-slim-buster}"
ARG PYTHON_VERSION="${PYTHON_VERSION:-3.8}"
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} as base

FROM base as python_dependencies

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

ARG REQUIREMENTS="${REQUIREMENTS:-requirements.txt}"
COPY ./requirements*.txt /code/
RUN echo "{\"process\": \"build\", \"event\": \"install_python_dependencies\", \"file\": \"$REQUIREMENTS\"}" \
    && touch /pip.log \
    && mkdir /install \
    && (pip-sync /code/"${REQUIREMENTS}" --pip-args "--no-cache-dir --force-reinstall --upgrade --log /pip.log --no-warn-script-location --prefix=/install" \
    || (cat /pip.log; exit 1)) \
    && rm -f /pip.log \
    && apt-get remove --purge -yq \
        git \
        gcc \
        build-essential \
    && apt-get autoremove --purge -yqq \
    && apt-get clean \
    && rm -rf /var/tmp/* /tmp/* /var/lib/apt/lists/*

FROM base
COPY --from=python_dependencies /install /usr/local

# Set python env vars
# No *.pyc.
ENV PYTHONDONTWRITEBYTECODE 1
# Print immediately, no print buffering.
ENV PYTHONUNBUFFERED 1

ARG USER_NAME="${USER_NAME:-user}"
ENV USER_NAME ${USER_NAME}
ARG USER_ID=1000
ARG GROUP_ID=1000

WORKDIR /code

# https://stackoverflow.com/questions/48671214/docker-image-size-for-different-user
RUN addgroup --system --gid "${GROUP_ID}" "${USER_NAME}" && adduser --system --uid "${USER_ID}" --ingroup "${USER_NAME}" --disabled-password --shell /bin/false "${USER_NAME}"

RUN apt-get update -qq && apt-get install -yqq --no-install-recommends \
        gosu \
    && apt-get autoremove --purge -yqq \
    && apt-get clean \
    && rm -rf /var/tmp/* /tmp/* /var/lib/apt/lists/*

VOLUME "/code"

COPY --chown=root:root ./entrypoint.sh /entrypoint.sh
RUN  chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["echo", "Not yet implemented."]
