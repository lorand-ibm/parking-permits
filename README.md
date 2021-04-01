# Parking Permits

![License](https://img.shields.io/github/license/City-of-Helsinki/parking-permits)

Registration API for Parking Permits.

## Development without Docker

Project uses following software versions:

* Postgres 11
* Postgis 2.5
* Python 3.9

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -RSPd parking_permits # use password `parking_permits`
    sudo -u postgres createdb -O parking_permits -l fi_FI.UTF-8 -E utf8 parking_permits
    
Create extensions in the database
    
    sudo -u postgres psql parking_permits -c "CREATE EXTENSION postgis;"

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER parking_permits CREATEDB;"

### Install Geospatial libraries

For Debian/Ubuntu:

    apt-get install binutils libproj-dev gdal-bin

For more information, see
https://docs.djangoproject.com/en/3.1/ref/contrib/gis/install/geolibs/

### Setup Python Virtual Environment

Installation with PyEnv and VirtualEnvWrapper:

```
pyenv install -v 3.9.0
pyenv virtualenv 3.9.0 parking_permits
pyenv local parking_permits
pyenv virtualenvwrapper
```

### Daily running

* Create `.env` file: `touch .env`
* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py runserver 0:8000`

The project is now running at [localhost:8000](http://localhost:8000)

## Keeping Python requirements up to date

1. Install `pip-tools`:
    
    * `pip install --upgrade pip`
    * `pip install pip-tools`

2. Add new packages to `requirements.in` or `requirements-dev.in`

3. Update `.txt` file for the changed requirements file:
 
    * `pip-compile requirements.in`
    * `pip-compile requirements-dev.in`

4. If you want to update dependencies to their newest versions, run:

    * `pip-compile --upgrade requirements.in`

5. To install Python requirements run:

    * `pip-sync requirements.txt`


## Code format

This project uses [`black`](https://github.com/ambv/black) for Python code formatting.
We follow the basic config, without any modifications. Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`


## Version control

### Commits and pull requests
We try to keep a clean git commit history. For that:
* Keep your commits as simple as possible
* Always rebase your PRs, **don't merge** the latest `main` into your branch
* Don't be afraid to `push --force` once you have fixed your commits 
* Avoid using the GitHub merge/rebase buttons


### Releases

This project is following [GitHub flow](https://guides.github.com/pdfs/githubflow-online.pdf).
Release notes can be found from [GitHub tags/releases](https://github.com/City-of-Helsinki/parking-permits/releases).


## Running tests

    pytest

