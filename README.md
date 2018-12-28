# freemarket
Repository for freemarket website's source code

## Getting Started


### Set up project static files for pythonganywhere server
Run the command below at project root directory in case static files are not properly loaded.

    pythonX.Y manage.py collectstatic


#### Commands for testing offline
    pythonX.Y manage.py makemigrations
    pythonX.Y manage.py migrate
    pythonX.Y manage.py createsuperuser
    pythonX.Y manage.py runserver