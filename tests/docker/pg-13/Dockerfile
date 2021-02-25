FROM postgres:13

ARG ES_PIP_VERSION

RUN apt-get update
RUN apt-get install --yes \
    python3               \
    python3-setuptools    \
    python3-pip           \
    wget
RUN wget -O /tmp/multicorn.deb http://de.archive.ubuntu.com/ubuntu/pool/universe/p/postgresql-multicorn/postgresql-13-python3-multicorn_1.4.0-3_amd64.deb && \
    dpkg -i /tmp/multicorn.deb && \
    rm /tmp/multicorn.deb
RUN pip3 install $ES_PIP_VERSION

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python3 setup.py install
