FROM postgres:9.4

ARG ES_PIP_VERSION

RUN apt-get update
RUN apt-key update
RUN apt-get install --yes --fix-missing \
    build-essential                     \
    libffi-dev                          \
    libssl-dev                          \
    postgresql-9.4-python-multicorn     \
    python                              \
    python-dev                          \
    python-pip
RUN pip install $ES_PIP_VERSION

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python setup.py install
