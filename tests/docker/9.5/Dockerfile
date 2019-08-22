FROM postgres:9.5

RUN apt-get update
RUN apt-get install --yes --force-yes \
    build-essential                   \
    libffi-dev                        \
    libssl-dev                        \
    postgresql-9.5-python-multicorn   \
    python                            \
    python-dev                        \
    python-pip
RUN pip install elasticsearch

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python setup.py install
