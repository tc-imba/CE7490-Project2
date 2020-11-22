FROM ubuntu:20.04

ENV HOME="/root"

RUN apt-get update && \
    apt-get install -y g++ python3-pip git

COPY ./ $HOME/raid6

WORKDIR $HOME/raid6
RUN pip3 install --upgrade Cython setuptools
RUN pip3 install -e .
RUN python3 setup.py build_ext --inplace
