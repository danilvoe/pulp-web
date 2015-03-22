pulp-web
==================

A simple web UI for interacting with pulp

## Usage

Install pulp and then run ```python run.py``` on the same server.

Browse to ```http://localhost:8080``` to begin using.

## Usage with docker
First to build the image, clone this repository and from inside the checkout :
```
docker build -t pulp-web .
```


Once build is done you can run the container :
```
docker run -p 8080:8080 -e PULPURL="https://<pulp_ip/host>[:port]" pulp-web
```

`PULPURL` default to "localhost"

```
docker run -p 8080:8080 --link pulp-web:pulpapi -e PULPURL="https://pulpapi" pulp-web
```

## Developing

First, download and install all python requirements via pip:
```
pip install -r requirements.txt
```

See the following for creating a Pulp cluster with docker-machine: https://gist.github.com/nextrevision/98da99f0abf8b89d322a

Then run the script locally or in the container as mentioned above.
