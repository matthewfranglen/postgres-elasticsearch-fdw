FROM postgres:14

ARG ES_PIP_VERSION

RUN echo "deb http://deb.debian.org/debian sid main" >> /etc/apt/sources.list
RUN echo "en_US UTF-8" >> /etc/locale.gen
RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true dpkg-reconfigure locales
RUN apt-get update
RUN apt-get install --yes    \
    clang-13                 \
    git                      \
    postgresql-server-dev-14 \
    python3                  \
    python3-dev              \
    python3-setuptools       \
    python3-pip
RUN git clone https://github.com/pgsql-io/multicorn2 /tmp/multicorn2 && \
    cd /tmp/multicorn2 && \
    PYTHON_OVERRIDE=python3 make install && \
    cp /tmp/multicorn2/multicorn.control /usr/share/postgresql/14/extension/multicorn.control && \
    rm -rf /tmp/multicorn2
RUN pip3 install $ES_PIP_VERSION --break-system-packages

COPY . /pg-es-fdw
WORKDIR /pg-es-fdw
RUN python3 setup.py install
