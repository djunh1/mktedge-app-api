# mktedge-app-api
API for the market edge application

1. To run, docker-compose run -p 3000:3000 --rm app sh -c "python manage.py runserver"

2. To debug, docker-compose run -p 3000:3000 --rm app sh -c "DJANGO_DEBUGGER=True python manage.py runserver --noreload --nothreading"
