ARG BASE_IMAGE=python:3.8-buster
FROM $BASE_IMAGE

# add kedro user
ARG KEDRO_UID=999
ARG KEDRO_GID=0
RUN groupadd -f -g ${KEDRO_GID} kedro_group && \
    useradd -d /home/kedro -s /bin/bash -g ${KEDRO_GID} -u ${KEDRO_UID} kedro

# copy the whole project except what is in .dockerignore
WORKDIR /home/kedro
COPY . .
RUN chown -R kedro:${KEDRO_GID} /home/kedro
USER kedro
RUN chmod -R a+w /home/kedro

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

EXPOSE 8888

ENV PATH=/home/kedro/.local/bin:$PATH
RUN poetry install

CMD ["poetry", "run", "kedro", "run"]
