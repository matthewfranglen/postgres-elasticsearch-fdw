FROM postgres:10

ARG ES_PIP_VERSION

RUN apt-get update
RUN apt-get install --yes          \
    postgresql-10-python-multicorn \
    python                         \
    python-pip
RUN pip install $ES_PIP_VERSION

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python setup.py install
