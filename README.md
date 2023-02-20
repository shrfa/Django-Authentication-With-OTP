# Django Project Boilerplate
This repository is a boilerplate Django project for quickly getting started. Created by **Code Stars Up** team

<br>

## Table Of Contents
- [Getting Started](#getting-started)
- [Custom Commands](#custom-commands)

    - [startapp](#startapp)
    - [startapi](#startapi)

## Getting Started

1. Before anything, please run below command to add pre-commit hook, for code quality assurance:
    ```bash
    # If `make` is installed
    $ make githook

    # or

    # If `make` is an unrecognized command
    $ git config --local core.hooksPath ./.githooks/
    ```
   Make sure you will have your pipeline on GitLab, referencing `.gitlab-ci.yml` file.<br><br>

2. First you must clone the boilerplate, to do it so use the command below in terminal:
    ```bash
    $ git clone git@github.com:codestarsup/django-starter-template.git
    ```

3. Build the dockerfile (Note: If you don't have docker and docker compose -f docker-compose.local.yml already installed flow the instructions of [Docker official docs](https://docs.docker.com/compose/install/) to install them):

    ```bash
    $ docker compose -f docker-compose.local.yml build
    ```
4. Your image is ready, and you can run your project by typing `$ docker compose -f docker-compose.local.yml up -d` in the terminal

<br>

5. To interact with docker and run you bash scripts like `python manage.py makemigrations` you can write the command like bellow
    ```bash
    $ docker compose -f docker-compose.local.yml run web python manage.py <your_command>
    ```
    Or open a terminal session inside container and run with your django project commands simply
    ```bash
    $ docker compose -f docker-compose.local.yml run web bash

    >> django@ :/code$ python manage.py makemigrations
    ```

## Custom Commands

In this boilerplate we have written some usefully commands to make it easier to work with django in this environment.

### startapp

**usage**:
Create django apps within the boilerplate structure.

**config**:
You can change the variable `APPS_DIR` in `config/settings/apps.py` which points to absolute path of the django apps directory to change the default one.

**example**:
```bash
$ docker compose -f docker-compose.local.yml run web python manage.py startapp core
```
or ignore `APPS_DIR` and give the directory yourself, which is not recommended at all:
```bash
$ docker compose -f docker-compose.local.yml run web python manage.py startapp core --appdir /home/django/core/apps/app
```

### startapi
**usage**:
Create files and directories needed to develop restful apis in the app directory.

**example**:
```bash
$ docker compose -f docker-compose.local.yml run web python manage.py startapi core #To create files needed for rest api development in the core app directory
```
or you can create the files within every other directory your app lives in:
```bash
$ docker compose -f docker-compose.local.yml run web python manage.py startapi core --appdir /code/foo/
```

### renameproject

**usage**:
Rename the project in all necessary files.

**example**:
```bash
$ docker compose -f docker-compose.local.yml run web python manage.py renameproject config codestars # "config" is the current name of project and "codestars" is the new name
```
