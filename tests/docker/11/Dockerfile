FROM postgres:11

RUN apt-get update
RUN apt-get install --yes          \
    postgresql-11-python-multicorn \
    python                         \
    python-pip
RUN pip install 'elasticsearch<6'

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python setup.py install
