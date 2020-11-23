## Requirements

Linux, with these libraries installed:
+ g++
+ python3.7+
+ git
+ Docker

## Installation

```
pip3 install --upgrade Cython setuptools
pip3 install -e .
python3 setup.py build_ext --inplace
```

## Usage

You can run a server with
```
python3 -m raid6 [OPTIONS]
```

```
Options:
  -h, --host TEXT          Host address
  -p, --base-port INTEGER  Port of the first server
  -d, --debug              Enable debug mode
  -s, --server-id INTEGER  ID of the current server  [required]
  -k, --primary INTEGER    Number of primary data strips
  -m, --parity INTEGER     Number of parity data strips
  -r, --random             Enable random distribution of data strips
  --data-dir TEXT          Location of data strips
  --help                   Show this message and exit.

```

## Example

Minimum Sample of two servers:

```
mkdir -p server0 && cd server0
python3 -m raid6 -s 0 -k 1 -m 1 --data-dir . &
cd ..
mkdir -p server1 && cd server1
python3 -m raid6 -s 1 -k 1 -m 1 --data-dir . &
```

Then play on
+ http://127.0.0.1:10000/docs
+ http://127.0.0.1:10001/docs

The APIs should have been well-documented

If you want to deploy many data nodes, usage of docker is preferred

## Deployment with Docker

```
docker build -t raid6:latest .
docker-compose up -d
```

The config consists of 6 primary and 2 parity data nodes
