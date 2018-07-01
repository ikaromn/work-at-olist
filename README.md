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
$ git clone git@github.com:heroku/python-getting-started.git
$ cd python-getting-started

$ pipenv install

$ createdb callcenter

$ python manage.py migrate
$ python manage.py collectstatic


$ python manage.py runserver 0.0.0.0:8000
```
