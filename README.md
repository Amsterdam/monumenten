# Monumenten

API and import  module.

## Development

* Python 3.6 (required)
* Virtualenv (recommended)
* Docker-Compose (recommended)


### Local dockers
    # start the local docker containers
    docker-compose up -d --build

    # check out status using
    http://127.0.0.1:8107/status/health
    http://127.0.0.1:8107/status/data

### Local dockers and local server
    # start the local docker containers
    docker-compose up -d --build

    # create virtual environment (use the appropiate python binary)
    virtualenv -p /usr/local/bin/python3 venv
    source venv/bin/activate

    # install the requirements in the virtual env
    pip install -r src/requirements.txt

    # run database migrations
    cd src
    ./manage.py migrate

    # start server
    ./manage.py runserver

    # check out status using
    http://127.0.0.1:8000/status/health
    http://127.0.0.1:8000/status/data

### Import the most recent database of off acceptance:
If your public user name + SSH key combination is properly registered it is
possible to download the most recent successfully imported databases. (This
is only allowed for members of the Datapunt development team, not for external
developers or other users.)

    docker-compose exec database update-db.sh monumenten <username>
    docker-compose exec database update-table.sh bag bag_pand public monumenten <username>
    docker-compose exec database update-table.sh bag bag_nummeraanduiding public monumenten <username>


### Monumenten import

#### Location of the datafiles
Login to Rattic and retrieve the objectstore user and password for `CloudVPS Monumenten` (username is `cultuur`).

Login to https://stack.cloudvps.com/

#### Run the import

    export CULTUUR_OBJECTSTORE_PASSWORD=XXX_from_step_above_XXX
    cd src
    ./manage.py run_import

Check out the database tool pgadmin on host 'localhost' , port 5412.

#### Run the tests

    cd src
    ./manage.py test

### endpoints
- /monumenten/complexen
- /monumenten/monumenten
- /monumenten/situeringen
