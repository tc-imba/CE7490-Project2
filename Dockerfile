FROM ubuntu:20.04

ENV HOME="/root"

RUN apt-get update && \
    apt-get install -y g++ python3-pip git

COPY ./requirements.txt $HOME/raid6/requirements.txt
WORKDIR $HOME/raid6

RUN pip3 install --upgrade Cython setuptools
RUN pip3 install -r requirements.txt

COPY ./ $HOME/raid6
RUN pip3 install -e .
RUN python3 setup.py build_ext --inplace

ENV HOST="127.0.0.1" \
    BASE_PORT=11000 \
    PORT=11000 \
    SERVER_ID=0 \
    PRIMARY=6 \
    PARITY=2

#EXPOSE $PORT

CMD python3 -m raid6 \
    --host $HOST \
    --base-port $BASE_PORT \
    --server-id $SERVER_ID \
    --primary $PRIMARY \
    --parity $PARITY \
    --random


