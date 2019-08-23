FROM postgres:9.5

ARG ES_PIP_VERSION

RUN apt-get update
RUN apt-get install --yes --force-yes \
    build-essential                   \
    libffi-dev                        \
    libssl-dev                        \
    postgresql-9.5-python-multicorn   \
    python                            \
    python-dev                        \
    python-pip
RUN pip install $ES_PIP_VERSION

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python setup.py install
