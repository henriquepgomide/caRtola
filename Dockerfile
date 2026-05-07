ARG BASE_IMAGE=python:3.10-buster
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

EXPOSE 8888

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/home/kedro/.local/bin:$PATH

RUN pip install -U pip
RUN poetry export -f requirements.txt --without-hashes > requirements_from_poetry.txt
RUN pip install -r requirements_from_poetry.txt

CMD ["poetry", "run", "kedro", "run"]
