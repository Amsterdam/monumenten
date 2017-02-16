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
    pip install -r requirements.txt
    
    # run database migrations
    export DJANGO_SETTINGS_MODULE=monumenten.settings
    ./manage.py migrate
    
    # start server
    ./manage.py runserver
   
   	# check out status using
    http://127.0.0.1:8000/status/health
    http://127.0.0.1:8000/status/data

### Importeer de meest recente database van acceptatie:

docker-compose exec database update-db.sh monumenten

### Monumenten import
#### Location of the datafiles
Login to Rattic and retrieve the tellus objectstore password for CloudVPS Monumenten.

Login to https://stack.cloudvps.com/ with the user 'monumenten'.

#### Run the import

    export DJANGO_SETTINGS_MODULE=monumenten.settings
    export OBJECTSTORE_PASSWORD=XXX_from_step_above_XXX
    ./manage.py run_import
    
Check out the database tool pgadmin on host 'localhost' , port 5409.

