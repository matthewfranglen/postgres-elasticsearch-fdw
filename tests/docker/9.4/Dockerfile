FROM postgres:9.4

RUN apt-get update
RUN apt-key update
RUN apt-get install --yes --force-yes \
    build-essential                   \
    libffi-dev                        \
    libssl-dev                        \
    postgresql-9.4-python-multicorn   \
    python                            \
    python-dev                        \
    python-pip
RUN pip install 'elasticsearch<6'

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python setup.py install
