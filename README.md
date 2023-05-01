# Roadflow Api

This is the backend api for RoadFlow. It uses DRF for api development and MindsDB NLP Models for user reviews classification and sentiment. The API follows REST API requirements. It can be tested from the Swagger documentation or any client.

## Figma Design

Here is a link to the [figma](https://www.figma.com/file/4sWAOaXGdd16N5AlyFVSBl/RoadTrack-Project?node-id=10-39&t=J5xBuuZrD2TIcSLZ-0).

## Github Project

Here is a link to the [Github Project](https://github.com/users/devvspaces/projects/2/views/2?layout=board).

## DB Diagram Design

Here is a db diagram for the project database - [Diagram](https://dbdiagram.io/d/6437cb1c8615191cfa8d9bc1)

![](./Roadflow%20DB.png)

## Prerequisites

- Python 3
- MindsDB Python SDK
- Redis

## Installing

A step by step series of examples that tell you how to get a development environment running.

> First you have to clone the project on your machine

- Setup virtual enviroment

    Debian

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

    Windows

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

- Install dependencies in the project root dir

    ```bash
    pip install -r requirements.txt
    cd src
    mkdir logs
    ```

- Setup the env file

    ```bash
    cp env.example .env
    ```

    For the email config:

    This is not required, for it is used to send OTP for account registration. Email sending is disabled by default in development.

    For MINDSDB config:

    Create a [MindsDB](https://mindsdb.com/) account. If you don't have one, sign up for a free account at [cloud.mindsdb.com](http://cloud.mindsdb.com/).

    Set `MINDSDB_SERVER_USERNAME` to your email, and `MINDSDB_SERVER_PASSWORD` to your password.

    Redis config:

    If you don't have redis installed you can configure `settings/base.py` to use Django Memcache. Cache is used for OTP verification.

- Run migrations

    ```bash
    python manage.py migrate
    ```

> The site is configured to run with SQLite but you can configure it to use postgress in production.

## Running the API

To run the API on your machine. Make sure you are in the `src` directory before you run the command below.

```bash
python manage.py runserver
```

API server will run on `http://localhost:8000/`. Visit [Swagger](http://localhost:8000/docs/) to read the Swagger API documentation.

## ⛏️ Built Using

- [Django](https://www.djangoproject.com/) - Web Framework
- [Django Rest Framework](https://www.django-rest-framework.org/) - Building Web APIs
- [Redis](https://redis.io/) - In-memory data store
- [Python](https://www.python.org/) - Programming Language
