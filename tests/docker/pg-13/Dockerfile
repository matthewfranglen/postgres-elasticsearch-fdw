FROM postgres:13

ARG ES_PIP_VERSION

RUN apt-get update
RUN apt-get install --yes           \
    postgresql-13-python3-multicorn \
    python3                         \
    python3-setuptools              \
    python3-pip
RUN pip3 install $ES_PIP_VERSION

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python3 setup.py install
