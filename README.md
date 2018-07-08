[![Build Status](https://travis-ci.org/ikaromn/work-at-olist.svg?branch=master)](https://travis-ci.org/ikaromn/work-at-olist)
[![codecov](https://codecov.io/gh/ikaromn/work-at-olist/branch/master/graph/badge.svg)](https://codecov.io/gh/ikaromn/work-at-olist)

# Call Center

An application to record calls and calculation billings

## Requiriments:

```sh
Python 3.6.5
Pipenv
PostgreSQL
```
## Running Locally

```sh
$ git clone https://github.com/ikaromn/work-at-olist.git
$ cd work-at-olist

$ pipenv install

$ createdb callcenter

$ python manage.py migrate
$ python manage.py collectstatic


$ python manage.py runserver 0.0.0.0:8000
```
