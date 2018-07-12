[![Build Status](https://travis-ci.org/ikaromn/work-at-olist.svg?branch=master)](https://travis-ci.org/ikaromn/work-at-olist)
[![codecov](https://codecov.io/gh/ikaromn/work-at-olist/branch/master/graph/badge.svg)](https://codecov.io/gh/ikaromn/work-at-olist)

# Call Center

An application to record calls and calculation billings

## Requiriments:

```sh
[Docker](https://docs.docker.com/install/)
[docker-compose](https://docs.docker.com/compose/install/)
```
## Running Locally

After install the requiriments run the follow commands:

### To clone Project:

```sh
$ git clone https://github.com/ikaromn/work-at-olist.git
$ cd work-at-olist
```

### To run the Project:
```sh
$ docker-compose up -d
$ docker-compose exec web bash
# python manage.py migrate
```

If all works fine, go to your web browser and type `http://0.0.0.0:8000`
